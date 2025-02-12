import logging
from flask import Flask
from flask_restful import Api
from flask_cors import CORS

from resources.ImageToTextService import ImageToTextService
from resources.FeedbackService import FeedbackService

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()],
    force=True
)

app = Flask(__name__)
app.logger.handlers = logging.getLogger().handlers
app.logger.setLevel(logging.INFO)

CORS(app)
api = Api(app)

api.add_resource(ImageToTextService, '/ai/convert')
api.add_resource(FeedbackService, '/feedback')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
