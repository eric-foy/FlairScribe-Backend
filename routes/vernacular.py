import openai
import pandas as pd
import os
from flask import request, jsonify
from concurrent.futures import ThreadPoolExecutor
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from docx import Document  # For handling .docx files
from util import delete_files_in_directory

from app import app

# Load API key from .env file
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
my_auth_user = os.getenv("FLAIRSCRIBE_API_USER")
my_auth_password = os.getenv("FLAIRSCRIBE_API_PASSWORD")

# Configure folders
UPLOAD_FOLDER_VERNACULAR = 'uploads/vernacular'

# Create folders if they don't exist
if not os.path.exists(UPLOAD_FOLDER_VERNACULAR):
    os.makedirs(UPLOAD_FOLDER_VERNACULAR)
    
app.config['UPLOAD_FOLDER_VERNACULAR'] = UPLOAD_FOLDER_VERNACULAR

def process_chunk_with_gpt(chunk, vernacular_prompt):
    """Process a text chunk with GPT-4o to add military term definitions."""
    try:
        prompt = f"""
        The following is a military transcription that includes specific terms which need to be expanded with their full definitions.
        The transcription chunk is:
        "{chunk}"

        Here is the list of military terms and their definitions:
        {vernacular_prompt}

        Please append the military terms in the transcription with their definitions in parentheses next to each term. For example, instead of "Devil Dog", use "Devil Dog (A term for U.S. Marines)".
        Respond with only the updated transcription chunk.
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-4o", 
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=16384,
            temperature=0.1
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"Error processing chunk: {e}")
        return chunk  # Return original chunk on error

def split_into_chunks(text, chunk_size=20384):
    """Split text into chunks of appropriate size for GPT processing."""
    words = text.split()
    chunks = []
    current_chunk = []

    for word in words:
        if sum(len(w) for w in current_chunk) + len(current_chunk) + len(word) > chunk_size:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
        current_chunk.append(word)

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks

def load_vernacular_from_excel(file_path):
    """Load military terms and definitions from an Excel file."""
    try:
        df = pd.read_excel(file_path)
        # Assuming first column is terms and second column is definitions
        return dict(zip(df.iloc[:, 0], df.iloc[:, 1]))
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return {}

def load_vernacular_from_files(excel_files):
    """Load military terms and definitions from multiple Excel files."""
    combined_dict = {}
    
    # Process Excel files in parallel
    with ThreadPoolExecutor() as executor:
        results = executor.map(load_vernacular_from_excel, excel_files)
        for vernacular_dict in results:
            combined_dict.update(vernacular_dict)
    
    return combined_dict

def read_docx(file_path):
    """Extract text from a .docx file."""
    try:
        doc = Document(file_path)
        text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
        return text
    except Exception as e:
        print(f"Error reading .docx file: {e}")
        return None

@app.route('/vernacular', methods=['POST'])
def process_transcription():
    if request.authorization.username != my_auth_user or request.authorization.password != my_auth_password:
        return jsonify({"msg": "Bad username or password"}), 401

    """API endpoint to process a transcription with military term definitions."""
    try:
        # Check if files were uploaded
        print("Received request to /vernacular")
        print(f"Request files: {list(request.files.keys())}")

        if 'transcription' not in request.files:
            return jsonify({'error': 'No transcription file provided'}), 400
        
        if 'vernacular' not in request.files:
            return jsonify({'error': 'No vernacular files provided'}), 400
        
        # Get transcription file
        transcription_file = request.files['transcription']
        if transcription_file.filename == '':
            return jsonify({'error': 'Empty transcription filename'}), 400
        
        # Get vernacular files (can be multiple)
        vernacular_files = request.files.getlist('vernacular')
        if not vernacular_files or vernacular_files[0].filename == '':
            return jsonify({'error': 'Empty vernacular filename'}), 400
        
        # Save uploaded transcription file
        transcription_filename = secure_filename(transcription_file.filename)
        transcription_path = os.path.join(app.config['UPLOAD_FOLDER_VERNACULAR'], transcription_filename)
        transcription_file.save(transcription_path)
        
        # Save vernacular files
        excel_paths = []
        for vernacular_file in vernacular_files:
            vernacular_path = os.path.join(app.config['UPLOAD_FOLDER_VERNACULAR'], secure_filename(vernacular_file.filename))
            vernacular_file.save(vernacular_path)
            excel_paths.append(vernacular_path)
        
        # Load the transcription text (support both .txt and .docx)
        transcription = None
        if transcription_path.lower().endswith('.docx'):
            transcription = read_docx(transcription_path)
            if not transcription:
                return jsonify({'error': 'Failed to read .docx file'}), 400
        else:
            try:
                with open(transcription_path, 'r', encoding='utf-8') as file:
                    transcription = file.read()
            except Exception as e:
                return jsonify({'error': f'Failed to read text file: {str(e)}'}), 400
        
        # Load military terms and definitions
        vernacular_dict = load_vernacular_from_files(excel_paths)
        
        # Convert the dictionary to a formatted string for the prompt
        vernacular_prompt = '\n'.join([f"{term}: {definition}" for term, definition in vernacular_dict.items()])
        
        # Split transcription into manageable chunks
        chunks = split_into_chunks(transcription)
        
        # Process each chunk with GPT-4o
        processed_chunks = []
        for i, chunk in enumerate(chunks, 1):
            processed_chunk = process_chunk_with_gpt(chunk, vernacular_prompt)
            processed_chunks.append(processed_chunk)
        
        # Combine processed chunks
        processed_text = " ".join(processed_chunks)
        
        # Clean up uploaded vernacular files
        delete_files_in_directory(UPLOAD_FOLDER_VERNACULAR)

        try:
            for path in excel_paths:
                os.remove(path)
        except Exception as e:
            print(f"Error cleaning up files: {e}")
        
        return jsonify({
            'status': 'success',
            'message': 'Transcription processed successfully',
            'terms_processed': len(vernacular_dict),
            'chunks_processed': len(chunks),
            'processed_text': processed_text
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500