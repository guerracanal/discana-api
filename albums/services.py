from utils.helpers import build_format_filter, execute_paginated_query, extract_year, get_albums_by_all_compilations, get_albums_by_all_genres, get_albums_by_all_moods, get_albums_by_any_compilations, get_albums_by_any_genres, get_albums_by_any_moods, pipeline_to_query
from app import mongo
import logging
from datetime import datetime
import random
import re

# Función base modificada para todos los servicios
def base_album_service(
    base_query: dict,
    filter: str = "all",
    page: int = 1,
    per_page: int = 10,
    rnd: bool = False,
    min: int = None,
    max: int = None,
    **kwargs  # Aceptar parámetros adicionales
) -> tuple:
    """Base para todos los servicios de álbumes"""
    format_filter = build_format_filter(filter)
    final_query = {**base_query, **format_filter}
    return execute_paginated_query(final_query, page, per_page, rnd, min, max)


# Obtener todos los álbumes
def get_all_albums(
    filter: str = "all",
    all: bool = False,
    page: int = 1,
    per_page: int = 10,
    rnd: bool = False,
    min: int = None,
    max: int = None
) -> tuple:
    query = {}
    return base_album_service(query, filter, page, per_page, rnd, min, max)


# Ejemplo de implementación para get_albums_by_artist
def get_albums_by_artist(
    artist: str,
    all: bool = False,
    filter: str = "all",
    page: int = 1,
    per_page: int = 10,
    rnd: bool = True,
    min: int = None,
    max: int = None
) -> tuple:
    query = {"artist": {"$regex": f".*{artist}.*", "$options": "i"}}
    return base_album_service(query, filter, page, per_page, rnd, min, max)

def get_albums_by_title(
    title: str,
    all: bool = False,
    filter: str = "all",
    page: int = 1,
    per_page: int = 10,
    rnd: bool = False,
    min: int = None,
    max: int = None
) -> tuple:
    query = {"title": {"$regex": f".*{title}.*", "$options": "i"}}
    return base_album_service(query, filter, page, per_page, rnd, min, max)

def get_albums_by_country(
    country: str,
    all: bool = False,
    filter: str = "all",
    page: int = 1,
    per_page: int = 10,
    rnd: bool = False,
    min: int = None,
    max: int = None
) -> tuple:
    query = {"country": {"$regex": f".*{country}.*", "$options": "i"}}
    return base_album_service(query, filter, page, per_page, rnd, min, max)

def get_albums_by_genres(
    genres: str,
    all: bool = False,
    filter: str = "all",
    page: int = 1,
    per_page: int = 10,
    rnd: bool = False,
    min: int = None,
    max: int = None
) -> tuple:
    genres_list = genres.split("/")

    if all:
        query = get_albums_by_all_genres(genres_list)
    else:
        query = get_albums_by_any_genres(genres_list)
    
    return base_album_service(query, filter, page, per_page, rnd, min, max)

def get_albums_by_moods(
    moods: str,
    all: bool = False,
    filter: str = "all",
    page: int = 1,
    per_page: int = 10,
    rnd: bool = False,
    min: int = None,
    max: int = None
) -> tuple:
    moods_list = moods.split("/")

    if all:
        query = get_albums_by_all_moods(moods_list)
    else:
        query = get_albums_by_any_moods(moods_list)
    
    return base_album_service(query, filter, page, per_page, rnd, min, max)


def get_albums_by_compilations(
    compilations: str,
    all: bool = False,
    filter: str = "all",
    page: int = 1,
    per_page: int = 10,
    rnd: bool = False,
    min: int = None,
    max: int = None
) -> tuple:
    compilations_list = compilations.split("/")

    if all:
        query = get_albums_by_all_compilations(compilations_list)
    else:
        query = get_albums_by_any_compilations(compilations_list)
    
    return base_album_service(query, filter, page, per_page, rnd, min, max)

def get_albums_by_format(
    format: str,
    all: bool = False,
    filter: str = "all",
    page: int = 1,
    per_page: int = 10,
    rnd: bool = False,
    min: int = None,
    max: int = None
) -> tuple:
    query = {"format": {"$regex": f".*{format}.*", "$options": "i"}}
    return base_album_service(query, filter, page, per_page, rnd, min, max)

# Obtener discos por año de lanzamiento
def get_albums_by_year(
    year: str,
    all: bool = False,
    filter: str = "all",
    page: int = 1,
    per_page: int = 10,
    rnd: bool = False,
    min: int = None,
    max: int = None
) -> tuple:
    query = {"date_release": {"$regex": f".*{year}.*"}}
    return base_album_service(query, filter, page, per_page, rnd, min, max)



# Error: Algunos date_release están vacíos o tienen formato incorrecto
def get_albums_by_year_range(
    start_year: int,
    end_year: int,
    filter: str = "all",
    page: int = 1,
    per_page: int = 10,
    rnd: bool = False,
    min: int = None,
    max: int = None,
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
    return base_album_service(query, filter, page, per_page, rnd, min, max)

# Aplicar misma lógica para get_albums_by_decade

# En services.py
def get_albums_by_decade(
    decade: int,
    filter: str = "all",
    page: int = 1,
    per_page: int = 10,
    rnd: bool = False,
    min: int = None,
    max: int = None,
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
    return base_album_service(query, filter, page, per_page, rnd, min, max)

def get_new_releases(
    days: int,
    all: bool = False,
    filter: str = "all",
    page: int = 1,
    per_page: int = 10,
    rnd: bool = False,
    **kwargs  # Aceptar parámetros adicionales
) -> tuple:
    """
    Devuelve álbumes lanzados en los últimos 'days' días con paginación y filtros.
    """
    pipeline = [
        # Convertir date_release a string y validar formato
        {
            "$addFields": {
                "date_str": {"$toString": "$date_release"}
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
        
        # Calcular días desde lanzamiento
        {
            "$addFields": {
                "diff_days": {
                    "$dateDiff": {
                        "startDate": "$release_date",
                        "endDate": "$$NOW",
                        "unit": "day"
                    }
                }
            }
        },
        
        # Filtrar por rango y fechas pasadas
        {
            "$match": {
                "$expr": {
                    "$and": [
                        {"$lte": ["$diff_days", days]},
                        {"$lte": ["$release_date", "$$NOW"]}
                    ]
                }
            }
        },
        
        # Ordenar por más recientes primero
        {"$sort": {"diff_days": 1}}
    ]
    
    # Aplicar filtro de formato
    if filter != "all":
        pipeline.append({"$match": build_format_filter(filter)})
    
    # Paginación u orden aleatorio
    if rnd:
        pipeline.append({"$sample": {"size": per_page}})
    else:
        pipeline.extend([
            {"$skip": (page - 1) * per_page},
            {"$limit": per_page}
        ])
    
    # Ejecutar pipeline principal
    albums = list(mongo.db.albums.aggregate(pipeline))
    
    # Obtener total de resultados (sin paginación)
    count_pipeline = pipeline.copy()
    for stage in reversed(count_pipeline):
        if "$skip" in stage or "$limit" in stage or "$sample" in stage:
            count_pipeline.remove(stage)
    
    count_pipeline.append({"$count": "total"})
    total_result = list(mongo.db.albums.aggregate(count_pipeline))
    total = total_result[0]["total"] if total_result else 0
    
    # Limpiar campos temporales y convertir IDs
    for album in albums:
        album.pop("date_str", None)
        album.pop("release_date", None)
        album["_id"] = str(album["_id"])
    
    return albums, total

def get_anniversary_albums(
    days: int,
    all: bool = False,
    filter: str = "all",
    page: int = 1,
    per_page: int = 10,
    rnd: bool = False,
    **kwargs  # Aceptar parámetros adicionales
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
    if filter != "all":
        pipeline.append({"$match": build_format_filter(filter)})
    
    # Paginación
    if not rnd:
        pipeline.extend([
            {"$skip": (page - 1) * per_page},
            {"$limit": per_page}
        ])
    
    # Obtener resultados
    albums = list(mongo.db.albums.aggregate(pipeline))
    
    # Contar total (sin paginación)
    count_pipeline = pipeline.copy()
    for stage in reversed(count_pipeline):
        if "$skip" in stage or "$limit" in stage:
            count_pipeline.remove(stage)
    
    count_pipeline.append({"$count": "total"})
    total = mongo.db.albums.aggregate(count_pipeline).next().get("total", 0)
    
    # Limpiar y convertir IDs
    for album in albums:
        album.pop("date_str", None)
        album.pop("release_date", None)
        album.pop("birthday", None)
        album["_id"] = str(album["_id"])
    
    return albums, total

def get_albums_by_type_service(
    tipo: str,
    page: int = 1,
    per_page: int = 10,
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
                    {"$match": {"name": tipo}},
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
                    {"$match": {"name": tipo}},
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
    total_result = list(mongo.db.albums.aggregate(count_pipeline))
    total = total_result[0]["total"] if total_result else 0
    
    # Obtener resultados
    results = list(mongo.db.albums.aggregate(results_pipeline))
    
    return results, total  # Devolver tupla correcta

