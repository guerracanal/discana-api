import requests
from cryptography.fernet import Fernet
from config import Config

# Simulación de almacenamiento en memoria para tokens de acceso
user_tokens = {}

# Instancia de Fernet para encriptar/desencriptar
fernet = Fernet(Config.ENCRYPTION_KEY)

def encrypt_token(token):
    """
    Encripta un token usando Fernet.
    """
    return fernet.encrypt(token.encode()).decode()

def decrypt_token(encrypted_token):
    """
    Desencripta un token encriptado usando Fernet.
    """
    return fernet.decrypt(encrypted_token.encode()).decode()

def save_access_token(user_id, access_token):
    """
    Guarda el token de acceso de Spotify para un usuario.
    """
    user_tokens[user_id] = access_token

def get_access_token_for_user(user_id):
    """
    Obtiene el token de acceso de Spotify para un usuario.
    """
    token = user_tokens.get(user_id)
    if not token:
        raise Exception(f"No se encontró un token de acceso para el usuario con ID: {user_id}")
    return token

def get_saved_albums_from_spotify(**params):
    """
    Llama a la API de Spotify para obtener los álbumes guardados de un usuario con paginación.
    """
    try:
        user_id = params.get('user_id')
        if not user_id:
            raise ValueError("El parámetro 'user_id' es obligatorio.")

        # Obtener parámetros de paginación
        limit = params.get('limit', 20)  # Límite por defecto: 20
        offset = (params.get('page', 1) - 1) * limit  # Calcular el offset

        # URL de la API de Spotify con parámetros de paginación
        spotify_api_url = f"https://api.spotify.com/v1/me/albums?limit={limit}&offset={offset}"
        
        # Obtener el token de acceso del usuario
        access_token = get_access_token_for_user(user_id)
        
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        
        # Llamar a la API de Spotify
        response = requests.get(spotify_api_url, headers=headers)
        response.raise_for_status()  # Lanza una excepción si la respuesta no es exitosa
        
        # Procesar la respuesta
        data = response.json()
        albums_data = data.get("items", [])
        total = data.get("total", 0)  # Total de álbumes guardados
        
        formatted_albums = []
        for item in albums_data:
            album = item.get("album", {})
            formatted_albums.append({
                "_id": album.get("id", ""),
                "artist": ", ".join([artist.get("name", "") for artist in album.get("artists", [])]),
                "title": album.get("name", ""),
                "date_release": album.get("release_date", ""),
                "genre": album.get("genres", []),
                "image": album.get("images", [{}])[0].get("url", ""),
                "spotify_id": album.get("id", ""),
                "spotify_link": album.get("external_urls", {}).get("spotify", ""),
                "tracks": album.get("total_tracks", 0),
            })

        return formatted_albums, total
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error al obtener los álbumes guardados de Spotify: {str(e)}")
