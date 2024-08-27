from flask_cors import CORS
from flask import Flask
from routes.pdf_to_psd import pdf_to_psd_route
app = Flask(__name__)


CORS(app)

pdf_to_psd_route(app)
if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=8000, use_reloader=True)
    