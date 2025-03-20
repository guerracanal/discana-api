from app import mongo
from logging_config import logger

def get_all_racks(collection_name: str):
    logger.info(f"Obteniendo todos los racks de la colección {collection_name}")
    if collection_name == "spotify":
        documents = mongo.db[collection_name].find({"endpoint": "me"}, {"_id": 0, "title": 1})
        result = []
        for doc in documents:
            if "title" in doc:
                concat = "en Spotify"
                result.append(f"{doc['title']} {concat}")
        return result
    return list(mongo.db[collection_name].find({}, {"_id": 0}))
