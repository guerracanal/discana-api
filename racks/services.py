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

def create_rack_service(collection_name, data):
    try:
        result = mongo.db[collection_name].insert_one(data)
        return {"_id": str(result.inserted_id)}, 201
    except Exception as e:
        logger.error(f"Error creating rack: {e}", exc_info=True)
        return {"error": "Failed to create rack"}, 500


def update_rack_service(collection_name, rack_id, data):
    try:
        from bson import ObjectId
        result = mongo.db[collection_name].update_one({"_id": ObjectId(rack_id)}, {"$set": data})
        if result.matched_count == 0:
            return {"error": "Rack not found"}, 404
        return {"_id": rack_id}, 200
    except Exception as e:
        logger.error(f"Error updating rack: {e}", exc_info=True)
        return {"error": "Failed to update rack"}, 500


def delete_rack_service(collection_name, rack_id):
    try:
        from bson import ObjectId
        result = mongo.db[collection_name].delete_one({"_id": ObjectId(rack_id)})
        if result.deleted_count == 0:
            return {"error": "Rack not found"}, 404
        return {"_id": rack_id}, 200
    except Exception as e:
        logger.error(f"Error deleting rack: {e}", exc_info=True)
        return {"error": "Failed to delete rack"}, 500
