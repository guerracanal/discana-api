from utils.constants import Parameters
from utils.helpers import build_format_filter, execute_paginated_query, extract_year, get_albums_by_all_compilations, get_albums_by_all_genres, get_albums_by_all_moods, get_albums_by_any_compilations, get_albums_by_any_genres, get_albums_by_any_moods, pipeline_to_query
from app import mongo
from logging_config import logger
from datetime import datetime, timedelta
import random
import re
import pytz

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

