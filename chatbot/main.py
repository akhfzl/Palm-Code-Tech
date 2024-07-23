from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from .api.main import ChatBotResponse

app = Flask(__name__)
CORS(app) 

api = Api(app)

api.add_resource(ChatBotResponse, '/chat')