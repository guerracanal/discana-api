from flask import Blueprint, redirect, request, session, current_app
from requests_oauthlib import OAuth1Session
from urllib.parse import parse_qs
import requests
from cryptography.fernet import Fernet
import os

discogs_bp = Blueprint('discogs', __name__, url_prefix='/api/v2/discogs')

# Configuración
DISCOGS_KEY = os.getenv('DISCOGS_API_KEY')
DISCOGS_SECRET = os.getenv('DISCOGS_API_SECRET')
FERNET_KEY = os.getenv('ENCRYPTION_KEY')
fernet = Fernet(FERNET_KEY)

@discogs_bp.route('/auth')
def discogs_auth():
    try:
        oauth = OAuth1Session(
            client_key=DISCOGS_KEY,
            client_secret=DISCOGS_SECRET,
            callback_uri=current_app.config['DISCOGS_CALLBACK_URL']
        )
        
        fetch_response = oauth.fetch_request_token(
            'https://api.discogs.com/oauth/request_token'
        )
        
        session['discogs_oauth_token'] = fetch_response.get('oauth_token')
        session['discogs_oauth_secret'] = fetch_response.get('oauth_token_secret')
        
        authorization_url = oauth.authorization_url(
            'https://discogs.com/oauth/authorize'
        )
        
        return redirect(authorization_url)
    
    except Exception as e:
        current_app.logger.error(f"Error Discogs auth: {str(e)}")
        return redirect(f"{current_app.config['FRONTEND_URL']}/error?code=500")

@discogs_bp.route('/callback')
def discogs_callback():
    try:
        oauth_token = session.pop('discogs_oauth_token', None)
        oauth_secret = session.pop('discogs_oauth_secret', None)
        
        oauth = OAuth1Session(
            client_key=DISCOGS_KEY,
            client_secret=DISCOGS_SECRET,
            resource_owner_key=oauth_token,
            resource_owner_secret=oauth_secret
        )
        
        oauth.parse_authorization_response(request.url)
        access_token_data = oauth.fetch_access_token(
            'https://api.discogs.com/oauth/access_token'
        )
        
        # Obtener datos del usuario
        user_response = oauth.get('https://api.discogs.com/oauth/identity')
        user_data = user_response.json()
        
        # Cifrar y almacenar tokens
        encrypted_token = fernet.encrypt(
            f"{access_token_data['oauth_token']}:{access_token_data['oauth_token_secret']}".encode()
        )
        
        # Guardar en base de datos (ejemplo simplificado)
        # user = User.update_discogs_tokens(user_data['id'], encrypted_token)
        
        frontend_redirect = (
            f"{current_app.config['FRONTEND_URL']}"
            f"?discogs_id={user_data['id']}"
            f"&discogs_user={user_data['username']}"
        )
        
        return redirect(frontend_redirect)
    
    except Exception as e:
        current_app.logger.error(f"Discogs callback error: {str(e)}")
        return redirect(f"{current_app.config['FRONTEND_URL']}/error?code=auth_failed")