from app import mongo
import logging

def get_all_racks(collection_name: str):
    logging.info(f"Obteniendo todos los racks de la colección {collection_name}")
    return list(mongo.db[collection_name].find({}, {"_id": 0}))  # No incluir el campo _id en la respuesta
