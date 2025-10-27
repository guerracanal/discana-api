"""
Clean, consolidated albums service module.

- Eliminadas definiciones repetidas/duplicadas.
- Helpers agrupados: DB helpers, external fetchers (Spotify, Discogs, LastFM, MusicBrainz).
- get_album_details: paralelo, configurable (sources, sources_timeout), merge con prioridad.
- Conserva firmas públicas usadas por routes.py.
"""
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta
from urllib.parse import unquote
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import pytz
import requests
from bson import ObjectId

from utils.constants import Parameters
from utils.helpers import build_format_filter, create_case_insensitive_regex, execute_paginated_query
from db import mongo
from logging_config import logger

# external service helpers (assumed present)
from lastfm.services import get_album_info_lastfm, make_lastfm_request
from spotify.services import make_spotify_request, format_album as format_album_spotify
from discogs.services import make_discogs_request, format_release as format_album_discogs

# -----------------------
# Basic query utilities
# -----------------------
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
) -> Tuple[List[dict], int]:
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
    query = {"artist": create_case_insensitive_regex(artist)}
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
    query = {"title": create_case_insensitive_regex(title)}
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
    query = {"country": create_case_insensitive_regex(country)}
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
    query = {"format": create_case_insensitive_regex(format)}
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

def get_albums_by_duration(
    duration_min: int = None,
    duration_max: int = None,
    filter: str = Parameters.ALL,
    page: int = 1,
    per_page: int = 10,
    rnd: bool = False,
    min: int = None,
    max: int = None,
    collection_name: str = Parameters.ALBUMS,
    **kwargs
) -> tuple:
    query = {}
    if duration_min is not None and duration_max is not None:
        query["duration"] = {"$gte": duration_min, "$lte": duration_max}
    elif duration_min is not None:
        query["duration"] = {"$gte": duration_min}
    elif duration_max is not None:
        query["duration"] = {"$lte": duration_max}
    return base_album_service(query, filter, page, per_page, rnd, min, max, collection_name)

def get_albums_by_duration_min(
    duration_min: int,
    filter: str = Parameters.ALL,
    page: int = 1,
    per_page: int = 10,
    rnd: bool = False,
    min: int = None,
    max: int = None,
    collection_name: str = Parameters.ALBUMS,
    **kwargs
) -> tuple:
    query = {"duration": {"$gte": duration_min}}
    return base_album_service(query, filter, page, per_page, rnd, min, max, collection_name)

def get_albums_by_duration_max(
    duration_max: int,
    filter: str = Parameters.ALL,
    page: int = 1,
    per_page: int = 10,
    rnd: bool = False,
    min: int = None,
    max: int = None,
    collection_name: str = Parameters.ALBUMS,
    **kwargs
) -> tuple:
    query = {"duration": {"$lte": duration_max}}
    return base_album_service(query, filter, page, per_page, rnd, min, max, collection_name)

def get_albums_by_label(
    label: str,
    filter: str = Parameters.ALL,
    page: int = 1,
    per_page: int = 10,
    rnd: bool = False,
    min: int = None,
    max: int = None,
    collection_name: str = Parameters.ALBUMS,
    **kwargs
) -> tuple:
    query = {"label": create_case_insensitive_regex(label)}
    return base_album_service(query, filter, page, per_page, rnd, min, max, collection_name)

def get_albums_by_tracks(
    tracks: int,
    filter: str = Parameters.ALL,
    page: int = 1,
    per_page: int = 10,
    rnd: bool = False,
    min: int = None,
    max: int = None,
    collection_name: str = Parameters.ALBUMS,
    **kwargs
) -> tuple:
    query = {"tracks": tracks}
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

# -----------------------
# DB helpers
# -----------------------
def _get_album_from_mongo(collection_name: str, title: str, artist: str) -> Dict[str, Any]:
    album = mongo.db[collection_name].find_one({
        "title": create_case_insensitive_regex(title),
        "artist": create_case_insensitive_regex(artist)
    })
    if album:
        album["_id"] = str(album["_id"])
    return album or {}

def _get_album_by_db_id(db_id: str, collection_name: str) -> Dict[str, Any]:
    try:
        album = mongo.db[collection_name].find_one({"_id": ObjectId(db_id)})
        if album:
            album["_id"] = str(album["_id"])
            return album
    except Exception as e:
        logger.warning("DB lookup by id failed: %s", e)
    return {}

def _get_album_db_by_spotify_id(spotify_id: str, collection_name: str = Parameters.ALBUMS) -> Dict[str, Any]:
    try:
        album = mongo.db[collection_name].find_one({"spotify_id": spotify_id})
        if album:
            album["_id"] = str(album["_id"])
            return album
    except Exception as e:
        logger.warning("DB lookup by spotify_id failed: %s", e)
    return {}

# -----------------------
# External fetchers
# Single-purpose, return {} on failure
# -----------------------
def _spotify_by_id(spotify_id: str, spotify_user_id: Optional[str] = None) -> Dict[str, Any]:
    try:
        data = make_spotify_request(endpoint=f"albums/{spotify_id}", no_user_neccessary=True)
        return format_album_spotify(data) or {}
    except Exception as e:
        logger.debug("spotify_by_id error: %s", e)
        return {}

def _spotify_by_title(title: str, artist: str, spotify_user_id: Optional[str] = None) -> Dict[str, Any]:
    try:
        params = {"endpoint": "search", "q": f"album:{title} artist:{artist}", "type": "album", "limit": 1, "no_user_neccessary": not spotify_user_id}
        if spotify_user_id:
            params["user_id"] = spotify_user_id
        data = make_spotify_request(**params)
        item = data.get("albums", {}).get("items", [])
        if item:
            return format_album_spotify(item[0])
    except Exception as e:
        logger.debug("spotify_by_title error: %s", e)
    return {}

def _discogs_by_id(discogs_id: str) -> Dict[str, Any]:
    try:
        data = make_discogs_request(endpoint=f"releases/{discogs_id}")
        return format_album_discogs(data) or {}
    except Exception as e:
        logger.debug("discogs_by_id error: %s", e)
        return {}

def _discogs_by_title(title: str, artist: str, discogs_user_id: Optional[str] = None) -> Dict[str, Any]:
    try:
        params = {"endpoint": "database/search", "q": title, "artist": artist, "type": "release", "per_page": 1}
        if discogs_user_id:
            params["user_id"] = discogs_user_id
        data = make_discogs_request(**params)
        results = data.get("results", [])
        if results:
            return format_album_discogs(results[0]) or {}
    except Exception as e:
        logger.debug("discogs_by_title error: %s", e)
    return {}

def _lastfm_by_mbid(mbid: str, artist: Optional[str] = None, title: Optional[str] = None, user: Optional[str] = None) -> Dict[str, Any]:
    try:
        params = {}
        if mbid:
            params["mbid"] = mbid
        else:
            params["artist"] = artist
            params["album"] = title
        if user:
            params["username"] = user
        return get_album_info_lastfm(**params) or {}
    except Exception as e:
        logger.debug("lastfm_by_mbid error: %s", e)
        return {}

def _lastfm_by_title(title: str, artist: str, user: Optional[str] = None) -> Dict[str, Any]:
    return _lastfm_by_mbid(None, artist=artist, title=title, user=user)

def _musicbrainz_by_mbid(mbid: str) -> Dict[str, Any]:
    # Reuse existing 'get_album_by_mbid' behavior if that uses MusicBrainz; here return lightweight placeholder
    try:
        return get_album_by_mbid(mbid) or {}
    except Exception:
        return {}

def _musicbrainz_by_title(title: str, artist: str) -> Dict[str, Any]:
    try:
        # perform direct MusicBrainz search (same approach used previously)
        headers = {"User-Agent": "Discana/1.0 (contact@your-email.com)"}
        search_url = "https://musicbrainz.org/ws/2/release/"
        params = {"query": f"artist:{artist} AND release:{title}", "fmt": "json"}
        r = requests.get(search_url, params=params, headers=headers, timeout=10)
        r.raise_for_status()
        data = r.json()
        return data or {}
    except Exception as e:
        logger.debug("musicbrainz_by_title error: %s", e)
        return {}

# -----------------------
# Public wrappers (used by routes)
# -----------------------
def get_album_by_spotify_id(spotify_id: str, collection_name: str = Parameters.ALBUMS, spotify_user_id: str = None, discogs_user_id: str = None, lastfm_user_id: str = None, **kwargs) -> Dict[str, Any]:
    try:
        data = _spotify_by_id(spotify_id, spotify_user_id)
        if not data:
            return {}
        # Optionally expand via composed title/artist flow to enrich with other sources
        title = data.get("title") or data.get("name") or data.get("name")
        artist = data.get("artist") or data.get("artists") or ""
        if isinstance(artist, list):
            artist = ", ".join([a.get("name", "") for a in artist])
        return get_album_by_title_and_artist(title=title, artist=artist, collection_name=collection_name, spotify_user_id=spotify_user_id, discogs_user_id=discogs_user_id, lastfm_user_id=lastfm_user_id)
    except Exception as e:
        logger.warning("get_album_by_spotify_id failed: %s", e)
        return {}

def get_album_by_db_id(db_id: str, collection_name: str = Parameters.ALBUMS, spotify_user_id: str = None, discogs_user_id: str = None, lastfm_user_id: str = None, **kwargs) -> Dict[str, Any]:
    try:
        album = _get_album_by_db_id(db_id, collection_name)
        if not album:
            return {"error": "Album not found in MongoDB"}
        spotify_id = album.get("spotify_id")
        if spotify_id:
            return get_album_by_spotify_id(spotify_id=spotify_id, collection_name=collection_name, spotify_user_id=spotify_user_id, discogs_user_id=discogs_user_id, lastfm_user_id=lastfm_user_id)
        return album
    except Exception as e:
        logger.warning("get_album_by_db_id failed: %s", e)
        return {}

def get_album_by_mbid(mbid: str, collection_name: str = Parameters.ALBUMS, spotify_user_id: str = None, discogs_user_id: str = None, lastfm_user_id: str = None, **kwargs) -> Dict[str, Any]:
    try:
        lf = get_album_info_lastfm(mbid=mbid)
        title = lf.get("name") or lf.get("title") or ""
        artist = lf.get("artist", {}).get("name", "") if isinstance(lf.get("artist"), dict) else lf.get("artist", "")
        return get_album_by_title_and_artist(title=title, artist=artist, collection_name=collection_name, spotify_user_id=spotify_user_id, discogs_user_id=discogs_user_id, lastfm_user_id=lastfm_user_id)
    except Exception as e:
        logger.warning("get_album_by_mbid failed: %s", e)
        return {}

def get_album_by_discogs_id(discogs_id: str, collection_name: str = Parameters.ALBUMS, spotify_user_id: str = None, discogs_user_id: str = None, lastfm_user_id: str = None, **kwargs) -> Dict[str, Any]:
    try:
        res = make_discogs_request(endpoint=f"releases/{discogs_id}")
        title = res.get("title") or res.get("name", "")
        artist = ", ".join(a.get("name") for a in res.get("artists", [])) if isinstance(res.get("artists"), list) else ""
        return get_album_by_title_and_artist(title=title, artist=artist, collection_name=collection_name, spotify_user_id=spotify_user_id, discogs_user_id=discogs_user_id, lastfm_user_id=lastfm_user_id)
    except Exception as e:
        logger.warning("get_album_by_discogs_id failed: %s", e)
        return {}

def get_album_by_id(album_id: str, collection_name: str = Parameters.ALBUMS, **kwargs) -> Dict[str, Any]:
    try:
        album = mongo.db[collection_name].find_one({"_id": ObjectId(album_id)})
        if album:
            album["_id"] = str(album["_id"])
        return album or {}
    except Exception as e:
        logger.warning("get_album_by_id failed: %s", e)
        return {}

# -----------------------
# Composed title+artist search (synchronous)
# -----------------------
def get_album_by_title_and_artist(
    title: str,
    artist: str,
    collection_name: str = Parameters.ALBUMS,
    album: Dict[str, Any] = None,
    spotify_user_id: Optional[str] = None,
    discogs_user_id: Optional[str] = None,
    lastfm_user_id: Optional[str] = None,
    invoke_db: bool = True,
    invoke_spotify: bool = True,
    invoke_lastfm: bool = True,
    invoke_discogs: bool = True,
    invoke_musicbrainz: bool = True,
    **kwargs
) -> Dict[str, Any]:
    title = unquote(title)
    artist = unquote(artist)
    album = album or {}
    if invoke_db and not album:
        album = _get_album_from_mongo(collection_name, title, artist)
    if invoke_lastfm and "lastfm" not in album:
        album["lastfm"] = _lastfm_by_title(title, artist, lastfm_user_id)
    if invoke_spotify and "spotify" not in album:
        album["spotify"] = _spotify_by_title(title, artist, spotify_user_id)
    if invoke_discogs and "discogs" not in album:
        album["discogs"] = _discogs_by_title(title, artist, discogs_user_id)
    if invoke_musicbrainz and "musicbrainz" not in album:
        album["musicbrainz"] = _musicbrainz_by_title(title, artist)
    return album

# -----------------------
# Merge utilities and normalization
# -----------------------
def _normalize_sources(sources: Optional[List[str]]) -> List[str]:
    if not sources:
        return ['db', 'spotify', 'discogs', 'lastfm', 'musicbrainz']
    known = ['db', 'spotify', 'discogs', 'lastfm', 'musicbrainz']
    normalized = []
    for s in sources:
        s = s.lower()
        if s in known and s not in normalized:
            normalized.append(s)
    return normalized

def _merge_results(primary: Dict[str, Any], secondary: Dict[str, Any]) -> Dict[str, Any]:
    if not primary:
        return secondary or {}
    if not secondary:
        return primary or {}
    merged = dict(primary)
    for k, v in secondary.items():
        if k not in merged or merged.get(k) in (None, '', [], {}):
            merged[k] = v
    return merged

# -----------------------
# Main: parallel get_album_details
# -----------------------
def get_album_details(
    collection_name: str,
    db_id: Optional[str] = None,
    spotify_id: Optional[str] = None,
    mbid: Optional[str] = None,
    discogs_id: Optional[str] = None,
    title: Optional[str] = None,
    artist: Optional[str] = None,
    spotify_user_id: Optional[str] = None,
    discogs_user_id: Optional[str] = None,
    lastfm_user_id: Optional[str] = None,
    sources: Optional[List[str]] = None,
    sources_timeout: Optional[int] = None
) -> Dict[str, Any]:
    """
    Parallelized album detail aggregation.
    - sources controls which sources to call (db, spotify, discogs, lastfm, musicbrainz).
    - sources_timeout (seconds): None => wait for all; int => bounded wait.
    - Merge priority: DB/local values preferred, then spotify, discogs, lastfm, musicbrainz.
    """
    try:
        normalized = _normalize_sources(sources)
        logger.info("get_album_details sources=%s timeout=%s", normalized, sources_timeout)

        result: Dict[str, Any] = {}

        # DB shortcuts (fast)
        if 'db' in normalized and db_id:
            result = _get_album_by_db_id(db_id, collection_name) or {}

        if 'db' in normalized and not result:
            if spotify_id:
                result = _get_album_db_by_spotify_id(spotify_id, collection_name) or {}
            if not result and mbid:
                result = get_album_by_mbid(mbid, collection_name=collection_name) or {}
            if not result and discogs_id:
                result = get_album_by_discogs_id(discogs_id, collection_name=collection_name) or {}
            if not result and title and artist:
                result = _get_album_from_mongo(collection_name, title, artist) or {}

        # If caller asked only DB, return early
        if sources is not None and set(normalized) == {'db'}:
            return result or {}

        # Prepare parallel tasks
        tasks = {}
        with ThreadPoolExecutor(max_workers=5) as exe:
            if 'spotify' in normalized:
                if spotify_id:
                    tasks[exe.submit(_spotify_by_id, spotify_id, spotify_user_id)] = 'spotify'
                elif title and artist:
                    tasks[exe.submit(_spotify_by_title, title, artist, spotify_user_id)] = 'spotify'
            if 'discogs' in normalized:
                if discogs_id:
                    tasks[exe.submit(_discogs_by_id, discogs_id)] = 'discogs'
                elif title and artist:
                    tasks[exe.submit(_discogs_by_title, title, artist, discogs_user_id)] = 'discogs'
            if 'lastfm' in normalized:
                if mbid:
                    tasks[exe.submit(_lastfm_by_mbid, mbid, artist, title, lastfm_user_id)] = 'lastfm'
                elif title and artist:
                    tasks[exe.submit(_lastfm_by_title, title, artist, lastfm_user_id)] = 'lastfm'
            if 'musicbrainz' in normalized:
                if mbid:
                    tasks[exe.submit(_musicbrainz_by_mbid, mbid)] = 'musicbrainz'
                elif title and artist:
                    tasks[exe.submit(_musicbrainz_by_title, title, artist)] = 'musicbrainz'

            external_results: Dict[str, Dict[str, Any]] = {}
            start = time.time()
            if tasks:
                if sources_timeout is None:
                    for fut in as_completed(tasks.keys()):
                        src = tasks[fut]
                        try:
                            res = fut.result()
                            if res:
                                external_results[src] = res
                        except Exception as e:
                            logger.debug("external %s failed: %s", src, e)
                else:
                    # bounded wait; as_completed may raise on timeout - handle gracefully
                    try:
                        for fut in as_completed(tasks.keys(), timeout=sources_timeout):
                            src = tasks[fut]
                            try:
                                remaining = max(0, sources_timeout - (time.time() - start))
                                res = fut.result(timeout=remaining)
                                if res:
                                    external_results[src] = res
                            except Exception as e:
                                logger.debug("external %s failed/timeout: %s", src, e)
                    except Exception as e:
                        logger.debug("as_completed timeout or other error: %s", e)

        # Merge results according to priority
        priority = ['spotify', 'discogs', 'lastfm', 'musicbrainz']
        merged = dict(result or {})
        for src in priority:
            if src in external_results:
                merged = _merge_results(merged, external_results[src])

        # Final fallback DB search by title+artist
        if not merged and title and artist:
            final_db = _get_album_from_mongo(collection_name, title, artist)
            if final_db:
                merged = _merge_results(merged, final_db)

        return merged or {}
    except Exception as e:
        logger.error("get_album_details unexpected error: %s", e, exc_info=True)
        return {"error": str(e)}

# -----------------------
# CRUD & small helpers
# -----------------------
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

def add_to_collection_name_service(collection_name, album_id, new_collection_name):
    try:
        result = mongo.db[collection_name].update_one(
            {"_id": ObjectId(album_id)},
            {"$addToSet": {"collection_name": new_collection_name}}
        )
        if result.matched_count == 0:
            return {"error": "Album not found"}, 404
        return {"_id": album_id, "collection_name": new_collection_name}, 200
    except Exception as e:
        logger.error(f"Error adding to collection_name: {e}", exc_info=True)
        return {"error": "Failed to add to collection_name"}, 500

def find_album_collection_service(album_id: str = None, spotify_id: str = None, title: str = None, collections: Optional[List[str]] = None):
    """
    Busca un álbum en una lista de colecciones y devuelve la colección y el documento.
    Parámetros:
      - album_id: id de MongoDB (string)
      - spotify_id: spotify_id del álbum
      - title: título del álbum (busca case-insensitive)
      - collections: lista de nombres de colecciones a buscar (por defecto ['albums','pendientes'])
    Retorna: (response_dict, status_code)
    """
    from bson import ObjectId
    if collections is None:
        collections = ["albums", "pendientes"]
    for collection in collections:
        query = {}
        if album_id:
            try:
                query["_id"] = ObjectId(album_id)
            except Exception:
                # si el album_id no es un ObjectId válido, ignorar este criterio
                pass
        if spotify_id:
            query["spotify_id"] = spotify_id
        if title:
            query["title"] = create_case_insensitive_regex(title)
        if not query:
            continue
        try:
            album = mongo.db[collection].find_one(query)
            if album:
                album["_id"] = str(album.get("_id"))
                return {"collection": collection, "album": album}, 200
        except Exception as e:
            logger.warning("Error searching collection %s: %s", collection, e)
            continue
    return {"error": "Album not found in any collection"}, 404

def get_album_of_the_day(collection_name: str = Parameters.ALBUMS, **kwargs) -> Dict[str, Any]:
    """
    Devuelve un álbum distinto cada día para la colección dada.
    Selecciona el álbum usando el día del año como índice cíclico sobre la lista ordenada por _id.
    """
    try:
        albums = list(mongo.db[collection_name].find({}).sort("_id", 1))
        total = len(albums)
        if total == 0:
            return {"error": "No albums found in collection"}
        day_of_year = datetime.now().timetuple().tm_yday
        idx = (day_of_year - 1) % total
        album = albums[idx]
        album["_id"] = str(album["_id"])
        return album
    except Exception as e:
        logger.error("Error in get_album_of_the_day: %s", e, exc_info=True)
        return {"error": "Failed to fetch album of the day"}

def move_album_service(origin_collection: str, dest_collection: str, album_id: str):
    """
    Mueve un documento de una colección a otra.
    - origin_collection: nombre de la colección origen
    - dest_collection: nombre de la colección destino
    - album_id: id de MongoDB (string)
    Devuelve: (response_dict, status_code)
    """
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
        logger.error(f"Error moving album from {origin_collection} to {dest_collection}: {e}", exc_info=True)
        return {"error": "Failed to move album"}, 500

def _make_regex_list(values: List[str]):
    """Convertir lista de strings a regex case-insensitive para Mongo queries."""
    return [create_case_insensitive_regex(v) for v in values if v is not None and str(v).strip()]

def get_albums_by_any_genres(genres_list: List[str]) -> dict:
    """
    Query que devuelve álbumes que tengan al menos uno de los géneros indicados
    en el campo 'genre' o en 'subgenres' (case-insensitive).
    """
    regs = _make_regex_list(genres_list)
    if not regs:
        return {}
    return {
        "$or": [
            {"genre": {"$in": regs}},
            {"subgenres": {"$in": regs}}
        ]
    }

def get_albums_by_all_genres(genres_list: List[str]) -> dict:
    """
    Query que devuelve álbumes que tengan todos los géneros indicados
    (cada género puede estar en 'genre' o en 'subgenres').
    Implementación: para cada género creamos un $or, y los combinamos con $and.
    """
    regs = [g for g in genres_list if g is not None and str(g).strip()]
    if not regs:
        return {}
    return {
        "$and": [
            {
                "$or": [
                    {"genre": create_case_insensitive_regex(g)},
                    {"subgenres": create_case_insensitive_regex(g)}
                ]
            } for g in regs
        ]
    }

def get_albums_by_any_moods(moods_list: List[str]) -> dict:
    """
    Query que devuelve álbumes que tengan al menos uno de los moods indicados
    en 'mood' o en 'moods' (case-insensitive).
    """
    regs = _make_regex_list(moods_list)
    if not regs:
        return {}
    return {
        "$or": [
            {"mood": {"$in": regs}},
            {"moods": {"$in": regs}}
        ]
    }

def get_albums_by_all_moods(moods_list: List[str]) -> dict:
    """
    Query que devuelve álbumes que tengan todos los moods indicados
    (cada mood puede estar en 'mood' o en 'moods').
    """
    regs = [m for m in moods_list if m is not None and str(m).strip()]
    if not regs:
        return {}
    return {
        "$and": [
            {
                "$or": [
                    {"mood": create_case_insensitive_regex(m)},
                    {"moods": create_case_insensitive_regex(m)}
                ]
            } for m in regs
        ]
    }