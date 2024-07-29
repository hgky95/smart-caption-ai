from flask import Flask
from flask_restful import Api
from flask_cors import CORS


from server.resources.AIIntegration import AIIntegration

app = Flask(__name__)
# Allow CORS for all domains at this time
CORS(app)
api = Api(app)

api.add_resource(AIIntegration, '/ai/convert')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
