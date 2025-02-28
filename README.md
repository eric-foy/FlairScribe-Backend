## Required Python Packages
Tested with python version: **Python 3.12.3** and **Python 3.10**
```
pip install flask openai==0.28 pandas python-docx openpyxl requests python-dotenv werkzeug numpy flask-cors
```


## Setup
Create a **.env** file in the root folder and add **OPENAI_API_KEY** variable and set it to a OpenAI access token.


## Applications
Run the Flask app as the backed. The file is **app.py** and contains the routes to the backend endpoints. This command is ran from the root directory.
```
flask run
```


## Routes
### **POST** to http://localhost:5000/speechbox
Take the inputs (transcription and diarization) and generate output (transcription with speaker)

### **GET** to http://localhost:5000/hello
Test the Flask setup

### **POST** to http://localhost:5000/process-transcription
Processes military transcriptions by adding definitions to specialized terms using GPT-4o.