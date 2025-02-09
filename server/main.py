from flask import Flask
from flask_restful import Api
from flask_cors import CORS

from resources.ImageToTextService import ImageToTextService
from resources.FeedbackService import FeedbackService

app = Flask(__name__)
# Allow CORS for all domains at this time
CORS(app)
api = Api(app)

api.add_resource(ImageToTextService, '/ai/convert')
api.add_resource(FeedbackService, '/feedback')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
