from flask import Blueprint, redirect, request, session, current_app
from requests_oauthlib import OAuth1Session
from urllib.parse import parse_qs
from cryptography.fernet import Fernet
import os

from config import Config
from utils.constants import Collections, Parameters
from discogs.services import save_discogs_tokens

discogs_blueprint = Blueprint(Collections.DISCOGS, __name__)

# Configuración
FERNET_KEY = Config.ENCRYPTION_KEY
fernet = Fernet(FERNET_KEY)

DISCOGS_KEY = Config.DISCOGS_API_KEY
DISCOGS_SECRET = Config.DISCOGS_API_SECRET

DISCOGS_API_REDIRECT_URI = os.path.join(Config.API_URL, Config.API_VERSION, Collections.DISCOGS, Parameters.CALLBACK)
DISCOGS_FRONTEND_REDIRECT_URI = os.path.join(Config.FRONTEND_URL, Collections.DISCOGS)

# Login Discogs
@discogs_blueprint.route(f'/{Parameters.LOGIN}', methods=['GET'])
def discogs_auth():
    if not current_app.secret_key:
        raise RuntimeError("Flask secret_key no está configurada. Asegúrate de configurarla en tu aplicación.")
    try:
        oauth = OAuth1Session(
            client_key=DISCOGS_KEY,
            client_secret=DISCOGS_SECRET,
            callback_uri=DISCOGS_API_REDIRECT_URI
        )
        
        fetch_response = oauth.fetch_request_token('https://api.discogs.com/oauth/request_token')
        session['discogs_oauth_token'] = fetch_response.get('oauth_token')
        session['discogs_oauth_secret'] = fetch_response.get('oauth_token_secret')
        
        authorization_url = oauth.authorization_url('https://discogs.com/oauth/authorize')
        return redirect(authorization_url)
    
    except Exception as e:
        current_app.logger.error(f"Discogs auth error: {str(e)}")
        return redirect(f"{DISCOGS_FRONTEND_REDIRECT_URI}/error?code=500")

# Callback Discogs
@discogs_blueprint.route(f'/{Parameters.CALLBACK}', methods=['GET'])
def discogs_callback():
    if not current_app.secret_key:
        raise RuntimeError("Flask secret_key no está configurada. Asegúrate de configurarla en tu aplicación.")
    try:
        oauth_token = session.pop('discogs_oauth_token', None)
        oauth_secret = session.pop('discogs_oauth_secret', None)
        
        if not oauth_token or not oauth_secret:
            return redirect(f"{DISCOGS_FRONTEND_REDIRECT_URI}/error?code=invalid_token")
        
        oauth = OAuth1Session(
            client_key=DISCOGS_KEY,
            client_secret=DISCOGS_SECRET,
            resource_owner_key=oauth_token,
            resource_owner_secret=oauth_secret
        )
        
        oauth.parse_authorization_response(request.url)
        access_token_data = oauth.fetch_access_token('https://api.discogs.com/oauth/access_token')
        
        # Obtener datos del usuario
        user_response = oauth.get('https://api.discogs.com/oauth/identity')
        if user_response.status_code != 200:
            return redirect(f"{DISCOGS_FRONTEND_REDIRECT_URI}/error?code=user_fetch_failed")
        
        user_data = user_response.json()
        
        # Cifrar y guardar tokens
        encrypted_token = fernet.encrypt(
            f"{access_token_data['oauth_token']}:{access_token_data['oauth_token_secret']}".encode()
        ).decode()
        save_discogs_tokens(user_data['id'], encrypted_token)
        
        # Redirigir al frontend con datos del usuario
        redirect_url = (
            f"{DISCOGS_FRONTEND_REDIRECT_URI}"
            f"?discogs_id={user_data['id']}"
            f"&discogs_user={user_data['username']}"
        )
        return redirect(redirect_url)
    
    except Exception as e:
        current_app.logger.error(f"Discogs callback error: {str(e)}")
        return redirect(f"{DISCOGS_FRONTEND_REDIRECT_URI}/error?code=auth_failed")