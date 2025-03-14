from app import mongo
import logging

def get_all_racks_ptes():
    return list(mongo.db.racks_ptes.find({}, {"_id": 0}))  # No incluir el campo _id en la respuesta
