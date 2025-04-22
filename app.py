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

logger.info("Inicializando la aplicación Flask y registrando blueprints")

VERSION = Config.API_VERSION
# Definir prefijo común para todas las rutas
app.config['API_PREFIX'] = '/api/' + VERSION

@app.route(f'/{app.config["API_PREFIX"]}/', methods=['GET'], strict_slashes=False)
#@app.route(f'/{app.config["API_PREFIX"]}/<path:subpath>', methods=['GET'])
def ruta():
    return f"API Version: {VERSION}"

# Registrar Blueprints
from albums.routes import albums_blueprint
from racks.routes import racks_blueprint
from spotify.routes import spotify_blueprint
from lastfm.routes import lastfm_blueprint
from discogs.routes import discogs_blueprint

app.register_blueprint(albums_blueprint, url_prefix=f'{app.config["API_PREFIX"]}/a')
app.register_blueprint(racks_blueprint, url_prefix=f'{app.config["API_PREFIX"]}/r')
app.register_blueprint(spotify_blueprint, url_prefix=f'{app.config["API_PREFIX"]}/spotify')
app.register_blueprint(lastfm_blueprint, url_prefix=f'{app.config["API_PREFIX"]}/lastfm')
app.register_blueprint(discogs_blueprint, url_prefix=f'{app.config["API_PREFIX"]}/discogs')