http://127.0.0.1:5000/transcribe

## This information is out of date!

# Whisper Transcription Flask API

This repository provides two Flask-based options for performing speech-to-text transcription using the OpenAI Whisper model. Both options expose a simple `/transcribe` endpoint that scans an `uploads` folder for audio files, transcribes them, and saves the resulting text as DOCX files in an `outputs` folder.

There are **two implementations** available:

1. **Local Whisper Model Option (`whisper-step2.py`)**  
   Uses a locally downloaded Whisper model (e.g. `"tiny.en"`) from the official source. This option does not require external cloud storage integration.

2. **Microsoft Graph & SharePoint Integration Option (`whisper-step2-ms.py`)**  
   Authenticates with Microsoft Graph (using Azure AD credentials specified in a `config.json` file) and connects to a designated SharePoint folder where Whisper models are stored.  
   - If the model exists on SharePoint, it is downloaded into a temporary cache (without leaving a persistent local copy) and used to load the model.
   - If the model does not exist on SharePoint, it is downloaded from the official source, uploaded to SharePoint, and then used for transcription.

Both implementations then use the loaded model to transcribe any audio files placed in the `uploads` folder and output the transcriptions as DOCX files in the `outputs` folder.

---

## Prerequisites

- **Python 3.10+**
- Required packages (install via `pip install -r requirements.txt`):
  - Flask
  - whisper (OpenAI Whisper package)
  - python-docx
  - requests
  - torch
  - msal (only needed for `whisper-step2-ms.py`)
- **Option 2** requires a valid `config.json` file with your Microsoft Graph (Azure AD) authentication credentials. An example configuration:

  ```json
  {
      "ms_auth": {
          "tenant_id": "YOUR_TENANT_ID",
          "client_id": "YOUR_CLIENT_ID",
          "client_secret": "YOUR_CLIENT_SECRET",
          "scope": "https://graph.microsoft.com/.default"
      }
  }


- A SharePoint site (e.g., `flairsoft.sharepoint.com/sites/ProductManagement`) with a folder (e.g., `/General/Projects/14.speech-to-text(whisper)/whisper-models`) where the Whisper model file (e.g., `tiny.en.pt`) is stored or can be uploaded. This SharePoint folder is used by **Option 2** to manage the Whisper model file remotely. If the model is not found on SharePoint, the application will download it from the official source and then upload it to this folder.

## Option 1: Local Whisper Model (`whisper-step2.py`)

### Overview

- **Purpose:** Uses a locally downloaded Whisper model.
- **Model:** Loads the model using:
  ```python
  model = whisper.load_model("tiny.en")


You can change the model type by editing the code.

### Usage:

1. **Place your audio files** (supported formats: WAV, MP3, M4A, FLAC, OGG) into the `uploads` folder.
2. **Run the script:**
   ```bash
   python whisper-step2.py

3. **Enter the command in another command window:**
    ```bash
    curl -X POST http://localhost:5000/transcribe -F "audiofiles=@combined_smaller_001.mp3"

4. **Check the outputs folder for the resulting DOCX files.**

## Option 2: Microsoft Graph & SharePoint Integration (`whisper-step2-ms.py`)

### Overview

- **Purpose:** Downloads (or "installs") the Whisper model from a SharePoint folder using the Microsoft Graph API.
- **Model Handling:**  
  - **If found on SharePoint:** The model file (e.g., `tiny.en.pt`) is downloaded into a temporary cache (used solely for loading) without keeping a persistent local copy.
  - **If not found on SharePoint:** The model is downloaded from the official source using `whisper.load_model()`, then uploaded to SharePoint for future use.
- **Authentication:** Uses credentials from `config.json` to obtain an access token and connect to SharePoint.

---

### Usage

1. **Configure your `config.json`** with valid Microsoft Graph credentials.
2. **Confirm that your SharePoint site and folder** (where models are stored) are correctly set in the code.
3. **Place your audio files** in the `uploads` folder.
4. **Run the script:**
   ```bash
   python whisper-step2-ms.py



Open your browser and navigate to:
    ```bash
    http://127.0.0.1:5000/transcribe


This will trigger the Flask API to process all audio files in the `uploads` folder and generate corresponding DOCX transcriptions in the `outputs` folder.

---

## Additional Notes

- **Warnings:**  
  Both scripts suppress a specific PyTorch warning regarding `torch.load` with `weights_only=False`.
- **Debug Mode:**  
  The Flask app runs in debug mode by default. For production use, consider deploying with a production-ready WSGI server.
- **Logging:**  
  Each processed file prints start and finish timestamps to the console for easier tracking.
- **Endpoint:**  
  After running the script, access the transcription endpoint at:
    ```bash
    http://127.0.0.1:5000/transcribe



---

## Troubleshooting

- **Whisper Model Not Found on SharePoint (Option 2)**  
If the model is missing from SharePoint, the script will automatically download it from the official source and upload it to SharePoint for future use.

- **Error: No audio file found**  
Ensure that you have placed audio files in the `uploads` folder before running the script.

- **Authentication Issues with SharePoint**  
- Check that `config.json` contains valid Azure AD credentials.
- Verify that your SharePoint site and folder paths are correct.
- Ensure that your Azure AD app has permissions to access SharePoint.


