# Import modules
from flask import Flask, jsonify
from flask_cors import CORS
from flask_restful import Resource, Api
from flask_session import Session

# Init app
app = Flask(__name__)

# Browser cachine
app.config['SESSION_TYPE'] = 'filesystem'

CORS(app)
Session(app)
api = Api(app)
        
class Ping(Resource):
    def get(self):
        return jsonify({'message' : "Pong!"})
    
api.add_resource(Ping, "/ping")

# Driver
if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)
    