import logging
import os

# Configurar el logger general
logger = logging.getLogger("discana")
logger.setLevel(logging.INFO)  # Cambia el nivel según sea necesario

# Eliminar handlers existentes para evitar duplicados
logger.handlers.clear()

# Formateador
formatter = logging.Formatter("[%(asctime)s] %(levelname)s in %(module)s (%(relativePath)s:%(lineno)d - %(funcName)s): %(message)s")

# Custom filter to add relativePath
class RelativePathFilter(logging.Filter):
    def filter(self, record):
        record.relativePath = os.path.relpath(record.pathname,os.path.dirname(__file__))
        return True

logger.addFilter(RelativePathFilter())

# StreamHandler para consola
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# Agregar el nuevo handler
logger.addHandler(console_handler)
