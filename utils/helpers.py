from datetime import datetime
from db import mongo
from logging_config import logger
from flask import jsonify, request
from functools import wraps
import os
import re


def convert_id(album):
    album['_id'] = str(album['_id'])
    return album

def parse_date(date_str):
    for fmt in ('%d/%m/%Y', '%Y', '%m/%Y'):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None

# Paginación
def paginate_results(query, page, limit):
    start = (page - 1) * limit
    end = start + limit
    return query[start:end]

# Función para manejar la paginación
def paginate_query(query):
    try:
        # Obtener los parámetros de paginación de la consulta
        limit = int(request.args.get('limit', 10))  # Número de elementos por página (por defecto 10)
        page = int(request.args.get('page', 1))  # Número de página (por defecto 1)
        
        # Calcular el número de documentos a omitir (skip)
        skip = (page - 1) * limit
        
        # Aplicar el límite y el skip a la consulta
        return query.skip(skip).limit(limit)
    except ValueError:
        return query  # Si los parámetros no son válidos, devolver la consulta sin modificaciones

def extract_year(date_release):
    """Extrae el año de una fecha en diferentes formatos y lo devuelve como entero."""
    if isinstance(date_release, int):  
        return date_release  # Ya es un número, lo devolvemos directamente.
    
    if isinstance(date_release, str):  
        parts = date_release.split("/")
        try:
            return int(parts[-1])  # Siempre tomamos el último valor y convertimos a int.
        except ValueError:
            return None  # Si la conversión falla, devolvemos None.

    return None  # Si el formato no es válido, devolvemos None.


def build_format_filter(filter: str) -> dict:
    """Construye el query de formato para MongoDB según el filtro"""
    if filter == "disc":
        return {"format": {"$elemMatch": {"$regex": r"^(CD|vinilo)$", "$options": "i"}}}
    if filter == "spotify":
        return {"format": {"$not": {"$elemMatch": {"$regex": r"^(CD|vinilo)$", "$options": "i"}}}}
    return {}

def create_case_insensitive_regex(value, exact_match=False):
    """Creates a case-insensitive regex for MongoDB queries."""
    if exact_match:
        return re.compile(f"^{re.escape(value)}$", re.IGNORECASE)
    else:
        return re.compile(f".*{re.escape(value)}.*", re.IGNORECASE)


def execute_paginated_query(base_query: dict, 
                          page: int, 
                          per_page: int, 
                          rnd: bool = False,
                          min: int = None, 
                          max: int = None,
                          collection_name: str = 'albums') -> tuple:
    """Ejecuta una query paginada con opción de orden aleatorio y filtro de duración"""
    try:
        # 1. Construir query de duración si es necesario
        duration_query = {}
        if min is not None:
            duration_query["$gte"] = min
        if max is not None:
            duration_query["$lte"] = max
        
        # Combinar con la query base
        if duration_query:
            final_query = {**base_query, "duration": duration_query}
        else:
            final_query = base_query.copy()

        # 2. Obtener total de documentos (sin paginación)
        total = mongo.db[collection_name].count_documents(final_query)
        
        # 3. Construir pipeline
        pipeline = [{"$match": final_query}]
        
        # 4. Orden aleatorio o por defecto
        if rnd:
            pipeline.extend([
                {"$addFields": {"_sort_field": {"$rand": {}}}},
                {"$sort": {"_sort_field": 1}},
                {"$project": {"_sort_field": 0}}
            ])
        else:
            pipeline.append({"$sort": {"_id": 1}})
        
        # 5. Paginación (siempre al final)
        pipeline.extend([
            {"$skip": (page - 1) * per_page},
            {"$limit": per_page}
        ])
        
        # 6. Ejecutar pipeline
        albums = list(mongo.db[collection_name].aggregate(pipeline))
        
        # 7. Convertir ObjectIds
        for album in albums:
            album["_id"] = str(album["_id"])
        
        return albums, total
        
    except Exception as e:
        logger.error(f"Error en execute_paginated_query: {str(e)}")
        raise
    
def log_route_info(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        route = request.path
        method = request.method
        params = request.args.to_dict()
        logger.info(f"Entering endpoint: {route} ({method}), Params: {params}")
        result = func(*args, **kwargs)
        logger.info(f"Exiting endpoint: {route} ({method})")
        return result
    return wrapper

def handle_response(service_func):
    @wraps(service_func)
    def wrapper(*args, **kwargs):
        try:
            # Parámetros comunes
            page = int(request.args.get('page', 1))
            limit = int(request.args.get('limit', 10))
            filter = request.args.get('filter', 'all')
            rnd = request.args.get('random', 'false').lower() == 'true'
            all = request.args.get('all', 'false').lower() == 'true'
            min_value = request.args.get('min', None)  # Esto te devuelve None si no encuentra el parámetro
            max_value = request.args.get('max', None)  # Lo mismo para 'max'
            user_id = request.args.get('user_id', None) # Parámetro opcional para el ID de usuario de Spotify
            period = request.args.get('period', None)
            detail = request.args.get('detail', None)


            # Aquí controlas que solo intentes convertir a entero si el valor no es None
            min = int(min_value) if min_value is not None else None
            max = int(max_value) if max_value is not None else None

            # Llamar al servicio
            albums, total = service_func(*args, **kwargs, 
                                       page=page, 
                                       per_page=limit,
                                       filter=filter,
                                       rnd=rnd,
                                       all=all,
                                       min=min,
                                       max=max,
                                       user_id=user_id,
                                       period=period, 
                                       detail = detail)
            
            # Convertir IDs y paginar
            # converted = [convert_id(album) for album in albums]
            
            return jsonify({
                "data": albums,
                "pagination": {
                    "total": total,
                    "page": page,
                    "per_page": limit,
                    "total_pages": (total + limit - 1) // limit
                }
            })
            
        except Exception as e:
            logger.error(f"Error en {service_func.__name__}: {str(e)}")
            return jsonify({"error": str(e)}), 500
            
    return wrapper

def pipeline_to_query(pipeline: list) -> dict:
    """Convierte un pipeline de agregación simple a query de MongoDB"""
    query = {}
    for stage in pipeline:
        if "$match" in stage:
            query = {**query, **stage["$match"]}
    logger.info(f"Pipeline to query: {query}")
    return query



def get_albums_by_any_genres(genres):
    logger.info(f"Any Genres: {genres}")
    regex_genres = [create_case_insensitive_regex(genre, exact_match=True) for genre in genres]
    return {
        "$or": [
            {"genre": {"$in": regex_genres}},
            {"subgenres": {"$in": regex_genres}}
        ]
    }

def get_albums_by_all_genres(genres):
    logger.info(f"All Genres: {genres}")
    return {
        "$and": [
            {
                "$or": [
                    {"genre": create_case_insensitive_regex(genre, exact_match=True)},
                    {"subgenres": create_case_insensitive_regex(genre, exact_match=True)}
                ]
            } for genre in genres
        ]
    }
def get_albums_by_any_moods(moods):
    regex_moods = [create_case_insensitive_regex(mood, exact_match=True) for mood in moods]
    return {
        "$or": [
            {"mood": {"$in": regex_moods}},
        ]
    }
   
def get_albums_by_all_moods(moods):
   return {
        "$and": [
            {
                "$or": [
                    {"mood": create_case_insensitive_regex(mood, exact_match=True)},
                ]
            } for mood in moods
        ]
    }

def get_albums_by_any_compilations(compilations):
    regex_compilations = [create_case_insensitive_regex(compilation, exact_match=True) for compilation in compilations]
    return{
        "$or": [
            {"compilations": {"$in": regex_compilations}},
        ]
    }

def get_albums_by_all_compilations(compilations):
    return {
        "$and": [
            {
                "$or": [
                    {"compilations": create_case_insensitive_regex(compilation, exact_match=True)},
                ]
            } for compilation in compilations
        ]
    }

ADMIN_TOKENS = os.getenv("ADMIN_TOKENS", "").split(",")

def is_admin_token(token: str) -> bool:
    return token in ADMIN_TOKENS

def require_admin_token(func):
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid Authorization header"}), 403
        token = auth_header.replace("Bearer ", "").strip()
        if not is_admin_token(token):
            return jsonify({"error": "Forbidden: invalid admin token"}), 403
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper
