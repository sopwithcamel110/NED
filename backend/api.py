# Import modules
from flask import Flask, jsonify, request, session
from flask_cors import CORS
from pdfgen import create_cheatsheet_pdf
from flask_restful import Resource, Api
from flask_session import Session

# Init app
app = Flask(__name__)

# Browser caching
app.config['SESSION_TYPE'] = 'filesystem'

CORS(app)
Session(app)
api = Api(app)
        
class Ping(Resource):
    def get(self):
        return jsonify({'message' : "Pong!"})
    
class CreatePDF(Resource):
    def post(self):
        content = request.json
        notes = content['notes']
        location = create_cheatsheet_pdf(notes)
        return jsonify({"location": location, "notes" : notes})

    
api.add_resource(Ping, "/ping")
api.add_resource(CreatePDF, "/createpdf")

# Driver
if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)
