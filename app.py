# app.py
from flask import Flask
from flask_pymongo import PyMongo
from config import Config
from flask_cors import CORS
import logging
from werkzeug.middleware.proxy_fix import ProxyFix

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
from albums_pendientes.routes import albums_ptes_blueprint
from racks.routes import racks_blueprint
from racks_pendientes.routes import racks_ptes_blueprint
from racks_types.routes import racks_types_blueprint

app.register_blueprint(albums_blueprint, url_prefix='/api/albums')
app.register_blueprint(albums_ptes_blueprint, url_prefix='/api/albums_ptes')
app.register_blueprint(racks_blueprint, url_prefix='/api/racks')
app.register_blueprint(racks_ptes_blueprint, url_prefix='/api/racks_ptes')
app.register_blueprint(racks_types_blueprint, url_prefix='/api/racks_types')


# Opcional: Mostrar logs en consola con formato
formatter = logging.Formatter("[%(asctime)s] %(levelname)s in %(module)s: %(message)s")

# Obtener el logger raíz
logger = logging.getLogger()

# Limpiar los handlers previos (evitar duplicados)
if logger.hasHandlers():
    logger.handlers.clear()

# Agregar el nuevo StreamHandler
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)

# Configurar el nivel de log
logger.setLevel(logging.INFO)