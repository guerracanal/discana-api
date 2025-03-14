from utils.helpers import extract_year
from app import mongo
import logging
from datetime import datetime
import random
import re


# Obtener todos los álbumes
def get_all_albums_ptes(rnd=False):
    albums_ptes = mongo.db.albums_ptes.find()
    album_list = []
    for album in albums_ptes:
        album['_id'] = str(album['_id'])
        album_list.append(album)
    if rnd:
        random.shuffle(album_list)
    return album_list

def get_albums_ptes_by_artist(artist, rnd=False):
    cursor = mongo.db.albums_ptes.find({'artist': {'$regex': f'.*{artist}.*', '$options': 'i'}})
    album_list = list(cursor)
    if rnd:
        random.shuffle(album_list)
    return album_list

def get_albums_ptes_by_title(title, rnd=False):
    cursor = mongo.db.albums_ptes.find({'title': {'$regex': f'.*{title}.*', '$options': 'i'}})
    album_list = list(cursor)
    if rnd:
        random.shuffle(album_list)
    return album_list

def get_albums_ptes_by_country(country, rnd=False):
    cursor = mongo.db.albums_ptes.find({'country': {'$regex': f'.*{country}.*', '$options': 'i'}})
    album_list = list(cursor)
    if rnd:
        random.shuffle(album_list)
    return album_list

def get_albums_ptes_by_genre(genre, rnd=False):
    cursor = mongo.db.albums_ptes.find({'genre': {'$regex': genre, '$options': 'i'}})
    album_list = list(cursor)
    if rnd:
        random.shuffle(album_list)
    return album_list

def get_albums_ptes_by_subgenres(subgenres, rnd=False):
    cursor = mongo.db.albums_ptes.find({'subgenres': {'$regex': subgenres, '$options': 'i'}})
    album_list = list(cursor)
    if rnd:
        random.shuffle(album_list)
    return album_list

def get_albums_ptes_by_mood(mood, rnd=False):
    cursor = mongo.db.albums_ptes.find({'mood': {'$regex': mood, '$options': 'i'}})
    album_list = list(cursor)
    if rnd:
        random.shuffle(album_list)
    return album_list

def get_albums_ptes_by_format(format, rnd=False):
    cursor = mongo.db.albums_ptes.find({'format': {'$regex': format, '$options': 'i'}})
    album_list = list(cursor)
    if rnd:
        random.shuffle(album_list)
    return album_list

def get_albums_ptes_by_compilations(compilations, rnd=False):
    cursor = mongo.db.albums_ptes.find({'compilations': {'$regex': compilations, '$options': 'i'}})
    album_list = list(cursor)
    if rnd:
        random.shuffle(album_list)
    return album_list

# Obtener discos por duración
def get_albums_ptes_by_duration(min_duration=None, max_duration=None, rnd=False):
    query = {}
    if min_duration is not None:
        query["duration"] = {"$gte": min_duration}
    if max_duration is not None:
        query["duration"] = query.get("duration", {})
        query["duration"]["$lte"] = max_duration
    cursor = mongo.db.albums_ptes.find(query)
    album_list = list(cursor)
    if rnd:
        random.shuffle(album_list)
    return album_list

# Obtener discos por número de pistas
def get_albums_ptes_by_tracks(min_tracks=None, max_tracks=None, rnd=False):
    query = {}
    if min_tracks is not None:
        query["tracks"] = {"$gte": min_tracks}
    if max_tracks is not None:
        query["tracks"] = query.get("tracks", {})
        query["tracks"]["$lte"] = max_tracks
    cursor = mongo.db.albums_ptes.find(query)
    album_list = list(cursor)
    if rnd:
        random.shuffle(album_list)
    return album_list

# Obtener discos por año de lanzamiento
def get_albums_ptes_by_year(year, rnd=False):
    cursor = mongo.db.albums_ptes.find({"date_release": {"$regex": f".*{year}.*"}})
    album_list = list(cursor)
    if rnd:
        random.shuffle(album_list)
    return album_list

def get_albums_ptes_by_year_range(start_year, end_year, rnd=False):
    albums_ptes = list(mongo.db.albums_ptes.find({}))
    def is_within_range(album):
        date_release = album.get("date_release")
        if not date_release:
            return False
        year = extract_year(date_release)
        return isinstance(year, int) and int(start_year) <= year <= int(end_year)
    filtered = [album for album in albums_ptes if is_within_range(album)]
    if rnd:
        random.shuffle(filtered)
    return filtered

def get_albums_ptes_by_decade(decade, rnd=False):
    start_year = decade
    end_year = decade + 9
    albums_ptes = list(mongo.db.albums_ptes.find({}))
    def is_in_decade(album):
        date_release = album.get("date_release")
        if not date_release:
            return False
        year = extract_year(date_release)
        return isinstance(year, int) and start_year <= year <= end_year
    filtered = [album for album in albums_ptes if is_in_decade(album)]
    if rnd:
        random.shuffle(filtered)
    return filtered

def get_albums_ptes_by_any_genres(genres, rnd=False):
    query = {
        "$or": [
            {"genre": {"$in": genres}},
            {"subgenres": {"$in": genres}}
        ]
    }
    cursor = mongo.db.albums_ptes.find(query)
    album_list = list(cursor)
    if rnd:
        random.shuffle(album_list)
    return album_list

def get_albums_ptes_by_all_genres(genres, rnd=False):
    query = {
        "$and": [
            {
                "$or": [
                    {"genre": {"$regex": f"^{genre}$", "$options": "i"}},
                    {"subgenres": {"$regex": f"^{genre}$", "$options": "i"}}
                ]
            } for genre in genres
        ]
    }
    cursor = mongo.db.albums_ptes.find(query)
    album_list = list(cursor)
    if rnd:
        random.shuffle(album_list)
    return album_list

def get_albums_ptes_by_any_moods(moods, rnd=False):
    query = {
        "$or": [
            {"mood": {"$in": moods}},
        ]
    }
    cursor = mongo.db.albums_ptes.find(query)
    album_list = list(cursor)
    if rnd:
        random.shuffle(album_list)
    return album_list

def get_albums_ptes_by_all_moods(moods, rnd=False):
    query = {
        "$and": [
            {
                "$or": [
                    {"mood": {"$regex": f"^{mood}$", "$options": "i"}},
                ]
            } for mood in moods
        ]
    }
    cursor = mongo.db.albums_ptes.find(query)
    album_list = list(cursor)
    if rnd:
        random.shuffle(album_list)
    return album_list

def get_albums_ptes_by_any_compilations(compilations, rnd=False):
    query = {
        "$or": [
            {"compilations": {"$in": compilations}},
        ]
    }
    cursor = mongo.db.albums_ptes.find(query)
    album_list = list(cursor)
    if rnd:
        random.shuffle(album_list)
    return album_list

def get_albums_ptes_by_all_compilations(compilations, rnd=False):
    query = {
        "$and": [
            {
                "$or": [
                    {"compilations": {"$regex": f"^{compilation}$", "$options": "i"}},
                ]
            } for compilation in compilations
        ]
    }
    cursor = mongo.db.albums_ptes.find(query)
    album_list = list(cursor)
    if rnd:
        random.shuffle(album_list)
    return album_list

def get_albums_ptes_by_filters(decade=None, genre=None, subgenres=None, mood=None, 
                           format=None, compilations=None, min_duration=None, 
                           max_duration=None, min_tracks=None, max_tracks=None, 
                           year=None, start_year=None, end_year=None, rnd=False):
    query = {}
    if decade:
        start_year = decade
        end_year = decade + 9
        query["date_release"] = {"$gte": f"{start_year}", "$lte": f"{end_year}"}
    if genre:
        query["genre"] = {"$regex": genre, "$options": "i"}
    if subgenres:
        query["subgenres"] = {"$regex": subgenres, "$options": "i"}
    if mood:
        query["mood"] = {"$regex": mood, "$options": "i"}
    if format:
        query["format"] = {"$regex": format, "$options": "i"}
    if compilations:
        query["compilations"] = {"$regex": compilations, "$options": "i"}
    if min_duration is not None or max_duration is not None:
        query["duration"] = {}
        if min_duration is not None:
            query["duration"]["$gte"] = min_duration
        if max_duration is not None:
            query["duration"]["$lte"] = max_duration
    if min_tracks is not None or max_tracks is not None:
        query["tracks"] = {}
        if min_tracks is not None:
            query["tracks"]["$gte"] = min_tracks
        if max_tracks is not None:
            query["tracks"]["$lte"] = max_tracks
    if year:
        query["date_release"] = {"$regex": f".*{year}.*"}
    if start_year and end_year:
        query["date_release"] = {"$gte": f"{start_year}", "$lte": f"{end_year}"}
    cursor = mongo.db.albums_ptes.find(query)
    album_list = list(cursor)
    if rnd:
        random.shuffle(album_list)
    return album_list

def get_filtered_albums_ptes(filters, rnd=False):
    query = {}
    if 'decade' in filters:
        start_year = filters['decade']
        end_year = filters['decade'] + 9
        query["date_release"] = {"$gte": str(start_year), "$lte": str(end_year)}
    if 'genre' in filters:
        query["genre"] = {"$regex": f".*{filters['genre']}.*", "$options": "i"}
    if 'mood' in filters:
        query["mood"] = {"$regex": f".*{filters['mood']}.*", "$options": "i"}
    if 'year' in filters:
        query["date_release"] = {"$regex": f".*{filters['year']}.*"}
    if 'min_duration' in filters or 'max_duration' in filters:
        duration_query = {}
        if 'min_duration' in filters:
            duration_query["$gte"] = filters['min_duration']
        if 'max_duration' in filters:
            duration_query["$lte"] = filters['max_duration']
        query["duration"] = duration_query
    if 'compilations' in filters:
        query["compilations"] = {"$regex": f".*{filters['compilations']}.*", "$options": "i"}
    cursor = mongo.db.albums_ptes.find(query)
    album_list = list(cursor)
    if rnd:
        random.shuffle(album_list)
    return album_list



def get_new_releases(days, rnd=False):
    """
    Devuelve los álbumes con date_release en formato dd/mm/yyyy que hayan sido lanzados
    hace como máximo 'days' días desde la fecha actual.
    Se ignoran fechas en el futuro y se ordenan de forma que los más nuevos (menor diferencia) aparezcan primero.
    """
    # Regex para validar el formato dd/mm/yyyy
    pattern = re.compile(r"^\d{2}/\d{2}/\d{4}$")
    # Buscar álbumes que cumplan con el formato en la base de datos
    albums_ptes = list(mongo.db.albums_ptes.find({"date_release": {"$regex": pattern.pattern}}))
    
    today = datetime.today()
    filtered = []
    for album in albums_ptes:
        date_str = album.get("date_release")
        try:
            release_date = datetime.strptime(date_str, "%d/%m/%Y")
        except ValueError:
            continue  # Si no se puede parsear, se ignora el registro.
        # Se ignoran fechas de lanzamiento futuras.
        if release_date > today:
            continue
        diff_days = (today - release_date).days
        if diff_days <= int(days):
            album["diff_days"] = diff_days  # Guardamos la diferencia para ordenar.
            filtered.append(album)
    # Ordenar: los álbumes con menor diferencia (más nuevos) primero.
    filtered.sort(key=lambda x: x["diff_days"])
    if rnd:
        random.shuffle(filtered)
    return filtered


def get_anniversary_albums_ptes(days, rnd=False):
    """
    Devuelve los álbumes cuyo día y mes de date_release se aproximan a la fecha actual.
    Se filtran los registros con date_release en formato dd/mm/yyyy.
    
    - Si days == 0 se requiere que el día y mes coincidan exactamente.
    - Si days > 0 se permite una diferencia de ±days (por ejemplo, si days=1, se aceptan registros un día antes o después).
    
    Se ordenan mostrando primero los que tienen menor diferencia (más cercanos a la fecha actual).
    """
    pattern = re.compile(r"^\d{2}/\d{2}/\d{4}$")
    albums_ptes = list(mongo.db.albums_ptes.find({"date_release": {"$regex": pattern.pattern}}))
    
    today = datetime.today()
    current_year = today.year
    filtered = []
    for album in albums_ptes:
        date_str = album.get("date_release")
        try:
            release_date = datetime.strptime(date_str, "%d/%m/%Y")
        except ValueError:
            continue
        
        # Generamos la "fecha de cumpleaños" trasladando el date_release al año actual.
        try:
            birthday = release_date.replace(year=current_year)
        except ValueError:
            # Por ejemplo, si la fecha es 29/02 y el año actual no es bisiesto.
            continue
        
        # Calculamos la diferencia en días entre el cumpleaños y hoy.
        diff = (birthday - today).days
        
        # Ajuste para diferencias mayores a la mitad del año (para casos de cambio de año)
        if diff < -182:
            diff += 365
        elif diff > 182:
            diff -= 365
        
        if abs(diff) <= int(days):
            album["diff_days"] = abs(diff)  # Se guarda la diferencia absoluta para ordenar.
            filtered.append(album)
    
    # Ordenar los álbumes por la diferencia (menor primero = más cercano a hoy)
    filtered.sort(key=lambda x: x["diff_days"])
    if rnd:
        random.shuffle(filtered)
    return filtered
