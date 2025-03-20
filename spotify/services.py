from datetime import datetime
import requests
from cryptography.fernet import Fernet
from config import Config
import requests
from typing import List, Tuple
import requests
from cryptography.fernet import Fernet
from logging_config import logger  # Importar el logger centralizado

# --------------------------
# Configuración y Helpers
# --------------------------

class Config:
    ENCRYPTION_KEY = Fernet.generate_key()  # Clave de ejemplo

user_tokens = {}
fernet = Fernet(Config.ENCRYPTION_KEY)

def encrypt_token(token: str) -> str:
    return fernet.encrypt(token.encode()).decode()

def decrypt_token(encrypted_token: str) -> str:
    return fernet.decrypt(encrypted_token.encode()).decode()

def save_access_token(user_id: str, access_token: str):
    user_tokens[user_id] = encrypt_token(access_token)

def get_access_token_for_user(user_id: str) -> str:
    encrypted_token = user_tokens.get(user_id)
    if not encrypted_token:
        raise ValueError(f"Token no encontrado para el usuario: {user_id}")
    return decrypt_token(encrypted_token)

# --------------------------
# Helpers Reutilizables
# --------------------------

def make_spotify_request(endpoint: str, **params) -> dict:
    """Realiza una solicitud GET a la API de Spotify con manejo robusto de errores."""
    try:
        user_id = params.get('user_id')
        if not user_id:
            logger.warning("Se intentó realizar una solicitud sin 'user_id'")
            raise ValueError("Se requiere user_id")
        
        access_token = get_access_token_for_user(user_id)
        logger.debug("Realizando solicitud a la API de Spotify con access_token: \n"+access_token);
        headers = {"Authorization": f"Bearer {access_token}"}
        if 'country' in params:
            headers["Accept-Language"] = f"{params['country']},en;q=0.9"  # Prioriza contenido local

         # Parámetros prohibidos por endpoint
        forbidden_params = {
                "recommendations": ["user_id", "filter", "rnd", "all"],
                "browse/new-releases": ["user_id", "per_page", "random"],
        }

        # Detectar endpoints dinámicos como "artists/{artist_id}/related-artists"
        if endpoint.startswith("artists/") and endpoint.endswith("/related-artists"):
            params.pop("user_id", None)

        for key in forbidden_params.get(endpoint, []):
            params.pop(key, None)

        # Asegurar user_id solo donde es necesario
        if endpoint in ["me/top/artists", "me/player/recently-played"]:
            params["user_id"] = params.get("user_id", "")

        if params.get('no_user_neccessary') == True:
            params.pop('user_id', None)

        for key in ['per_page', 'filter', 'rnd', 'all', 'user_neccessary']:
            params.pop(key, None)

        url = f"https://api.spotify.com/v1/{endpoint}"
        full_url = requests.Request('GET', url, params=params).prepare().url  # Construir URL completa
        logger.debug(f"Requesting: {full_url}")  # Log de la URL completa
        
        response = requests.get(
            url,
            headers=headers,
            params=params
        )
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, dict):  # Validar que la respuesta sea un diccionario
            logger.error(f"Respuesta inesperada de Spotify API: {data}")
            raise ValueError("Respuesta inesperada de Spotify API")
        logger.debug(f"Respuesta recibida: {data}")
        return data
    except requests.exceptions.HTTPError as e:
        logger.error(f"Error HTTP en Spotify API {url} - {e.response.status_code} - {e.response.text}")
        raise Exception(f"Error HTTP en Spotify API: {url} - {e.response.status_code} - {e.response.text}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error en Spotify API: {str(e)}")
        raise Exception(f"Error en Spotify API: {str(e)}")
    
def format_date(date_string: str) -> str:
    """Formatea una fecha en diferentes formatos."""
    parts = date_string.split('-')
    
    # Manejar diferentes formatos de fecha
    if len(parts) == 3:  # Formato completo YYYY-MM-DD
        return f"{parts[2].zfill(2)}/{parts[1].zfill(2)}/{parts[0]}"
    elif len(parts) == 2:  # Formato MM/YYYY
        return f"{parts[1].zfill(2)}/{parts[0]}"
    elif len(parts) == 1:  # Solo año YYYY
        return parts[0]
    else:
        return "Fecha inválida"

def format_album(album_data: dict) -> dict:
    """Formatea un álbum en el formato estándar"""
    return {
        "_id": album_data.get("id", ""),
        "artist": ", ".join([a.get("name", "") for a in album_data.get("artists", [])]),
        "title": album_data.get("name", ""),
        "date_release": format_date(album_data.get("release_date", "")),
        "genre": album_data.get("genres", []),
        "image": next((img["url"] for img in album_data.get("images", []) if img.get("height") == 640), None),
        "spotify_link": album_data.get("external_urls", {}).get("spotify", ""),
        "tracks": album_data.get("total_tracks", 0),
        "duration": round(sum(track.get("duration_ms", 0) for track in album_data.get("tracks", {}).get("items", [])) / 60000)
    }

# --------------------------
# Servicios de Álbumes
# --------------------------

def get_saved_albums_spotify(**params) -> Tuple[List[dict], int]:
    """Obtiene álbumes guardados del usuario"""
    params.setdefault('limit', params.get('per_page', 20))
    params['offset'] = (params.get('page', 1) - 1) * params['limit']
    
    data = make_spotify_request("me/albums", **params)
    return [format_album(item['album']) for item in data.get('items', [])], data.get('total', 0)

def get_new_releases_spotify(**params) -> Tuple[List[dict], int]:
    """Obtiene álbumes nuevos lanzados en Spotify según el país especificado."""
    # Extraer user_id primero
    user_id = params.get("user_id")
    if not user_id:
        raise ValueError("Se requiere user_id")

    # Validar y corregir códigos de país
    country_map = {
        "UK": "GB",
        "EN": "GB",
        "JP": "JP",
        "US": "US",
        "ES": "ES",
        "FR": "FR",
        "DE": "DE"
    }
    # Convertir a código ISO válido
    country = country_map.get(params.get("country", "US").upper(), "US")

    # Forzar parámetros válidos
    clean_params = {
        "user_id": user_id,
        "country": country,
        "market": country,  # Obligatorio para filtrar por país
        "limit": params.get("limit", 20),
        "offset": params.get("offset", 0)  # Agregar soporte para paginación
    }

    try:
        data = make_spotify_request("browse/new-releases", **clean_params)
        albums = data.get("albums", {}).get("items", [])
        if not isinstance(albums, list):  # Validar que sea una lista
            logger.error(f"Formato inesperado en la respuesta de nuevos lanzamientos: {data}")
            raise ValueError("Formato inesperado en la respuesta de nuevos lanzamientos")
        
        # Validar y formatear álbumes
        formatted_albums = []
        for album in albums:
            try:
                formatted_albums.append(format_album(album))
            except Exception as e:
                logger.warning(f"Error formateando álbum: {album}. Error: {str(e)}")
        
        return formatted_albums, len(formatted_albums)
    except Exception as e:
        logger.error(f"Error obteniendo nuevos lanzamientos: {str(e)}")
        return [], 0

def is_recent(release_date: str, days=365) -> bool:
    from datetime import datetime, timedelta
    try:
        release = datetime.strptime(release_date, "%Y-%m-%d")
        return (datetime.now() - release) < timedelta(days=days)
    except:
        return False


def get_recommended_albums_spotify(**params) -> Tuple[List[dict], int]:
    """Genera recomendaciones personalizadas combinando datos de artistas, tracks y lanzamientos recientes."""
    user_id = params.get("user_id")
    type = params.get("type")
    # page = params.get("page", 1)
    # limit = params.get("limit", 20)

    params.setdefault('limit', params.get('per_page', 20))
    params['offset'] = (params.get('page', 1) - 1) * params['limit']

    logger.info(f"Generando recomendaciones personalizadas para el usuario: {user_id}")
    
    try:
        # Obtener artistas principales
        #top_artists = _get_user_top_artists(user_id, limit=10)
        #artist_ids = [artist.get("id") for artist in top_artists if artist.get("id")]
        #logger.debug(f"Artistas principales: {artist_ids}")
        
        # Obtener tracks principales
        #top_tracks = _get_user_top_tracks(user_id, limit=30)
        #track_ids = [track.get("id") for track in top_tracks if track.get("id")]
        #logger.debug(f"Tracks principales: {track_ids}")
        
        # Combinar datos para recomendaciones
        recommendations = []

        

        if type == "recent":
            recommendations.extend(get_recent_albums(**params))
        elif type == "history":
            recommendations.extend(get_releases_from_listening_history(**params))
        else: 
            recommendations.extend(get_albums_from_paylist(playlist=type, **params))

        # Eliminar duplicados por ID
        unique_recommendations = {album["_id"]: album for album in recommendations if album.get("_id")}
        
        # Retornar los álbumes únicos como lista y el total
        formatted_albums = list(unique_recommendations.values())
        return formatted_albums[:params.get("limit", 20)], len(formatted_albums)

    except Exception as e:
        logger.error(f"Error generando recomendaciones personalizadas: {str(e)}")
        return [], 0

def _get_playlist_artists(user_id: str) -> List[dict]:
    """Obtiene artistas similares a partir de las playlists más escuchadas del usuario."""
    try:
        # Obtener las playlists del usuario
        playlists_data = make_spotify_request(
            endpoint="me/playlists",
            user_id=user_id,
            limit=2  # Limitar a las 10 playlists más escuchadas
        )
        playlists = playlists_data.get("items", [])
        
        # Extraer artistas de las playlists
        artists = []
        for playlist in playlists:
            tracks_data = make_spotify_request(
                endpoint=f"playlists/{playlist['id']}/tracks",
                user_id=user_id
            )
            for item in tracks_data.get("items", []):
                track = item.get("track", {})
                for artist in track.get("artists", []):
                    if artist not in artists:
                        artists.append(artist)
        
        return artists
    except Exception as e:
        logger.warning(f"Error obteniendo artistas similares a partir de playlists para el usuario {user_id}: {str(e)}")
        return []

def _get_user_top_tracks(user_id: str, limit: int = 5) -> List[dict]:
    """Obtiene tracks más escuchados del usuario."""
    data = make_spotify_request(
        endpoint="me/top/tracks",
        user_id=user_id,
        limit=limit,
        time_range="medium_term"  # Últimos 6 meses
    )
    return data.get("items", [])

def _get_albums_by_artist(artist_id: str, user_id: str, limit: int = 3) -> List[dict]:
    """Obtiene álbumes de un artista específico."""
    try:
        data = make_spotify_request(
            endpoint=f"artists/{artist_id}/albums",
            user_id=user_id,
            limit=limit,
            include_groups="album,single",  # Incluir álbumes y sencillos
            market="US"
        )
        albums = data.get("items", [])
        return [format_album(album) for album in albums if album.get("id")]
    except Exception as e:
        logger.warning(f"Error obteniendo álbumes para el artista {artist_id}: {str(e)}")
        return []

def _get_user_top_artists(user_id: str, limit: int = 5) -> List[dict]:
    """Obtiene artistas más escuchados del usuario."""
    try:
        data = make_spotify_request(
            endpoint="me/top/artists",
            user_id=user_id,
            limit=limit,
            time_range="medium_term"  # Últimos 6 meses
        )
        return data.get("items", [])
    except Exception as e:
        logger.error(f"Error obteniendo artistas principales para el usuario {user_id}: {str(e)}")
        return []

def get_recommended_albums(**params) -> List[dict]:
    """Obtiene álbumes populares por país"""
    try:
        # Validar semillas mínimas
        if not any([params.get("seed_artists"), params.get("seed_genres"), params.get("seed_tracks")]):
            raise ValueError("Se requieren al menos 2 semillas de diferentes tipos")
    
        params['limit'] = params.get('limit', 20) * 2  # Para evitar duplicados
        data = make_spotify_request("recommendations", **params)
        albums = {}
        for track in data.get('tracks', []):
            album = track.get('album', {})
            albums[album.get('id')] = format_album(album)
        return list(albums.values())[:params.get('limit', 20)]
    except Exception as e:
        logger.error(f"Error generando recomendaciones: {str(e)}")
        return []

def get_popular_albums_spotify(**params) -> List[dict]:
    """Obtiene álbumes populares por país"""
    country = params.get('country', 'US')
    playlist_id = f"37i9dQZEVXbMDoHDwVN2tF"  # Top 50 Global (actualizar según país)
    data = make_spotify_request(f"playlists/{playlist_id}/tracks", **params)
    albums = {}
    for item in data.get('items', []):
        album = item.get('track', {}).get('album', {})
        albums[album.get('id')] = format_album(album)
    return list(albums.values())

def get_albums_by_genre_spotify(**params) -> Tuple[List[dict], int]:
    """Obtiene álbumes por género"""
    genre = params.get('genre')
    if not genre:
        raise ValueError("Se requiere parámetro 'genre'")
    search_params = {
        'q': genre,
        'type': 'playlist',
        'limit': params.get('limit', 5)
    }
    search_data = make_spotify_request("search", **{**params, **search_params})
    albums = {}
    for playlist in search_data.get('playlists', {}).get('items', []):
        tracks_data = make_spotify_request(f"playlists/{playlist['id']}/tracks", **params)
        for item in tracks_data.get('items', []):
            album = item.get('track', {}).get('album', {})
            albums[album.get('id')] = format_album(album)
    
    return list(albums.values()), len(albums)

def get_albums_from_user_playlists(user_id: str, playlist_names: List[str]) -> List[dict]:
    """Obtiene álbumes de playlists específicas del usuario, como Radar de novedades y Descubrimiento semanal."""
    try:
        # Obtener todas las playlists del usuario
        playlists_data = make_spotify_request(
            endpoint="me/playlists",
            user_id=user_id,
            limit=50  # Limitar a las primeras 50 playlists
        )
        playlists = playlists_data.get("items", [])
        
        # Loggear los nombres de todas las playlists
        for playlist in playlists:
            logger.debug(f"Playlist encontrada: {playlist.get('name')}")

        # Filtrar playlists por nombre
        target_playlists = [
            playlist for playlist in playlists if playlist.get("name") in playlist_names
        ]
        
        albums = []
        for playlist in target_playlists:
            # Obtener las pistas de la playlist
            tracks_data = make_spotify_request(
                endpoint=f"playlists/{playlist['id']}/tracks",
                user_id=user_id
            )
            for item in tracks_data.get("items", []):
                track = item.get("track", {})
                album = track.get("album", {})
                if album.get("id") and album not in albums:
                    albums.append(format_album(album))
        
        return albums
    except Exception as e:
        logger.warning(f"Error obteniendo álbumes de playlists específicas para el usuario {user_id}: {str(e)}")
        return []

def get_albums_from_search_playlists(user_id: str, playlist_names: List[str]) -> List[dict]:
    """Obtiene álbumes de playlists específicas buscando por nombre usando el endpoint 'search'."""
    try:
        albums = []
        for playlist_name in playlist_names:
            # Buscar la playlist por nombre
            search_data = make_spotify_request(
                endpoint="search",
                user_id=user_id,
                q=playlist_name,
                type="playlist",
                limit=1  # Limitar a la primera coincidencia
            )
            playlists = search_data.get("playlists", {}).get("items", [])
            if not playlists:
                logger.warning(f"No se encontró ninguna playlist con el nombre: {playlist_name}")
                continue

            # Obtener la primera playlist encontrada
            playlist = playlists[0]
            logger.debug(f"Playlist encontrada: {playlist.get('name')} (ID: {playlist.get('id')})")

            # Obtener las pistas de la playlist
            tracks_data = make_spotify_request(
                endpoint=f"playlists/{playlist['id']}/tracks",
                user_id=user_id
            )
            for item in tracks_data.get("items", []):
                track = item.get("track", {})
                album = track.get("album", {})
                if album.get("id") and album not in albums:
                    albums.append(format_album(album))
        
        return albums
    except Exception as e:
        logger.warning(f"Error obteniendo álbumes de playlists buscadas por nombre para el usuario {user_id}: {str(e)}")
        return []
    

def get_albums_from_category_playlists(user_id: str, category_id: str, playlist_names: List[str]) -> List[dict]:
    """Obtiene álbumes de playlists específicas dentro de una categoría de Spotify."""
    try:
        # Obtener playlists de la categoría especificada
        category_data = make_spotify_request(
            endpoint=f"browse/categories/{category_id}",
            user_id=user_id
        )
        playlists = category_data.get("playlists", {}).get("items", [])
          # Loggear los nombres de todas las playlists
        for playlist in playlists:
            logger.debug(f"Playlist encontrada: {playlist.get('name')}")
        
        # Filtrar playlists por nombre
        target_playlists = [
            playlist for playlist in playlists
            if playlist.get("name") in playlist_names
        ]

        # Loggear nombres de playlists encontradas
        logger.debug(f"Playlists encontradas en categoría {category_id}: {[p.get('name') for p in target_playlists]}")

        albums = []
        for playlist in target_playlists:
            # Obtener las pistas de la playlist
            tracks_data = make_spotify_request(
                endpoint=f"playlists/{playlist['id']}/tracks",
                user_id=user_id
            )
            
            # Extraer álbumes únicos
            for item in tracks_data.get("items", []):
                track = item.get("track", {})
                if album := track.get("album"):
                    if album.get("id") and not any(a["id"] == album["id"] for a in albums):
                        albums.append(format_album(album))
        
        return albums

    except Exception as e:
        logger.warning(f"Error obteniendo álbumes de categoría {category_id}: {str(e)}")
        return []
    
def get_recent_albums(**params) -> List[dict]:
    recent_tracks = make_spotify_request(
        endpoint="me/player/recently-played",
        user_id=params.get("user_id"),
        limit=params.get("limit", 20),
        offset=params.get("offset", 0)
    )
    albums = {track['track']['album']['id']: track['track']['album'] 
              for track in recent_tracks.get('items', [])}.values()
    return [format_album(album) for album in albums]

def get_genre_releases_from_listening_history(user_id: str, genre: str) -> List[dict]:
    try:
        # Obtener artistas top del usuario
        top_artists = make_spotify_request(
            endpoint="me/top/artists",
            user_id=user_id,
            time_range="short_term",
            limit=20
        ).get("items", [])

        # Filtrar artistas del género objetivo
        genre_artists = [
            artist for artist in top_artists
            if genre.lower() in [g.lower() for g in artist.get("genres", [])]
        ]

        # Obtener lanzamientos recientes de esos artistas
        releases = []
        for artist in genre_artists:
            artist_albums = make_spotify_request(
                endpoint=f"artists/{artist['id']}/albums",
                user_id=user_id,
                include_groups="single,album",
                limit=1
            ).get("items", [])
            
            releases.extend([format_album(album) for album in artist_albums])

        return releases

    except Exception as e:
        logger.error(f"Error obteniendo historial para {genre}: {str(e)}")
        return []

GENRE_PLAYLIST_ID_MAP = {
    "pitchfork_new": "7q503YgioHAbo1iOIa67M8",  
    "pitchfork_selects": "7f9o34JAe8ZSRq4GX7f0Ol",
    "asturiana": "7H6h4MOojh4as892BrGs6d",
    "NPR_new": "5X8lN5fZSrLnXzFtDEUwb9",
    "JC_indie_new": "2uOpKxcmVwIEfZ8welQSzq",
    "JC_week_new": "1Y5VQwD7a0u6FxA9Yk7nPu",
    "JC_100": "6snL5r74SvjsTR38XAcN3F",
    "top_hits": "5iwkYfnHAGMEFLiHFFGnP4",
    "PMB_new": "1XLX6Ptnl74kG2fTSo3JSV",
    "acp_rock_spain":"64frvZUdrdb4grFxckU9MF",
    "acp_punk_spain":"5WRuCKhCdeSqBGRAUtXviy",
    "ts_metal":"173gN3GcuhIDaZKJOw0luH",
    "sonemic_selects":"1bZsWs0bwQReyC4MpWnr5S"
}

#    """Obtiene álbumes guardados del usuario"""
#    params.setdefault('limit', params.get('per_page', 20))
#    params['offset'] = (params.get('page', 1) - 1) * params['limit']
    
#    data = make_spotify_request("me/albums", **params)
#    return [format_album(item['album']) for item in data.get('items', [])], data.get('total', 0)

def get_albums_from_paylist(playlist: str, **params) -> List[dict]:
    try:
        params.setdefault('limit', params.get('per_page', 20))
        params['offset'] = (params.get('page', 1) - 1) * params['limit']

        playlist_id = GENRE_PLAYLIST_ID_MAP.get(playlist.lower())
        if not playlist_id:
            # Verificar si el parámetro playlist tiene formato de ID de Spotify
            if len(playlist) == 22 and playlist.isalnum():
                playlist_id = playlist
            else:
                return []

        # Obtener tracks directamente de la playlist con paginación
        tracks_data = make_spotify_request(
            endpoint=f"playlists/{playlist_id}/tracks",
            **params
        )

        # Procesar álbumes únicos de los tracks
        recent_albums = {}
        for item in tracks_data.get("items", []):
            track = item.get("track")
            if not track:
                continue

            album = track.get("album")
            if album and album.get("id"):  # and is_recent(album.get("release_date")):
                album_id = album.get("id")
                if album_id not in recent_albums:
                    recent_albums[album_id] = format_album(album)

        return list(recent_albums.values())

    except Exception as e:
        logger.error(f"Error crítico obteniendo {playlist}: {str(e)}", exc_info=True)
        return []
    
def get_releases_from_listening_history(**params) -> List[dict]:
    try:

        # Obtener artistas top del usuario con paginación
        top_artists = make_spotify_request(
            endpoint="me/top/artists",
            user_id=params.get("user_id"),
            time_range="long_term",  # medium_term, long_term
            limit=params.get("limit", 20),
            offset=params.get("offset", 0)
        ).get("items", [])

        # Obtener lanzamientos recientes de esos artistas
        releases = []
        for artist in top_artists:
            artist_albums = make_spotify_request(
                endpoint=f"artists/{artist['id']}/albums",
                user_id=params.get("user_id"),
                include_groups="single,album",
                limit=1
            ).get("items", [])
            
            releases.extend([format_album(album) for album in artist_albums])

        return releases

    except Exception as e:
        logger.error(f"Error obteniendo historial para: {str(e)}")
        return []