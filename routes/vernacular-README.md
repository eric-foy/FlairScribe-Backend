# Military Transcription Processor
A Flask-based application that processes military transcriptions by adding definitions to specialized terms using GPT-4o.

## Features
- Processes transcriptions in DOCX format
- Adds definitions to military terms based on provided vernacular data in Excel files
- Uses OpenAI's GPT-4o to intelligently add definitions to terms in context
- Handles large transcriptions by splitting into manageable chunks
- Saves processed output as a DOCX file


### Using the Flask Server with cURL
In a separate terminal, use cURL to send your files for processing:
```
curl -X POST http://localhost:5000/process-transcription \
  -F "transcription=@path/to/your/transcription.docx" \
  -F "vernacular=@path/to/your/military_terms1.xlsx" \
  -F "vernacular=@path/to/your/military_terms2.xlsx"
```

Replace the file paths with the actual paths to your transcription and vernacular files.


### Input Files
1. Transcription file: A DOCX file containing the military transcription text
2. Vernacular files: Excel files (XLSX) with military terms and their definitions
First column: Terms
Second column: Definitions