from flask import Flask, request, jsonify
import os
import whisper
import warnings
import time
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from util import misc

from app import app

warnings.filterwarnings(
    "ignore",
    message="You are using `torch.load` with `weights_only=False`"
)

load_dotenv()
my_auth_user = os.getenv("FLAIRSCRIBE_API_USER")
my_auth_password = os.getenv("FLAIRSCRIBE_API_PASSWORD")

# Define the directories for input and output
UPLOAD_FOLDER_TRANSCRIBE = "uploads/transcribe"

# Create folders if they don't exist
if not os.path.exists(UPLOAD_FOLDER_TRANSCRIBE):
    os.makedirs(UPLOAD_FOLDER_TRANSCRIBE)

app.config['UPLOAD_FOLDER_TRANSCRIBE'] = UPLOAD_FOLDER_TRANSCRIBE

# Load the Whisper model (adjust the model type as needed)
model = whisper.load_model("tiny.en")  # 'tiny.en', 'tiny', 'base.en', 'base', 'small.en', 'small', 'medium.en', 'medium', 'large-v1', 'large-v2', 'large-v3', 'large', 'large-v3-turbo', 'turbo'


class ProcessedFile:
    def __init__(self, filename, transcription):
        # Instance attributes
        self.filename = filename
        self.transcription = transcription

    def __json__(self):
        return self.__dict__

def transcribe_audio_file(file_path):
    """Use Whisper to transcribe the audio file at file_path."""
    result = model.transcribe(file_path)
    return result.get("text", "")

@app.route('/transcribe', methods=['POST'])
def process_all_files():
    processed_files = []
    errors = []

    if request.authorization.username != my_auth_user or request.authorization.password != my_auth_password:
        return jsonify({"msg": "Bad username or password"}), 401

    try:
        print("Received request to /process-transcription")
        print(f"Request files: {list(request.files.keys())}")

        if 'audiofiles' not in request.files:
            return jsonify({'error': 'No audiofiles provided'}), 400
        
        audio_files = request.files.getlist('audiofiles')
        if not audio_files or audio_files[0].filename == '':
            return jsonify({'error': 'Empty audiofiles filename'}), 400
        
        audio_paths = []
        for audio_file in audio_files:
            audio_path = os.path.join(app.config['UPLOAD_FOLDER_TRANSCRIBE'], secure_filename(audio_file.filename))
            audio_file.save(audio_path)
            audio_paths.append(audio_path)

    
        for filename in os.listdir(UPLOAD_FOLDER_TRANSCRIBE):
            file_path = os.path.join(UPLOAD_FOLDER_TRANSCRIBE, filename)
            
            if os.path.isfile(file_path) and filename.lower().endswith(('.wav', '.mp3', '.m4a', '.flac', '.ogg')):
                try:
                    print(f"Processing file: {filename} at {time.strftime('%Y-%m-%d %H:%M:%S')}")
                    transcription = transcribe_audio_file(file_path)
                    
                    base_name = os.path.splitext(filename)[0]
                    
                    processed_files.append(ProcessedFile(base_name, transcription).__json__())
                    print(f"Finished processing: {filename}")
                except Exception as e:
                    errors.append(f"Error processing {filename}: {str(e)}")
        
        misc.delete_files_in_directory(UPLOAD_FOLDER_TRANSCRIBE)

        return jsonify({
            "processed_files": processed_files,
            "errors": errors
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500