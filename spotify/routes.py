import os
from pathlib import Path
from flask import Blueprint, jsonify, request, redirect, url_for
import requests
from spotify.services import save_access_token
from config import Config
from cryptography.fernet import Fernet

from utils.constants import Collections, Parameters

spotify_blueprint = Blueprint(Collections.SPOTIFY, __name__)

SPOTIFY_CLIENT_ID = Config.SPOTIFY_CLIENT_ID
SPOTIFY_CLIENT_SECRET = Config.SPOTIFY_SECRET

SPOTIFY_API_REDIRECT_URI = os.path.join(Config.API_URL, Config.API_VERSION, Collections.SPOTIFY, Parameters.CALLBACK)
SPOTIFY_FRONTEND_REDIRECT_URI = os.path.join(Config.FRONTEND_URL, Collections.SPOTIFY)

# Generar una instancia de Fernet con la clave de encriptación
try:
    fernet = Fernet(Config.ENCRYPTION_KEY)
except ValueError as e:
    raise ValueError("Invalid ENCRYPTION_KEY in configuration. Ensure it is a 32-byte, URL-safe, base64-encoded string.") from e

# Login Spotify
@spotify_blueprint.route(f'/{Parameters.LOGIN}', methods=['GET'])
def spotify_login():
    scopes = [
        "user-top-read",
        "user-library-read",
        "user-read-recently-played"
    ]
    spotify_auth_url = (
        f"https://accounts.spotify.com/authorize"
        f"?client_id={SPOTIFY_CLIENT_ID}"
        f"&response_type=code"
        f"&redirect_uri={SPOTIFY_API_REDIRECT_URI}"
        f"&scope={'%20'.join(scopes)}"
    )
    return redirect(spotify_auth_url)

# Callback Spotify
@spotify_blueprint.route(f'/{Parameters.CALLBACK}', methods=['GET'])
def spotify_callback():
    code = request.args.get('code')
    if not code:
        return jsonify({"error": "Missing authorization code"}), 400

    # 1. Obtener token de Spotify
    token_url = "https://accounts.spotify.com/api/token"
    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": SPOTIFY_API_REDIRECT_URI,
        "client_id": SPOTIFY_CLIENT_ID,
        "client_secret": SPOTIFY_CLIENT_SECRET,
    }
    
    token_response = requests.post(token_url, data=payload)
    if token_response.status_code != 200:
        return jsonify({"error": "Token exchange failed"}), 400

    access_token = token_response.json().get('access_token')
    
    # Encriptar el token de acceso
    encrypted_token = fernet.encrypt(access_token.encode()).decode()
    
    # 2. Obtener información del usuario de Spotify
    user_info_url = "https://api.spotify.com/v1/me"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    user_response = requests.get(user_info_url, headers=headers)
    if user_response.status_code != 200:
        return jsonify({"error": "Failed to fetch user data"}), 400

    user_data = user_response.json()
    
    # 3. Guardar en tu sistema (ejemplo básico)
    save_access_token(user_data['id'], access_token)
    
    # 4. Redirigir al frontend con los datos del usuario y token
    frontend_url = SPOTIFY_FRONTEND_REDIRECT_URI
    redirect_url = (
        f"{frontend_url}"
        f"?spotify_id={user_data['id']}"
        f"&display_name={user_data.get('display_name', '')}"
        f"&email={user_data.get('email', '')}"
        f"&access_token={encrypted_token}"
        f"&expires_in={token_response.json().get('expires_in')}"
    )
    return redirect(redirect_url)
