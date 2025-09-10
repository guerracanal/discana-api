import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv('MONGO_URI', 'mongodb+srv://guerracanal:mellonella57@discana.tnsuc.mongodb.net/?retryWrites=true&w=majority&appName=discana')

client = MongoClient(MONGO_URI)
db = client['discana']
albums_collection = db['albums']
descriptors_collection = db['descriptors']

def get_album_by_spotify_id(spotify_id):
    return albums_collection.find_one({'spotify_id': spotify_id})



def get_mood_descriptors(moods):
    """
    moods: lista de moods en inglés
    Devuelve una lista de dicts: [{'en':..., 'es':..., 'color':...}, ...] en el mismo orden que moods
    """
    docs = descriptors_collection.find({"en": {"$in": moods}})
    mood_map = {doc['en']: doc for doc in docs}
    result = []
    for m in moods:
        doc = mood_map.get(m, None)
        if doc:
            result.append({
                "en": doc['en'],
                "es": doc.get('es', doc['en']),
                "color": doc.get('color', "#929292")
            })
        else:
            result.append({
                "en": m,
                "es": m,
                "color": "#929292"
            })
    return result