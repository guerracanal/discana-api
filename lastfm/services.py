from datetime import datetime
import requests
from typing import List, Tuple
from config import Config
from logging_config import logger
from cryptography.fernet import Fernet
from app import mongo
from pymongo import errors
import hashlib

# --------------------------
# Configuración Last.fm
# --------------------------

user_tokens = {}
fernet = Fernet(Config.ENCRYPTION_KEY)

class LastfmConfig(Config):
    LASTFM_API_KEY = Config.LASTFM_API_KEY
    LASTFM_API_SECRET = Config.LASTFM_API_SECRET
    BASE_URL = "http://ws.audioscrobbler.com/2.0/"

def encrypt_token(token: str) -> str:
    return fernet.encrypt(token.encode()).decode()

def decrypt_token(encrypted_token: str) -> str:
    return fernet.decrypt(encrypted_token.encode()).decode()


def save_lastfm_session(session_key: str, username: str):
    encrypted_key = fernet.encrypt(session_key.encode()).decode()
    try:
        result = mongo.db['lastfm_sessions'].update_one(
            {'username': username},
            {'$set': {'session_key': encrypted_key, 'last_updated': datetime.utcnow()}},
            upsert=True
        )
        if result.matched_count == 0:
            logger.info(f"Nueva sesión Last.fm guardada para {username}")
        else:
            logger.info(f"Sesión Last.fm actualizada para {username}")
    except errors.PyMongoError as e:
        logger.error(f"Error al guardar la sesión Last.fm en MongoDB: {str(e)}", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"Unexpected error saving Last.fm session: {e}", exc_info=True)
        raise


def get_lastfm_session(username: str) -> str:
    try:
        session_data = mongo.db['lastfm_sessions'].find_one({'username': username})
        if session_data:
            return fernet.decrypt(session_data['session_key'].encode()).decode()
        else:
            raise ValueError(f"Token no encontrado para el usuario: {username}")
    except errors.PyMongoError as e:
        logger.error(f"Error al obtener la sesión Last.fm de MongoDB: {str(e)}", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"Unexpected error getting Last.fm session: {e}", exc_info=True)
        raise

# --------------------------
# Helpers Reutilizables
# --------------------------

def make_lastfm_request(method: str, **params) -> dict:
    """Realiza una solicitud GET a la API de Last.fm"""
    try:
        params.update({
            'method': method,
            'api_key': LastfmConfig.LASTFM_API_KEY,
            'format': 'json'
        })
        
        logger.info(f"Solicitando a Last.fm: {method} con {params}")

        full_url = requests.Request('GET', LastfmConfig.BASE_URL, params=params).prepare().url  # Construir URL completa
        logger.info(f"Requesting: {full_url}")  # Log de la URL completa
        
        response = requests.get(LastfmConfig.BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()
        
        if 'error' in data:
            logger.error(f"Error Last.fm {data['error']}: {data['message']}")
            raise Exception(f"{data['message']}")
            
        return data
        
    except requests.exceptions.HTTPError as e:
        logger.error(f"Error HTTP {e.response.status_code}: {e.response.text}", exc_info=True) # exc_info=True agrega el traceback
        raise
    except Exception as e:
        logger.error(f"Error general: {str(e)}", exc_info=True) # exc_info=True agrega el traceback
        raise

def format_date_lastfm(date_str: str) -> str:
    """Formatea fechas de Last.fm"""
    try:
        if not date_str or len(date_str) < 4:
            return ""
            
        if len(date_str) == 4:  # Solo año
            return date_str
            
        date_formats = [
            '%d %b %Y',  # 01 Jan 2020
            '%b %Y',     # Jan 2020
            '%Y-%m-%d',  # 2020-01-01
        ]
        
        for fmt in date_formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime("%d/%m/%Y") if ' ' in date_str else date_str
            except:
                continue
                
        return date_str.split(' ')[0]
    except:
        return ""

def get_album_info_lastfm(artist: str, album: str, mbid: str = None, user: str = None, include_track_info: bool = False) -> dict:
    """Obtiene información detallada de un álbum, priorizando mbid."""
    try:
        params = {}
        if mbid:
            params['mbid'] = mbid
        else:
            params['artist'] = artist
            params['album'] = album
        if user:
            params['username'] = user

        data = make_lastfm_request('album.getInfo', **params)
        if 'error' in data:  # Check for Last.fm errors
            logger.error(f"Last.fm API error: {data['message']}")
            return {}
        album_info = data.get('album', {})

        if not isinstance(album_info, dict):
            logger.warning(f"Unexpected album_info type from Last.fm API: {type(album_info)}. Returning empty dictionary.")
            return {}

        # Si se solicita información de tracks, invocar el método auxiliar
        if include_track_info:
            album_info = _add_track_info_to_album(album_info, artist, user)

        return album_info

    except Exception as e:
        logger.warning(f"Error obteniendo info de {artist} - {album} (mbid: {mbid}): {str(e)}", exc_info=True)
        return {}


def _add_track_info_to_album(album_info: dict, artist: str, user: str) -> dict:
    """Añade información detallada de los tracks al álbum."""
    try:
        tracks = album_info.get('tracks', {}).get('track', [])
        if isinstance(tracks, dict):  # Si solo hay una pista, convertirla en lista
            tracks = [tracks]

        user_most_listened_track = None
        total_most_listened_track = None
        max_user_playcount = 0
        max_total_playcount = 0

        for track in tracks:
            track_name = track.get('name')
            if not track_name:
                continue

            # Invocar track.getInfo para obtener userplaycount y playcount
            try:
                track_info = make_lastfm_request(
                    'track.getInfo',
                    artist=artist,
                    track=track_name,
                    username=user
                )
                track_user_playcount = int(track_info.get('track', {}).get('userplaycount', 0))
                track_total_playcount = int(track_info.get('track', {}).get('playcount', 0))
            except Exception as e:
                logger.warning(f"Error fetching track info for {track_name}: {str(e)}")
                track_user_playcount = 0
                track_total_playcount = 0

            # Determinar la pista más escuchada por el usuario
            if track_user_playcount > max_user_playcount:
                max_user_playcount = track_user_playcount
                user_most_listened_track = {
                    "name": track_name,
                    "user_playcount": track_user_playcount
                }

            # Determinar la pista más escuchada en general
            if track_total_playcount > max_total_playcount:
                max_total_playcount = track_total_playcount
                total_most_listened_track = {
                    "name": track_name,
                    "total_playcount": track_total_playcount
                }

        album_info['user_most_listened_track'] = user_most_listened_track
        album_info['total_most_listened_track'] = total_most_listened_track

        # Calcular album_playcount
        user_scrobbles = int(album_info.get('userplaycount', 0))
        total_tracks = len(tracks)
        album_info['album_playcount'] = round(user_scrobbles / total_tracks, 2) if total_tracks > 0 else 0

        return album_info

    except Exception as e:
        logger.error(f"Error añadiendo información de tracks al álbum: {str(e)}")
        return album_info

def format_album_lastfm(album_data: dict, use_album_info: bool = False) -> dict:
    """Formatea un álbum de Last.fm, enriqueciendo con get_album_info (opcional)."""
    if not isinstance(album_data, dict):
        logger.error(f"Error: album_data is not a dictionary: {album_data}", exc_info=True)
        return {"error": "invalid_album_data"}

    artist_name = album_data.get('artist', {}).get('name') or album_data.get('artist', '')
    album_name = album_data.get('name', '')
    mbid = album_data.get('mbid', '')
    _id = mbid or album_name.replace(" ", "_") + "_" + artist_name.replace(" ", "_")

    info_album = {}  # Initialize as empty dictionary
    if use_album_info:
        info_album = get_album_info(artist_name, album_name, mbid)
        if not isinstance(info_album, dict):
            logger.warning(f"Unexpected info_album type: {type(info_album)}. Using album_data.")
            info_album = {}

    try:
        total_playcount = int(info_album.get('playcount', 0))
        total_listeners = int(info_album.get('listeners', 0))
    except ValueError as e:
        logger.warning(f"Invalid total_playcount or total_listeners: {e}. Setting to 0.")
        total_playcount = 0
        total_listeners = 0

    tracks = info_album.get('tracks', {}).get('track', [])
    if isinstance(tracks, dict):  # Si solo hay una pista, convertirla en lista
        tracks = [tracks]
    elif not isinstance(tracks, list):  # Validar que sea una lista
        tracks = []

    duration_total = round(
        sum(safe_int(track.get('duration', 0)) for track in tracks if isinstance(track, dict)) / 60, 0
    )

    genre, subgenres = extract_genres(info_album)

    try:
        playcount = safe_int(album_data.get('playcount', 0))
        listeners = safe_int(album_data.get('listeners', 0))
        tracks_total = len(tracks)  # Calculate the total number of tracks
        listens = playcount // tracks_total if tracks_total > 0 else 0
        percentage_playcount = round((playcount / total_playcount) * 100 if total_playcount > 0 else 0, 2)
        percentage_listeners = round((listeners / total_listeners) * 100 if total_listeners > 0 else 0, 2)
    except (ValueError, TypeError) as e:
        logger.warning(f"Error calculating percentages or listens: {e}. Setting to 0.")
        percentage_playcount = 0
        percentage_listeners = 0
        listens = 0

    # Calcular album_playcount
    user_scrobbles = safe_int(info_album.get('userplaycount', 0))
    album_playcount = round(user_scrobbles / tracks_total, 2) if tracks_total > 0 else 0

    result = {
        "mbid": mbid,
        "artist": artist_name,
        "title": album_name,
        "date_release": format_date_lastfm(info_album.get('releasedate', '')),
        "genre": genre,
        "subgenres": subgenres,
        "duration": duration_total,
        "total_playcount": total_playcount,
        "total_listeners": total_listeners,
        "image": get_largest_image(info_album, album_data),
        "playcount": playcount,
        "lastfm_link": info_album.get('url', album_data.get('url', '')),
        "listeners": listeners,
        "tracks": tracks_total,
        "listens": listens,
        "percentage_playcount": percentage_playcount,
        "percentage_listeners": percentage_listeners,
        "user_most_listened_track": info_album.get('user_most_listened_track'),
        "total_most_listened_track": info_album.get('total_most_listened_track'),
        "album_playcount": album_playcount
    }
    return result


def safe_int(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0

def extract_genres(album_data):
    if not isinstance(album_data, dict):
        logger.warning(f"Unexpected album_data type in extract_genres: {type(album_data)}. Returning empty lists.")
        return [], []

    tags = album_data.get('tags', {}).get('tag', [])
    if isinstance(tags, list):
        filtered_tags = [tag for tag in tags if isinstance(tag, dict) and tag.get('name') and not tag['name'].isdigit()]
        if len(filtered_tags) > 0:
            genre = [filtered_tags[0].get('name')]
            subgenres = [tag.get('name') for tag in filtered_tags[1:]]
        else:
            genre = []
            subgenres = []
    else:
        genre = []
        subgenres = []
    return genre, subgenres

def get_largest_image(info_album, album_data):
    return next((img['#text'] for img in info_album.get('image', []) if img.get('size') == 'extralarge'),
                next((img['#text'] for img in album_data.get('image', []) if img.get('size') == 'extralarge'), ''))




# --------------------------
# Servicios Last.fm
# --------------------------

#TODO 
# tag.getTopAlbums
# Get the top albums tagged by this tag, ordered by tag count.

#user.getWeeklyAlbumChart
#Get an album chart for a user profile, for a given date range. If no date range is supplied, it will return the most recent album chart for this user.
    

#geo.getTopArtists
#geo.getTopTracks
#artist.getSimilar

# https://musicbrainz.org/ws/2/release/053a0640-8c4b-4ea8-adaa-1250dcbe6580?inc=artists+collections+labels+recordings+release-groups&fmt=json
# https://musicbrainz.org/ws/2/release-group/6cb9f36f-df55-463a-82a1-84bbdd03e95e?inc=genres+tags+ratings+url-rels&fmt=json

def get_user_top_albums(**params) -> Tuple[List[dict], int]:
    """Álbumes más escuchados por el usuario"""
    try:
        user_id = params.get('user_id')
        if not user_id:
            raise ValueError("user_id is required")
        
        # overall | 7day | 1month | 3month | 6month | 12month
        period = params.get('period', 'overall')  # Use 'overall' as default if 'period' is not in params
        detail = params.get('detail', True)
        detail = detail.lower() == 'true' if isinstance(detail, str) else bool(detail)
        
        page = params.get('page', 1)
        limit = params.get('limit', 10)

        request_params = {
            'user': user_id,
            'period': period,
            'page': page,
            'limit': limit
        }

        data = make_lastfm_request('user.getTopAlbums', **request_params)
        top_albums = data.get('topalbums', {})
        albums_list = top_albums.get('album', [])

        albums = []
        total = int(top_albums.get('@attr', {}).get('total', 0))

        for item in albums_list:
            if isinstance(item, dict):
                try:
                    album_data = format_album_lastfm(item, detail)
                    if isinstance(album_data, dict) and "error" not in album_data:
                        albums.append(album_data)
                    else:
                        logger.warning(f"format_album_lastfm returned an error or non-dictionary: {album_data}")
                except Exception as e:
                    logger.error(f"Error processing album: {item}, error: {e}", exc_info=True)
            else:
                logger.warning(f"Skipping non-dictionary album item: {item}")

        return albums, total

    except Exception as e:
        logger.error(f"Error en top álbumes: {str(e)}", exc_info=True)
        raise

def get_country_top_albums(country: str, page: int = 1, per_page: int = 20) -> Tuple[List[dict], int]:
    """Álbumes más populares por país"""
    try:
        data = make_lastfm_request(
            'geo.getTopAlbums',
            country=country,
            page=page,
            limit=per_page
        )
        
        albums_data = data.get('albums', {})
        albums = [format_album_lastfm(a) for a in albums_data.get('album', [])]
        total = int(albums_data.get('@attr', {}).get('total', 0))
        
        return albums, total
        
    except Exception as e:
        logger.error(f"Error en álbumes por país: {str(e)}")
        return [], 0

def get_tag_recommendations(tag: str, page: int = 1, per_page: int = 20) -> Tuple[List[dict], int]:
    """Recomendaciones por género/etiqueta"""
    try:
        data = make_lastfm_request(
            'tag.getTopAlbums',
            tag=tag,
            page=page,
            limit=per_page
        )
        
        albums_data = data.get('albums', {})
        albums = [format_album_lastfm(a) for a in albums_data.get('album', [])]
        total = int(albums_data.get('@attr', {}).get('total', 0))
        
        return albums, total
        
    except Exception as e:
        logger.error(f"Error en recomendaciones: {str(e)}")
        return [], 0

def get_user_recent_albums(user: str, limit: int = 20) -> List[dict]:
    """Álbumes recientemente escuchados"""
    try:
        data = make_lastfm_request(
            'user.getRecentTracks',
            user=user,
            limit=limit
        )
        
        tracks = data.get('recenttracks', {}).get('track', [])
        albums = {}
        
        for track in tracks:
            album_info = track.get('album', {})
            if album_info.get('#text'):
                artist = track.get('artist', {}).get('#text', '')
                album_name = album_info['#text']
                album_id = f"{artist}_{album_name}"
                
                if album_id not in albums:
                    full_data = get_album_info(artist, album_name)
                    if full_data:
                        albums[album_id] = format_album_lastfm(full_data)
        
        return list(albums.values())
        
    except Exception as e:
        logger.error(f"Error en álbumes recientes: {str(e)}")
        return []

def get_personalized_recommendations(user: str, limit: int = 20) -> List[dict]:
    """Recomendaciones personalizadas basadas en tus gustos"""
    try:
        # Obtener top tags del usuario
        tags_data = make_lastfm_request(
            'user.getTopTags',
            user=user,
            limit=3
        )
        tags = [t['name'] for t in tags_data.get('toptags', {}).get('tag', [])]
        
        # Obtener recomendaciones por cada tag
        recommendations = []
        for tag in tags:
            albums, _ = get_tag_recommendations(tag, limit=5)
            recommendations.extend(albums)
        
        # Eliminar duplicados
        unique = {a['_id']: a for a in recommendations}
        return list(unique.values())[:limit]
        
    except Exception as e:
        logger.error(f"Error en recomendaciones personalizadas: {str(e)}")
        return []

def scrobble_album(username: str, album: str, artist: str, timestamp: int = None) -> dict:
    """
    Scrobblea todas las canciones de un álbum en Last.fm.
    
    :param username: Nombre de usuario de Last.fm.
    :param album: Nombre del álbum.
    :param artist: Nombre del artista.
    :param timestamp: Marca de tiempo para el scrobble (opcional, por defecto usa el tiempo actual).
    :return: Respuesta de la API de Last.fm.
    """
    try:
        # Obtener la sesión del usuario
        session_key = get_lastfm_session(username)

        # Obtener información del álbum para obtener las pistas
        album_info = get_album_info(artist=artist, album=album)
        tracks = album_info.get('tracks', {}).get('track', [])
        if isinstance(tracks, dict):  # Si solo hay una pista, convertirla en lista
            tracks = [tracks]

        if not tracks:
            raise ValueError(f"No se encontraron pistas para el álbum '{album}' de '{artist}'.")

        # Preparar scrobbles
        scrobbles = []
        timestamp = timestamp or int(datetime.utcnow().timestamp())
        for i, track in enumerate(tracks):
            scrobbles.append({
                'track': track.get('name'),
                'artist': artist,
                'album': album,
                'timestamp': timestamp + i  # Incrementar el timestamp para cada pista
            })

        # Enviar scrobbles a Last.fm
        params = {
            'method': 'track.scrobble',
            'api_key': LastfmConfig.LASTFM_API_KEY,
            'sk': session_key,
            'format': 'json'
        }
        for i, scrobble in enumerate(scrobbles):
            params.update({
                f'track[{i}]': scrobble['track'],
                f'artist[{i}]': scrobble['artist'],
                f'album[{i}]': scrobble['album'],
                f'timestamp[{i}]': scrobble['timestamp']
            })

        # Firmar la solicitud
        params['api_sig'] = _generate_lastfm_signature(params)

        # Realizar la solicitud
        response = requests.post(LastfmConfig.BASE_URL, data=params)
        response.raise_for_status()
        data = response.json()

        if 'error' in data:
            logger.error(f"Error al scrobblear álbum en Last.fm: {data['message']}")
            raise Exception(data['message'])

        logger.info(f"Álbum '{album}' de '{artist}' scrobbleado exitosamente para el usuario '{username}'.")
        return data

    except Exception as e:
        logger.error(f"Error scrobbleando álbum '{album}' de '{artist}' para el usuario '{username}': {str(e)}", exc_info=True)
        return {"error": str(e)}


def _generate_lastfm_signature(params: dict) -> str:
    """
    Genera la firma para la solicitud de Last.fm.
    
    :param params: Parámetros de la solicitud.
    :return: Firma generada.
    """
    try:
        sorted_params = ''.join(f"{key}{value}" for key, value in sorted(params.items()) if key != 'format')
        signature_base = f"{sorted_params}{LastfmConfig.LASTFM_API_SECRET}"
        return hashlib.md5(signature_base.encode('utf-8')).hexdigest()
    except Exception as e:
        logger.error(f"Error generando firma para Last.fm: {str(e)}", exc_info=True)
        raise