from app import mongo
import logging

def get_all_racks():
    return list(mongo.db.racks.find({}, {"_id": 0}))  # No incluir el campo _id en la respuesta
