from utils.constants import Parameters
from utils.helpers import build_format_filter, execute_paginated_query, extract_year, get_albums_by_all_compilations, get_albums_by_all_genres, get_albums_by_all_moods, get_albums_by_any_compilations, get_albums_by_any_genres, get_albums_by_any_moods, pipeline_to_query
from db import mongo
from logging_config import logger
from datetime import datetime, timedelta
import random
import re
import pytz
import requests
from bson import ObjectId  # Importar ObjectId para manejar IDs de MongoDB
from urllib.parse import unquote  # Importar para decodificar URL

from lastfm.services import get_album_info_lastfm, make_lastfm_request
from spotify.services import make_spotify_request, format_album as format_album_spotify
from discogs.services import make_discogs_request, format_release as format_album_discogs

# Función base modificada para todos los servicios
def base_album_service(
    base_query: dict,
    filter: str = Parameters.ALL,
    page: int = 1,
    per_page: int = 10,
    rnd: bool = False,
    min: int = None,
    max: int = None,
    collection_name: str = Parameters.ALBUMS,  
    **kwargs  
) -> tuple:
    """Base para todos los servicios de álbumes"""
    format_filter = build_format_filter(filter)
    final_query = {**base_query, **format_filter}
    return execute_paginated_query(final_query, page, per_page, rnd, min, max, collection_name)


# Obtener todos los álbumes
def get_all_albums(
    filter: str = Parameters.ALL,
    all: bool = False,
    page: int = 1,
    per_page: int = 10,
    rnd: bool = False,
    min: int = None,
    max: int = None,
    collection_name: str = Parameters.ALBUMS,
    **kwargs
) -> tuple:
    query = {}
    return base_album_service(query, filter, page, per_page, rnd, min, max, collection_name)


# Ejemplo de implementación para get_albums_by_artist
def get_albums_by_artist(
    artist: str,
    all: bool = False,
    filter: str = Parameters.ALL,
    page: int = 1,
    per_page: int = 10,
    rnd: bool = True,
    min: int = None,
    max: int = None,
    collection_name: str = Parameters.ALBUMS,
    **kwargs
) -> tuple:
    query = {"artist": {"$regex": f".*{artist}.*", "$options": "i"}}
    return base_album_service(query, filter, page, per_page, rnd, min, max, collection_name)

def get_albums_by_title(
    title: str,
    all: bool = False,
    filter: str = Parameters.ALL,
    page: int = 1,
    per_page: int = 10,
    rnd: bool = False,
    min: int = None,
    max: int = None,
    collection_name: str = Parameters.ALBUMS,
    **kwargs 
) -> tuple:
    query = {"title": {"$regex": f".*{title}.*", "$options": "i"}}
    return base_album_service(query, filter, page, per_page, rnd, min, max, collection_name)

def get_albums_by_country(
    country: str,
    all: bool = False,
    filter: str = Parameters.ALL,
    page: int = 1,
    per_page: int = 10,
    rnd: bool = False,
    min: int = None,
    max: int = None,
    collection_name: str = Parameters.ALBUMS,
    **kwargs
) -> tuple:
    query = {"country": {"$regex": f".*{country}.*", "$options": "i"}}
    return base_album_service(query, filter, page, per_page, rnd, min, max, collection_name)

def get_albums_by_genres(
    genres: str,
    all: bool = False,
    filter: str = Parameters.ALL,
    page: int = 1,
    per_page: int = 10,
    rnd: bool = False,
    min: int = None,
    max: int = None,
    collection_name: str = Parameters.ALBUMS,
    **kwargs
) -> tuple:
    genres_list = genres.split("/")

    if all:
        query = get_albums_by_all_genres(genres_list)
    else:
        query = get_albums_by_any_genres(genres_list)
    
    return base_album_service(query, filter, page, per_page, rnd, min, max, collection_name)

def get_albums_by_moods(
    moods: str,
    all: bool = False,
    filter: str = Parameters.ALL,
    page: int = 1,
    per_page: int = 10,
    rnd: bool = False,
    min: int = None,
    max: int = None,
    collection_name: str = Parameters.ALBUMS,
    **kwargs
) -> tuple:
    moods_list = moods.split("/")

    if all:
        query = get_albums_by_all_moods(moods_list)
    else:
        query = get_albums_by_any_moods(moods_list)
    
    return base_album_service(query, filter, page, per_page, rnd, min, max, collection_name)


def get_albums_by_compilations(
    compilations: str,
    all: bool = False,
    filter: str = Parameters.ALL,
    page: int = 1,
    per_page: int = 10,
    rnd: bool = False,
    min: int = None,
    max: int = None,
    collection_name: str = Parameters.ALBUMS,
    **kwargs
) -> tuple:
    compilations_list = compilations.split("/")

    if all:
        query = get_albums_by_all_compilations(compilations_list)
    else:
        query = get_albums_by_any_compilations(compilations_list)
    
    return base_album_service(query, filter, page, per_page, rnd, min, max, collection_name)

def get_albums_by_format(
    format: str,
    all: bool = False,
    filter: str = Parameters.ALL,
    page: int = 1,
    per_page: int = 10,
    rnd: bool = False,
    min: int = None,
    max: int = None,
    collection_name: str = Parameters.ALBUMS,
    **kwargs
) -> tuple:
    query = {"format": {"$regex": f".*{format}.*", "$options": "i"}}
    return base_album_service(query, filter, page, per_page, rnd, min, max, collection_name)

# Obtener discos por año de lanzamiento
def get_albums_by_year(
    year: str,
    all: bool = False,
    filter: str = Parameters.ALL,
    page: int = 1,
    per_page: int = 10,
    rnd: bool = False,
    min: int = None,
    max: int = None,
    collection_name: str = Parameters.ALBUMS,
    **kwargs
) -> tuple:
    query = {"date_release": {"$regex": f".*{year}.*"}}
    return base_album_service(query, filter, page, per_page, rnd, min, max, collection_name)



# Error: Algunos date_release están vacíos o tienen formato incorrecto
def get_albums_by_year_range(
    start_year: int,
    end_year: int,
    filter: str = Parameters.ALL,
    page: int = 1,
    per_page: int = 10,
    rnd: bool = False,
    min: int = None,
    max: int = None,
    collection_name: str = Parameters.ALBUMS,  
    **kwargs  # Absorbe parámetros adicionales
) -> tuple:
    query = {
        "$and": [
            {"date_release": {"$regex": r"^\d{2}/\d{2}/\d{4}$"}},  # Validar formato
            {"$expr": {
                "$and": [
                    {"$gte": [{"$toInt": {"$substrCP": ["$date_release", 6, 4]}}, start_year]},
                    {"$lte": [{"$toInt": {"$substrCP": ["$date_release", 6, 4]}}, end_year]}
                ]
            }}
        ]
    }
    return base_album_service(query, filter, page, per_page, rnd, min, max, collection_name)

# Aplicar misma lógica para get_albums_by_decade

# En services.py
def get_albums_by_decade(
    decade: int,
    filter: str = Parameters.ALL,
    page: int = 1,
    per_page: int = 10,
    rnd: bool = False,
    min: int = None,
    max: int = None,
    collection_name: str = Parameters.ALBUMS,  
    **kwargs
) -> tuple:
    start_year = decade
    end_year = decade + 9
    query = {
        "$and": [
            {"date_release": {"$regex": r"^\d{2}/\d{2}/\d{4}$"}},  # Validar formato
            {"$expr": {
                "$and": [
                    {"$gte": [{"$toInt": {"$substrCP": ["$date_release", 6, 4]}}, start_year]},
                    {"$lte": [{"$toInt": {"$substrCP": ["$date_release", 6, 4]}}, end_year]}
                ]
            }}
        ]
    }
    return base_album_service(query, filter, page, per_page, rnd, min, max, collection_name)

def get_new_releases(
    days: int,
    filter: str = Parameters.ALL,
    page: int = 1,
    per_page: int = 10,
    rnd: bool = False,
    collection_name: str = Parameters.ALBUMS,  
    **kwargs  
) -> tuple:
    """
    Devuelve álbumes lanzados en los últimos 'days' días con paginación y filtros.
    - Filtra por date_release en formato dd/mm/yyyy.
    - No incluye fechas futuras.
    """
    # 1. Calcular fecha límite (NOW - days)
    utc = pytz.UTC
    cutoff_date = datetime.now(utc) - timedelta(days=int(days))
    
    # 2. Pipeline principal (optimizado)
    pipeline = [
        # Filtro inicial: regex para validar formato dd/mm/yyyy
        {
            "$match": {
                "date_release": {"$regex": r"^\d{2}/\d{2}/\d{4}$"}
            }
        },
        # Convertir a fecha y filtrar nulos (evitar fechas inválidas)
        {
            "$addFields": {
                "release_date": {
                    "$dateFromString": {
                        "dateString": "$date_release",
                        "format": "%d/%m/%Y"
                    }
                }
            }
        },
        {
            "$match": {
                "release_date": {"$ne": None}
            }
        },
        # Filtrar por rango: [cutoff_date, NOW]
        {
            "$match": {
                "release_date": {
                    "$gte": cutoff_date,
                    "$lte": datetime.now(utc)
                }
            }
        },
        # Ordenar por fecha descendente
        {"$sort": {"release_date": -1}}
    ]
    
    # 3. Añadir filtro adicional (formato físico/digital)
    if filter != Parameters.ALL:
        format_filter = build_format_filter(filter)
        pipeline.append({"$match": format_filter})
    
    # 4. Paginación o muestra aleatoria
    #if rnd:
    #    pipeline.append({"$sample": {"size": per_page}})
    #else:
        pipeline.extend([
            {"$skip": (page - 1) * per_page},
            {"$limit": per_page}
        ])
    
    # 5. Ejecutar consulta principal
    albums = list(mongo.db[collection_name].aggregate(pipeline))
    
    # 6. Contar total (pipeline separado para evitar límite BSON)
    count_pipeline = [
        {"$match": {"date_release": {"$regex": r"^\d{2}/\d{2}/\d{4}$"}}},
        {"$addFields": {"release_date": {"$dateFromString": {"dateString": "$date_release", "format": "%d/%m/%Y"}}}},
        {"$match": {"release_date": {"$ne": None}}},
        {"$match": {"release_date": {"$gte": cutoff_date, "$lte": datetime.now(utc)}}}
    ]
    if filter != Parameters.ALL:
        count_pipeline.append({"$match": format_filter})
    count_pipeline.append({"$count": "total"})
    
    total_result = list(mongo.db[collection_name].aggregate(count_pipeline))
    total = total_result[0]["total"] if total_result else 0
    
    # 7. Limpiar campos y formatear IDs
    for album in albums:
        album.pop("release_date", None)
        album["_id"] = str(album["_id"])
    
    return albums, total

def get_anniversary_albums(
    days: int,
    all: bool = False,
    filter: str = Parameters.ALL,
    page: int = 1,
    per_page: int = 10,
    rnd: bool = False,
    collection_name: str = Parameters.ALBUMS,  
    **kwargs  
) -> tuple:
    today = datetime.today()
    current_year = today.year
    
    pipeline = [
        # Convertir date_release a string y validar formato
        {
            "$addFields": {
                "date_str": {
                    "$toString": "$date_release"
                }
            }
        },
        {
            "$match": {
                "$expr": {
                    "$regexMatch": {
                        "input": "$date_str",
                        "regex": r"^\d{2}/\d{2}/\d{4}$"
                    }
                }
            }
        },
        
        # Convertir a fecha
        {
            "$addFields": {
                "release_date": {
                    "$dateFromString": {
                        "dateString": "$date_str",
                        "format": "%d/%m/%Y"
                    }
                }
            }
        },
        
        # Calcular fecha de aniversario
        {
            "$addFields": {
                "birthday": {
                    "$dateAdd": {
                        "startDate": "$release_date",
                        "unit": "year",
                        "amount": {
                            "$subtract": [
                                current_year,
                                {"$year": "$release_date"}
                            ]
                        }
                    }
                }
            }
        },
        
        # Calcular diferencia de días
        {
            "$addFields": {
                "diff_days": {
                    "$dateDiff": {
                        "startDate": "$$NOW",
                        "endDate": "$birthday",
                        "unit": "day"
                    }
                }
            }
        },
        
        # Filtrar por rango de días
        {
            "$match": {
                "$expr": {
                    "$lte": [
                        {"$abs": "$diff_days"},
                        days
                    ]
                }
            }
        },
        
        # Ordenar
        {"$sort": {"diff_days": 1}}
    ]
    
    # Aplicar filtro de formato
    if filter != Parameters.ALL:
        pipeline.append({"$match": build_format_filter(filter)})
    
    # Paginación
    if not rnd:
        pipeline.extend([
            {"$skip": (page - 1) * per_page},
            {"$limit": per_page}
        ])
    
    # Obtener resultados
    albums = list(mongo.db[collection_name].aggregate(pipeline))
    
    # Contar total (sin paginación)
    count_pipeline = pipeline.copy()
    for stage in reversed(count_pipeline):
        if "$skip" in stage or "$limit" in stage:
            count_pipeline.remove(stage)
    
    count_pipeline.append({"$count": "total"})
    total = mongo.db[collection_name].aggregate(count_pipeline).next().get("total", 0)
    
    # Limpiar y convertir IDs
    for album in albums:
        album.pop("date_str", None)
        album.pop("release_date", None)
        album.pop("birthday", None)
        album["_id"] = str(album["_id"])
    
    return albums, total

def get_albums_by_type_service(
    type: str,
    page: int = 1,
    per_page: int = 10,
    collection_name: str = Parameters.ALBUMS,
    **kwargs
) -> tuple:
    """
    Ejecuta la query de agregación para obtener álbumes cuyo campo 'genre' o 'subgenres'
    tengan al menos una coincidencia con los géneros del tipo indicado.
    La consulta se pagina y devuelve resultados en orden aleatorio, priorizando las coincidencias en 'genre'.
    """
    # Pipeline modificado para incluir conteo total
    count_pipeline = [
        {
            "$lookup": {
                "from": "types",
                "let": {"combinedGenres": {"$setUnion": [{"$ifNull": ["$genre", []]}, {"$ifNull": ["$subgenres", []]}]}},
                "pipeline": [
                    {"$match": {"name": type}},
                    {"$project": {"_id": 0, "genres": 1}}
                ],
                "as": "type"
            }
        },
        {
            "$addFields": {
                "genreMatches": {
                    "$size": {
                        "$setIntersection": [
                            {"$arrayElemAt": ["$type.genres", 0]},
                            {"$ifNull": ["$genre", []]}
                        ]
                    }
                },
                "subgenreMatches": {
                    "$map": {
                        "input": {"$ifNull": ["$subgenres", []]},
                        "as": "subgenre",
                        "in": {
                            "$size": {
                                "$setIntersection": [
                                    {"$arrayElemAt": ["$type.genres", 0]},
                                    ["$$subgenre"]
                                ]
                            }
                        }
                    }
                }
            }
        },
        {
            "$match": {
                "$expr": {
                    "$gt": [{"$sum": ["$genreMatches", {"$sum": "$subgenreMatches"}]}, 0]
                }
            }
        },
        {
            "$addFields": {
                "matchScore": {
                    "$sum": ["$genreMatches", {"$sum": "$subgenreMatches"}]
                }
            }
        },
        {"$sort": {"matchScore": -1}},
        {"$addFields": {"random": {"$rand": {}}}},
        {"$sort": {"random": 1}},
        {"$skip": (page - 1) * per_page if page > 0 else 0},
        {"$limit": per_page},
        {"$project": {"type": 0, "random": 0, "matchScore": 0, "genreMatches": 0, "subgenreMatches": 0}},
        {"$count": "total"}
    ]

     # Pipeline para resultados paginados
    results_pipeline = [
               {
            "$lookup": {
                "from": "types",
                "let": {"combinedGenres": {"$setUnion": [{"$ifNull": ["$genre", []]}, {"$ifNull": ["$subgenres", []]}]}},
                "pipeline": [
                    {"$match": {"name": type}},
                    {"$project": {"_id": 0, "genres": 1}}
                ],
                "as": "type"
            }
        },
        {
            "$addFields": {
                "genreMatches": {
                    "$size": {
                        "$setIntersection": [
                            {"$arrayElemAt": ["$type.genres", 0]},
                            {"$ifNull": ["$genre", []]}
                        ]
                    }
                },
                "subgenreMatches": {
                    "$map": {
                        "input": {"$ifNull": ["$subgenres", []]},
                        "as": "subgenre",
                        "in": {
                            "$size": {
                                "$setIntersection": [
                                    {"$arrayElemAt": ["$type.genres", 0]},
                                    ["$$subgenre"]
                                ]
                            }
                        }
                    }
                }
            }
        },
        {
            "$match": {
                "$expr": {
                    "$gt": [{"$sum": ["$genreMatches", {"$sum": "$subgenreMatches"}]}, 0]
                }
            }
        },
        {
            "$addFields": {
                "matchScore": {
                    "$sum": ["$genreMatches", {"$sum": "$subgenreMatches"}]
                }
            }
        },
        {"$sort": {"matchScore": -1}},
        {"$addFields": {"random": {"$rand": {}}}},
        {"$sort": {"random": 1}},
        {"$skip": (page - 1) * per_page if page > 0 else 0},
        {"$limit": per_page},
        {"$project": {"type": 0, "random": 0, "matchScore": 0, "genreMatches": 0, "subgenreMatches": 0}},
        {"$skip": (page - 1) * per_page},
        {"$limit": per_page}
    ]
     # Obtener total
    total_result = list(mongo.db[collection_name].aggregate(count_pipeline))
    total = total_result[0]["total"] if total_result else 0
    
    # Obtener resultados
    results = list(mongo.db[collection_name].aggregate(results_pipeline))
    
    return results, total  # Devolver tupla correcta

def create_album_service(collection_name, data):
    try:
        result = mongo.db[collection_name].insert_one(data)
        return {"_id": str(result.inserted_id)}, 201
    except Exception as e:
        logger.error(f"Error creating album: {e}", exc_info=True)
        return {"error": "Failed to create album"}, 500


def update_album_service(collection_name, album_id, data):
    try:
        result = mongo.db[collection_name].update_one({"_id": ObjectId(album_id)}, {"$set": data})
        if result.matched_count == 0:
            return {"error": "Album not found"}, 404
        return {"_id": album_id}, 200
    except Exception as e:
        logger.error(f"Error updating album: {e}", exc_info=True)
        return {"error": "Failed to update album"}, 500


def delete_album_service(collection_name, album_id):
    try:
        result = mongo.db[collection_name].delete_one({"_id": ObjectId(album_id)})
        if result.deleted_count == 0:
            return {"error": "Album not found"}, 404
        return {"_id": album_id}, 200
    except Exception as e:
        logger.error(f"Error deleting album: {e}", exc_info=True)
        return {"error": "Failed to delete album"}, 500

def get_album_details(
    collection_name: str,
    title: str = None,
    artist: str = None,
    spotify_id: str = None,
    db_id: str = None,
    mbid: str = None,
    discogs_id: str = None,
    spotify_user_id: str = None,
    discogs_user_id: str = None,
    lastfm_user_id: str = None,
    **kwargs
) -> dict:
    """
    Obtiene el detalle de un álbum priorizando las consultas por ID.
    Si no hay ID disponible, consulta por título y artista.
    """
    album = {}

    try:
        # Priorizar consulta por MongoDB ID
        if db_id:
            album = _get_album_by_db_id(db_id, collection_name)
            spotify_id = album.get("spotify_id")
            title = album.get("title")
            artist = album.get("artist")

        # Priorizar consulta por Spotify ID
        if spotify_id and not album.get("spotify"):
            if not db_id:
                # Si no hay ID de MongoDB, buscar en Spotify
                album = _get_album_db_by_spotify_id(spotify_id)
            album["spotify"] = _get_album_by_spotify_id(spotify_id, spotify_user_id)
            title = album["spotify"].get("title")
            artist = album["spotify"].get("artist")


        # Priorizar consulta por MBID (Last.fm)
        if mbid and not album.get("lastfm"):
            album["lastfm"] = _get_album_by_mbid(mbid)
            title = album["lastfm"].get("title")
            artist = album["lastfm"].get("artist")

        # Priorizar consulta por Discogs ID
        if discogs_id and not album.get("discogs"):
            album["discogs"] = _get_album_by_discogs_id(discogs_id)
            title = album["discogs"].get("title")
            artist = album["discogs"].get("artist")

        # Si no hay IDs, consultar por título y artista
        if title and artist:
            album.update(
                get_album_by_title_and_artist(
                    title=title,
                    artist=artist,
                    collection_name=collection_name,
                    spotify_user_id=spotify_user_id,
                    discogs_user_id=discogs_user_id,
                    lastfm_user_id=lastfm_user_id,
                    invoke_db=not album.get("_id"),
                    invoke_spotify=not album.get("spotify"),
                    invoke_lastfm=not album.get("lastfm"),
                    invoke_discogs=not album.get("discogs"),
                    invoke_musicbrainz=not album.get("musicbrainz"),
                    album=album,  # Pasar el álbum existente
                )
            )

        return album or {"error": "Album not found"}
    except Exception as e:
        logger.error(f"Error fetching album details: {e}", exc_info=True)
        return {"error": "Failed to fetch album details"}


def _get_album_by_db_id(db_id: str, collection_name: str) -> dict:
    """Obtiene el álbum desde MongoDB por su ID."""
    try:
        album = mongo.db[collection_name].find_one({"_id": ObjectId(db_id)})
        if album:
            album["_id"] = str(album["_id"])
        return album or {"error": "Album not found in MongoDB"}
    except Exception as e:
        logger.error(f"Error fetching album by MongoDB ID: {e}", exc_info=True)
        return {"error": "Failed to fetch album by MongoDB ID"}


def _get_album_db_by_spotify_id(spotify_id: str, collection_name: str = Parameters.ALBUMS) -> dict:
    """Obtiene el álbum desde MongoDB por su Spotify ID."""
    try:
        album = mongo.db[collection_name].find_one({"spotify_id": spotify_id})
        if album:
            album["_id"] = str(album["_id"])  # Convertir ObjectId a string
        return album or {"error": "Album not found in MongoDB by Spotify ID"}
    except Exception as e:
        logger.error(f"Error fetching album by Spotify ID in MongoDB: {e}", exc_info=True)
        return {"error": "Failed to fetch album by Spotify ID in MongoDB"}


def _get_album_by_spotify_id(spotify_id: str, spotify_user_id: str = None) -> dict:
    """Obtiene el álbum desde Spotify por su ID."""
    try:
        spotify_album = make_spotify_request(endpoint=f"albums/{spotify_id}", no_user_neccessary=True)
        formatted_album = format_album_spotify(spotify_album)

        # Obtener detalles del álbum independientemente del usuario
        album_details = make_spotify_request(endpoint=f"albums/{formatted_album['spotify_id']}", no_user_neccessary=True)
        if album_details:
            tracks = album_details.get("tracks", {}).get("items", [])
            total_duration_ms = sum(track.get("duration_ms", 0) for track in tracks)
            formatted_album["duration"] = round(total_duration_ms / 60000, 2)
            formatted_album["track_details"] = [
                {
                    "disc_number": track.get("disc_number"),
                    "duration_ms": track.get("duration_ms"),
                    "explicit": track.get("explicit"),
                    "href": track.get("href"),
                    "id": track.get("id"),
                    "is_local": track.get("is_local"),
                    "name": track.get("name"),
                    "popularity": track.get("popularity"),
                    "preview_url": track.get("preview_url"),
                    "track_number": track.get("track_number"),
                    "type": track.get("type"),
                    "uri": track.get("uri"),
                }
                for track in tracks
            ]

        # Obtener detalles específicos del usuario
        if spotify_user_id:
            saved_albums = make_spotify_request(endpoint="me/albums/contains", ids=formatted_album["spotify_id"], user_id=spotify_user_id)
            formatted_album["is_saved"] = saved_albums[0] if isinstance(saved_albums, list) else False

            recent_tracks = make_spotify_request(endpoint="me/player/recently-played", user_id=spotify_user_id, limit=50)
            last_played_date = next(
                (item.get("played_at") for item in recent_tracks.get("items", []) if item.get("track", {}).get("album", {}).get("id") == formatted_album["spotify_id"]),
                None
            )
            if last_played_date:
                last_played_datetime = datetime.strptime(last_played_date, "%Y-%m-%dT%H:%M:%S.%fZ")
                formatted_album["last_listened_date"] = last_played_datetime.isoformat()
                formatted_album["recently_listened"] = (datetime.now() - last_played_datetime).days <= 30
            else:
                formatted_album["last_listened_date"] = None
                formatted_album["recently_listened"] = False

        return formatted_album
    except Exception as e:
        logger.error(f"Error fetching album by Spotify ID: {e}", exc_info=True)
        return {"error": "Failed to fetch album by Spotify ID"}


def _get_album_by_mbid(mbid: str) -> dict:
    """Obtiene el álbum desde Last.fm por su MBID."""
    try:
        lastfm_album = get_album_info_lastfm(mbid=mbid)
        return lastfm_album
    except Exception as e:
        logger.error(f"Error fetching album by MBID: {e}", exc_info=True)
        return {"error": "Failed to fetch album by MBID"}


def _get_album_by_discogs_id(discogs_id: str) -> dict:
    """Obtiene el álbum desde Discogs por su ID."""
    try:
        discogs_album = make_discogs_request(endpoint=f"releases/{discogs_id}")
        return format_album_discogs(discogs_album)
    except Exception as e:
        logger.error(f"Error fetching album by Discogs ID: {e}", exc_info=True)
        return {"error": "Failed to fetch album by Discogs ID"}

def get_album_by_title_and_artist(
    title: str,
    artist: str,
    collection_name: str = Parameters.ALBUMS,
    album: dict = None,  # Nuevo parámetro opcional
    spotify_user_id: str = None,
    discogs_user_id: str = None,
    lastfm_user_id: str = None,
    invoke_db: bool = True,
    invoke_spotify: bool = True,
    invoke_lastfm: bool = True,
    invoke_discogs: bool = True,
    invoke_musicbrainz: bool = True,
    **kwargs
) -> dict:
    """Obtiene el detalle de un álbum por su título y artista desde MongoDB, Last.fm, Spotify, Discogs y MusicBrainz."""
    # Decodificar valores de title y artist
    title = unquote(title)
    artist = unquote(artist)

    album = album or {}  # Usar el álbum proporcionado o inicializar como un diccionario vacío

    if invoke_db and not album:
        album = _get_album_from_mongo(collection_name, title, artist)

    if invoke_lastfm and "lastfm" not in album:
        album["lastfm"] = _get_album_from_lastfm(title, artist, lastfm_user_id)

    if invoke_spotify and "spotify" not in album:
        album["spotify"] = _get_album_from_spotify(title, artist, spotify_user_id)

    if invoke_discogs and "discogs" not in album:
        album["discogs"] = _get_album_from_discogs(title, artist, discogs_user_id)

    if invoke_musicbrainz and "musicbrainz" not in album:
        album["musicbrainz"] = _get_album_from_musicbrainz(title, artist)

    return album


def _get_album_from_mongo(collection_name: str, title: str, artist: str) -> dict:
    """Obtiene el álbum desde MongoDB."""
    album = mongo.db[collection_name].find_one({
        "title": {"$regex": f".*{title}.*", "$options": "i"},
        "artist": {"$regex": f".*{artist}.*", "$options": "i"}
    })
    if album:
        album["_id"] = str(album["_id"])
    else:
        album = {"error": "Album not found in MongoDB"}
    return album


def _get_album_from_lastfm(title: str, artist: str, lastfm_user_id: str) -> dict:
    """Obtiene el álbum desde Last.fm."""
    try:
        lastfm_params = {"artist": artist, "album": title, "include_track_info": True}
        if lastfm_user_id:
            lastfm_params["user"] = lastfm_user_id
        lastfm_data = get_album_info_lastfm(**lastfm_params)
        if lastfm_data:
            if lastfm_user_id:
                lastfm_data["user_scrobbles"] = lastfm_data.get("userplaycount", 0)
                recent_tracks = make_lastfm_request("user.getRecentTracks", user=lastfm_user_id, limit=50)
                tracks = recent_tracks.get("recenttracks", {}).get("track", [])
                last_scrobble_date = next(
                    (track.get("date", {}).get("#text") for track in tracks if track.get("album", {}).get("#text") == title),
                    None
                )
                if last_scrobble_date:
                    last_scrobble_datetime = datetime.strptime(last_scrobble_date, "%d %b %Y, %H:%M")
                    lastfm_data["last_listened_date"] = last_scrobble_datetime.isoformat()
                    lastfm_data["recently_listened"] = (datetime.now() - last_scrobble_datetime).days <= 30
                else:
                    lastfm_data["last_listened_date"] = None
                    lastfm_data["recently_listened"] = False
        return lastfm_data
    except Exception as e:
        logger.error(f"Error fetching album from Last.fm: {e}", exc_info=True)
        return {"error": "Failed to fetch data from Last.fm"}


def _get_album_from_spotify(title: str, artist: str, spotify_user_id: str) -> dict:
    """Obtiene el álbum desde Spotify."""
    try:
        spotify_params = {
            "endpoint": "search",
            "q": f"album:{title} artist:{artist}",
            "type": "album",
            "limit": 1,
            "no_user_neccessary": not spotify_user_id
        }
        if spotify_user_id:
            spotify_params["user_id"] = spotify_user_id
        spotify_data = make_spotify_request(**spotify_params)
        if spotify_data.get("albums", {}).get("items"):
            spotify_album = format_album_spotify(spotify_data["albums"]["items"][0])

            # Obtener detalles del álbum independientemente del usuario
            album_details = make_spotify_request(endpoint=f"albums/{spotify_album['spotify_id']}", no_user_neccessary=True)
            if album_details:
                tracks = album_details.get("tracks", {}).get("items", [])
                total_duration_ms = sum(track.get("duration_ms", 0) for track in tracks)
                spotify_album["duration"] = round(total_duration_ms / 60000, 2)
                spotify_album["track_details"] = [
                    {
                        "disc_number": track.get("disc_number"),
                        "duration_ms": track.get("duration_ms"),
                        "explicit": track.get("explicit"),
                        "href": track.get("href"),
                        "id": track.get("id"),
                        "is_local": track.get("is_local"),
                        "name": track.get("name"),
                        "popularity": track.get("popularity"),
                        "preview_url": track.get("preview_url"),
                        "track_number": track.get("track_number"),
                        "type": track.get("type"),
                        "uri": track.get("uri"),
                    }
                    for track in tracks
                ]

            # Obtener detalles específicos del usuario
            if spotify_user_id:
                saved_albums = make_spotify_request(endpoint="me/albums/contains", ids=spotify_album["_id"], user_id=spotify_user_id)
                spotify_album["is_saved"] = saved_albums[0] if isinstance(saved_albums, list) else False

                recent_tracks = make_spotify_request(endpoint="me/player/recently-played", user_id=spotify_user_id, limit=50)
                last_played_date = next(
                    (item.get("played_at") for item in recent_tracks.get("items", []) if item.get("track", {}).get("album", {}).get("id") == spotify_album["_id"]),
                    None
                )
                if last_played_date:
                    last_played_datetime = datetime.strptime(last_played_date, "%Y-%m-%dT%H:%M:%S.%fZ")
                    spotify_album["last_listened_date"] = last_played_datetime.isoformat()
                    spotify_album["recently_listened"] = (datetime.now() - last_played_datetime).days <= 30
                else:
                    spotify_album["last_listened_date"] = None
                    spotify_album["recently_listened"] = False

            return spotify_album
    except Exception as e:
        logger.error(f"Error fetching album from Spotify: {e}", exc_info=True)
        return {"error": "Failed to fetch data from Spotify"}


def _get_album_from_discogs(title: str, artist: str, discogs_user_id: str) -> dict:
    """Obtiene el álbum desde Discogs."""
    try:
        discogs_params = {
            "endpoint": "database/search",
            "q": title,
            "artist": artist,
            "type": "release",
            "per_page": 1
        }
        if discogs_user_id:
            discogs_params["user_id"] = discogs_user_id
        discogs_data = make_discogs_request(**discogs_params)
        if discogs_data.get("results"):
            discogs_album = format_album_discogs(discogs_data["results"][0])
            if discogs_user_id:
                master_id = discogs_album.get("master_id")
                release_id = discogs_album.get("_id")
                user_collection = []
                page = 1
                while True:
                    collection_page = make_discogs_request(
                        endpoint=f"users/{discogs_user_id}/collection/folders/0/releases",
                        user_id=discogs_user_id,
                        page=page,
                        per_page=50
                    )
                    user_collection.extend(collection_page.get("releases", []))
                    if page >= collection_page.get("pagination", {}).get("pages", 1):
                        break
                    page += 1
                album_ids = [item["id"] for item in user_collection]
                discogs_album["in_collection"] = release_id in album_ids or any(
                    item.get("master_id") == master_id for item in user_collection
                )
                formats = [
                    {
                        "id": item["id"],
                        "url": f"https://www.discogs.com/release/{item['id']}",
                        "formats": [
                            {
                                "name": fmt["name"],
                                "qty": fmt.get("qty", 1),
                                "text": fmt.get("text", ""),
                                "descriptions": fmt.get("descriptions", []),
                            }
                            for fmt in item["basic_information"]["formats"]
                        ]
                    }
                    for item in user_collection
                    if item["id"] == release_id or item.get("basic_information", {}).get("master_id") == master_id
                ]
                discogs_album["formats"] = formats
            return discogs_album
    except Exception as e:
        logger.error(f"Error fetching album from Discogs: {e}", exc_info=True)
        return {"error": "Failed to fetch data from Discogs"}

def _get_album_from_musicbrainz(title: str, artist: str) -> dict:
    """Obtiene el álbum desde MusicBrainz."""
    try:
        headers = {
            "User-Agent": "Discana/1.0 (https://github.com/your-repo; contact@your-email.com)"
        }

        # Primera solicitud: Buscar el álbum por artista y título
        search_url = "https://musicbrainz.org/ws/2/release/"
        search_params = {
            "query": f"artist:{artist} AND release:{title}",
            "fmt": "json"
        }
        search_response = requests.get(search_url, params=search_params, headers=headers)
        search_response.raise_for_status()
        search_data = search_response.json()

        # Obtener el primer elemento del campo releases
        releases = search_data.get("releases", [])
        if not releases:
            return {"error": "No releases found in MusicBrainz"}

        first_release = releases[0]
        release_group_id = first_release.get("release-group", {}).get("id")
        if not release_group_id:
            return {"error": "No release-group ID found in MusicBrainz"}

        # Segunda solicitud: Obtener detalles del release-group
        details_url = f"https://musicbrainz.org/ws/2/release-group/{release_group_id}"
        details_params = {
            "inc": "genres+tags+ratings+url-rels",
            "fmt": "json"
        }
        details_response = requests.get(details_url, params=details_params, headers=headers)
        details_response.raise_for_status()
        details_data = details_response.json()

        return details_data
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching album from MusicBrainz: {e}", exc_info=True)
        return {"error": "Failed to fetch data from MusicBrainz"}
    except Exception as e:
        logger.error(f"Unexpected error in MusicBrainz integration: {e}", exc_info=True)
        return {"error": "Unexpected error in MusicBrainz integration"}

def _get_album_from_genius(title: str, artist: str) -> dict:
    """Obtiene el álbum desde Genius."""
    try:
        headers = {
            # "Authorization": f"Bearer {Config.GENIUS_API_TOKEN}"
        }

        # Buscar el álbum por título y artista
        search_url = "https://api.genius.com/search"
        search_params = {
            "q": f"{artist} {title}"
        }
        search_response = requests.get(search_url, params=search_params, headers=headers)
        search_response.raise_for_status()
        search_data = search_response.json()

        # Obtener el primer resultado relevante
        hits = search_data.get("response", {}).get("hits", [])
        if not hits:
            return {"error": "No results found in Genius"}

        first_hit = hits[0].get("result", {})
        album_id = first_hit.get("id")
        if not album_id:
            return {"error": "No album ID found in Genius"}

        # Obtener detalles del álbum
        details_url = f"https://api.genius.com/songs/{album_id}"
        details_response = requests.get(details_url, headers=headers)
        details_response.raise_for_status()
        details_data = details_response.json()

        return details_data.get("response", {}).get("song", {})
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching album from Genius: {e}", exc_info=True)
        return {"error": "Failed to fetch data from Genius"}
    except Exception as e:
        logger.error(f"Unexpected error in Genius integration: {e}", exc_info=True)
        return {"error": "Unexpected error in Genius integration"}

def get_album_by_spotify_id(
    spotify_id: str,
    collection_name: str = Parameters.ALBUMS,
    spotify_user_id: str = None,
    discogs_user_id: str = None,
    lastfm_user_id: str = None,
    **kwargs
) -> dict:
    """Obtiene el detalle de un álbum a partir de su ID de Spotify."""
    try:
        spotify_album = make_spotify_request(endpoint=f"albums/{spotify_id}", no_user_neccessary=True)
        title = spotify_album.get("name")
        artist = ", ".join(artist.get("name") for artist in spotify_album.get("artists", []))
        return get_album_by_title_and_artist(
            title=title,
            artist=artist,
            collection_name=collection_name,
            spotify_user_id=spotify_user_id,
            discogs_user_id=discogs_user_id,
            lastfm_user_id=lastfm_user_id
        )
    except Exception as e:
        logger.error(f"Error fetching album by Spotify ID: {e}", exc_info=True)
        return {"error": "Failed to fetch album by Spotify ID"}


def get_album_by_db_id(
    db_id: str,
    collection_name: str = Parameters.ALBUMS,
    spotify_user_id: str = None,
    discogs_user_id: str = None,
    lastfm_user_id: str = None,
    **kwargs
) -> dict:
    """Obtiene el detalle de un álbum a partir de su ID de MongoDB."""
    try:
        # Convertir db_id a ObjectId
        album = mongo.db[collection_name].find_one({"_id": ObjectId(db_id)})
        if not album:
            return {"error": "Album not found in MongoDB"}
        spotify_id = album.get("spotify_id")
        if not spotify_id:
            return {"error": "Spotify ID not found in MongoDB album"}
        return get_album_by_spotify_id(
            spotify_id=spotify_id,
            collection_name=collection_name,
            spotify_user_id=spotify_user_id,
            discogs_user_id=discogs_user_id,
            lastfm_user_id=lastfm_user_id
        )
    except Exception as e:
        logger.error(f"Error fetching album by MongoDB ID: {e}", exc_info=True)
        return {"error": "Failed to fetch album by MongoDB ID"}


def get_album_by_mbid(
    mbid: str,
    collection_name: str = Parameters.ALBUMS,
    spotify_user_id: str = None,
    discogs_user_id: str = None,
    lastfm_user_id: str = None,
    **kwargs
) -> dict:
    """Obtiene el detalle de un álbum a partir de su MBID de Last.fm."""
    try:
        lastfm_album = get_album_info_lastfm(mbid=mbid)
        title = lastfm_album.get("name")
        artist = lastfm_album.get("artist", {}).get("name", "")
        return get_album_by_title_and_artist(
            title=title,
            artist=artist,
            collection_name=collection_name,
            spotify_user_id=spotify_user_id,
            discogs_user_id=discogs_user_id,
            lastfm_user_id=lastfm_user_id
        )
    except Exception as e:
        logger.error(f"Error fetching album by MBID: {e}", exc_info=True)
        return {"error": "Failed to fetch album by MBID"}


def get_album_by_discogs_id(
    discogs_id: str,
    collection_name: str = Parameters.ALBUMS,
    spotify_user_id: str = None,
    discogs_user_id: str = None,
    lastfm_user_id: str = None,
    **kwargs
) -> dict:
    """Obtiene el detalle de un álbum a partir de su ID de Discogs."""
    try:
        discogs_album = make_discogs_request(endpoint=f"releases/{discogs_id}")
        title = discogs_album.get("title")
        artist = ", ".join(artist.get("name") for artist in discogs_album.get("artists", []))
        return get_album_by_title_and_artist(
            title=title,
            artist=artist,
            collection_name=collection_name,
            spotify_user_id=spotify_user_id,
            discogs_user_id=discogs_user_id,
            lastfm_user_id=lastfm_user_id
        )
    except Exception as e:
        logger.error(f"Error fetching album by Discogs ID: {e}", exc_info=True)
        return {"error": "Failed to fetch album by Discogs ID"}

def get_album_by_id(
    album_id: str,
    collection_name: str = Parameters.ALBUMS,
    **kwargs
) -> dict:
    """Obtiene el detalle de un álbum por su ID."""
    try:
        album = mongo.db[collection_name].find_one({"_id": ObjectId(album_id)})
        if album:
            album["_id"] = str(album["_id"])
        return album or {"error": "Album not found"}
    except Exception as e:
        logger.error(f"Error fetching album by ID: {e}", exc_info=True)
        return {"error": "Failed to fetch album by ID"}

def get_album_of_the_day(
    collection_name: str = Parameters.ALBUMS,
    **kwargs
) -> dict:
    """
    Devuelve un álbum distinto cada día para la colección dada.
    Elige el álbum usando el día del año como índice cíclico.
    """
    try:
        # Obtener todos los álbumes ordenados por _id para consistencia
        albums = list(mongo.db[collection_name].find({}).sort("_id", 1))
        total = len(albums)
        if total == 0:
            return {"error": "No albums found in collection"}
        # Día del año (1-366)
        day_of_year = datetime.now().timetuple().tm_yday
        idx = (day_of_year - 1) % total
        album = albums[idx]
        album["_id"] = str(album["_id"])
        return album
    except Exception as e:
        logger.error(f"Error in get_album_of_the_day: {e}", exc_info=True)
        return {"error": "Failed to fetch album of the day"}

def move_album_service(origin_collection, dest_collection, album_id):
    try:
        album = mongo.db[origin_collection].find_one({"_id": ObjectId(album_id)})
        if not album:
            return {"error": "Album not found in origin collection"}, 404
        album_copy = album.copy()
        album_copy.pop("_id", None)
        insert_result = mongo.db[dest_collection].insert_one(album_copy)
        delete_result = mongo.db[origin_collection].delete_one({"_id": ObjectId(album_id)})
        return {
            "moved": True,
            "new_id": str(insert_result.inserted_id),
            "deleted": bool(delete_result.deleted_count)
        }, 200
    except Exception as e:
        logger.error(f"Error moving album: {e}", exc_info=True)
        return {"error": "Failed to move album"}, 500

def find_album_collection_service(album_id=None, spotify_id=None, title=None, collections=None):
    from bson import ObjectId
    if collections is None:
        collections = ["albums", "albums_ptes"]
    for collection in collections:
        query = {}
        if album_id:
            try:
                query["_id"] = ObjectId(album_id)
            except Exception:
                pass
        if spotify_id:
            query["spotify_id"] = spotify_id
        if title:
            query["title"] = {"$regex": f".*{title}.*", "$options": "i"}
        if not query:
            continue
        album = mongo.db[collection].find_one(query)
        if album:
            album["_id"] = str(album.get("_id"))
            return {
                "collection": collection,
                "album": album
            }, 200
    return {"error": "Album not found in any collection"}, 404

