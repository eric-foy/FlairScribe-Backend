from flask import Flask
from flask_cors import CORS, cross_origin

app = Flask(__name__)
cors = CORS(app, resources={"/speechbox": {"origins": ["http://localhost:5150", "https://localhost:7054"]},
                            "/hello": {"origins": ["http://localhost:5150", "https://localhost:7054"]},
                            "/vernacular": {"origins": ["http://localhost:5150", "https://localhost:7054"]},
                            "/transcribe": {"origins": ["http://localhost:5150", "https://localhost:7054"]}
                            })
app.config['CORS_HEADERS'] = 'Content-Type'

from routes import hello
from routes import speechbox
from routes import vernacular
from routes import transcribe