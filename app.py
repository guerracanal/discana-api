# app.py
from flask import Flask
from flask_pymongo import PyMongo
from config import Config
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix
from logging_config import logger

# Inicializar Flask
app = Flask(__name__)
app.config.from_object(Config)

# Inicializar MongoDB
mongo = PyMongo(app)

# Habilitar CORS para todas las rutas
CORS(app)

app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Registrar Blueprints
from albums.routes import albums_blueprint
from racks.routes import racks_blueprint
from spotify.routes import spotify_blueprint

logger.info("Inicializando la aplicación Flask y registrando blueprints")

app.register_blueprint(albums_blueprint, url_prefix='/api/v2/a')
app.register_blueprint(racks_blueprint, url_prefix='/api/v2/r')
app.register_blueprint(spotify_blueprint, url_prefix='/api/v2/s')