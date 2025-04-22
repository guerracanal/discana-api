from datetime import datetime
import requests
from typing import List, Tuple, Optional
from config import Config
from logging_config import logger
from cryptography.fernet import Fernet
from app import mongo

# --------------------------
# Configuración Discogs
# --------------------------

class DiscogsConfig(Config):
    DISCOGS_API_KEY = Config.DISCOGS_API_KEY
    DISCOGS_API_SECRET = Config.DISCOGS_API_SECRET
    DISCOGS_USER_AGENT = 'Discana/1.0'
    BASE_URL = "https://api.discogs.com/"

fernet = Fernet(Config.ENCRYPTION_KEY)
user_tokens = {}

# --------------------------
# Helpers de Autenticación
# --------------------------

def save_discogs_token(user_id: str, token: str, secret: str):
    encrypted = fernet.encrypt(f"{token}:{secret}".encode())
    user_tokens[user_id] = encrypted.decode()

def get_discogs_token(user_id: str) -> Optional[Tuple[str, str]]:
    encrypted = user_tokens.get(user_id)
    if encrypted:
        decrypted = fernet.decrypt(encrypted.encode()).decode()
        return decrypted.split(':')
    return None

def save_discogs_tokens(user_id, encrypted_token):
    """Guarda los tokens de Discogs en la base de datos."""
    try:
        mongo.db.users.update_one(
            {"discogs_id": user_id},
            {"$set": {"discogs_token": encrypted_token}},
            upsert=True
        )
        logger.info(f"Discogs tokens saved for user {user_id}")
    except Exception as e:
        logger.error(f"Error saving Discogs tokens for user {user_id}: {str(e)}")
        raise

# --------------------------
# Helpers Reutilizables
# --------------------------

def make_discogs_request(endpoint: str, user_id: str = None, **params) -> dict:
    """Realiza solicitudes autenticadas a la API de Discogs"""
    try:
        print(DiscogsConfig.DISCOGS_API_KEY, DiscogsConfig.DISCOGS_API_SECRET)
        logger.info(f"API Key: {DiscogsConfig.DISCOGS_API_KEY}, API Secret: {DiscogsConfig.DISCOGS_API_SECRET}")

        headers = {
            'User-Agent': DiscogsConfig.DISCOGS_USER_AGENT,
            'Authorization': f'Discogs key={DiscogsConfig.DISCOGS_API_KEY}, secret={DiscogsConfig.DISCOGS_API_SECRET}'
        }
        
        # Autenticación OAuth si hay usuario
        if user_id:
            tokens = get_discogs_token(user_id)
            logger.info(f"Tokens recuperados: {tokens}")
            if tokens:
                headers['Authorization'] = f'OAuth oauth_consumer_key="{DiscogsConfig.DISCOGS_API_KEY}", oauth_token="{tokens[0]}"'
        
        url = f"{DiscogsConfig.BASE_URL}{endpoint}"
        logger.debug(f"Requesting: {url}")

        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        # Manejar rate limiting
        remaining = int(response.headers.get('X-Discogs-RateLimit-Remaining', 60))
        if remaining < 10:
            logger.warning(f"Límite de API cercano: {remaining} llamadas restantes")
        
        return response.json()
        
    except requests.exceptions.HTTPError as e:
        logger.error(f"Error HTTP {e.response.status_code}: {e.response.text}")
        raise
    except Exception as e:
        logger.error(f"Error en Discogs API: {str(e)}")
        raise

def format_release(release_data: dict) -> dict:
    """Formatea un release de Discogs a formato estándar"""
    return {
        "_id": release_data.get('id'),
        "artist": ", ".join([a.get('name', '') for a in release_data.get('artists', [])]),
        "title": release_data.get('title'),
        "date_release": release_data.get('year'),
        "genre": release_data.get('genres', []),
        "subgenres": release_data.get('styles', []),
        "image": release_data.get('cover_image'),
        "thumbnail": release_data.get('thumb'),
        "tracklist": [t['title'] for t in release_data.get('tracklist', [])],
        "formats": [f"{f['name']} ({', '.join(f.get('descriptions', []))})" for f in release_data.get('formats', [])],
        "format": release_data.get('formats', [{}])[0].get('name'),
        "rating": release_data.get('community', {}).get('rating', {}).get('average'),
        "marketplace": {
            "min_price": release_data.get('lowest_price'),
            "have": release_data.get('num_have'),
            "want": release_data.get('num_want')
        },
        "label": [l.get('name', '') for l in release_data.get('labels', [])],
        "master_id": release_data.get('master_id'),
        "master_url": release_data.get('master_url'),
        "resource_url": release_data.get('resource_url'),
        "discogs_link": release_data.get('resource_url').replace('api.discogs.com/releases/', 'discogs.com/release/'),
    }

# --------------------------
# Servicios Discogs
# --------------------------

def get_user_collection(**params) -> Tuple[List[dict], int]:
    """Obtiene la colección de discos del usuario"""
    try:

        user_id = params.get('user_id')
        page = params.get('page', 1)
        per_page = params.get('limit', 20)

        data = make_discogs_request(
            f"users/{user_id}/collection/folders/0/releases",
            sort="added",
            sort_order="desc",
            user_id=user_id,
            page=page,
            per_page=per_page
        )
        
        releases = [format_release(r['basic_information']) for r in data.get('releases', [])]
        return releases, data.get('pagination', {}).get('items', 0)
        
    except Exception as e:
        logger.error(f"Error obteniendo colección: {str(e)}")
        return [], 0

def get_user_wantlist(user_id: str, page: int = 1, per_page: int = 20) -> Tuple[List[dict], int]:
    """Obtiene la lista de deseos del usuario"""
    try:
        data = make_discogs_request(
            f"users/{user_id}/wantlist",
            user_id=user_id,
            page=page,
            per_page=per_page
        )
        
        return [format_release(item['basic_information']) for item in data.get('wants', [])], data.get('pagination', {}).get('items', 0)
        
    except Exception as e:
        logger.error(f"Error obteniendo wantlist: {str(e)}")
        return [], 0

def search_releases(query: str, page: int = 1, per_page: int = 20) -> Tuple[List[dict], int]:
    """Busca lanzamientos en el catálogo de Discogs"""
    try:
        data = make_discogs_request(
            "database/search",
            q=query,
            type='release',
            page=page,
            per_page=per_page
        )
        
        return [format_release(result) for result in data.get('results', [])], data.get('pagination', {}).get('items', 0)
        
    except Exception as e:
        logger.error(f"Error en búsqueda: {str(e)}")
        return [], 0

def get_marketplace_listings(release_id: str, page: int = 1, per_page: int = 20) -> Tuple[List[dict], int]:
    """Obtiene listados del marketplace para un release"""
    try:
        data = make_discogs_request(
            f"marketplace/listings",
            release_id=release_id,
            page=page,
            per_page=per_page
        )
        
        listings = []
        for item in data.get('listings', []):
            listing = {
                "price": item.get('price'),
                "condition": item.get('condition'),
                "seller": item.get('seller').get('username'),
                "location": item.get('ships_from'),
                "posted": item.get('posted')
            }
            listings.append(listing)
            
        return listings, data.get('pagination', {}).get('items', 0)
        
    except Exception as e:
        logger.error(f"Error obteniendo listados: {str(e)}")
        return [], 0

def get_recommendations(user_id: str, limit: int = 20) -> List[dict]:
    """Recomendaciones basadas en la colección del usuario"""
    try:
        # Obtener géneros más comunes en la colección
        collection, _ = get_user_collection(user_id, per_page=100)
        genre_count = {}
        for release in collection:
            for genre in release.get('genre', []):
                genre_count[genre] = genre_count.get(genre, 0) + 1
                
        top_genres = sorted(genre_count.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Buscar lanzamientos en los mismos géneros
        recommendations = []
        for genre, _ in top_genres:
            results, _ = search_releases(f"genre:{genre}", per_page=10)
            recommendations.extend(results)
            
        # Eliminar duplicados y ya en colección
        collection_ids = {r['_id'] for r in collection}
        unique_recs = [r for r in recommendations if r['_id'] not in collection_ids]
        
        return unique_recs[:limit]
        
    except Exception as e:
        logger.error(f"Error generando recomendaciones: {str(e)}")
        return []

def get_new_releases_discogs(**params) -> Tuple[List[dict], int]:
    """Obtiene los últimos lanzamientos añadidos a Discogs"""
    try:
        page = params.get('page', 1)
        per_page = params.get('limit', 20)
        
        data = make_discogs_request(
            "database/search",
            sort="added",
            sort_order="desc",
            type="release",
            page=page,
            per_page=per_page
        )
        
        return [format_release(result) for result in data.get('results', [])], data.get('pagination', {}).get('items', 0)
        
    except Exception as e:
        logger.error(f"Error obteniendo nuevos lanzamientos: {str(e)}")
        return [], 0