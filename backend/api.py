# Import modules
import json
from io import BytesIO

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from flask_restful import Api, Resource

from flask_session import Session
from pdfgen import CheatsheetGenerator

# Init app
app = Flask(__name__)

# Browser caching
app.config['SESSION_TYPE'] = 'filesystem'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB

CORS(app)
Session(app)
api = Api(app)


class Ping(Resource):

    def get(self):
        return jsonify({'message': "Pong!"})


class CreatePDF(Resource):

    def post(self):
        topics = []
        meta = {}
        for key, value in request.form.items():
            if key.startswith('data_'):
                topics.append(json.loads(value))
            elif key.startswith('meta_'):
                meta[key[5:]] = json.loads(value)

        # Process files
        for file in request.files.values():
            topics.append({'media': 'image', 'file': BytesIO(file.read())})

        cg = CheatsheetGenerator(topics)
        buf = cg.create_pdf()
        #buf = open('example/dummy.pdf', 'rb')

        return send_file(buf,
                         mimetype='application/pdf',
                         as_attachment=False,
                         download_name="generated.pdf")


api.add_resource(Ping, "/ping")
api.add_resource(CreatePDF, "/createpdf")

# Driver
if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)
