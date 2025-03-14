from flask_pymongo import PyMongo
from config import Config

mongo = PyMongo()

def init_db(app):
    mongo.init_app(app)
