from flask import Blueprint, redirect, request, current_app
import hashlib
import requests
import os

from config import Config
from lastfm.services import save_lastfm_session
from utils.constants import Collections, Parameters

lastfm_blueprint = Blueprint(Collections.LASTFM, __name__)

LASTFM_KEY = Config.LASTFM_API_KEY
LASTFM_SECRET = Config.LASTFM_API_SECRET

LASTFM_API_REDIRECT_URI = os.path.join(Config.API_URL, Config.API_VERSION, Collections.LASTFM, Parameters.CALLBACK)
LASTFM_FRONTEND_REDIRECT_URI = os.path.join(Config.FRONTEND_URL, Collections.LASTFM)

# Login Last.fm
@lastfm_blueprint.route(f'/{Parameters.LOGIN}', methods=['GET'])
def lastfm_auth():
    try:
        auth_url = (
            f"https://www.last.fm/api/auth/"
            f"?api_key={LASTFM_KEY}"
            f"&cb={LASTFM_API_REDIRECT_URI}"
        )
        return redirect(auth_url)
    
    except Exception as e:
        current_app.logger.error(f"Last.fm auth error: {str(e)}")
        return redirect(f"{LASTFM_FRONTEND_REDIRECT_URI}/error?code=500")

# Callback Last.fm
@lastfm_blueprint.route(f'/{Parameters.CALLBACK}', methods=['GET'])
def lastfm_callback():
    try:
        token = request.args.get('token')
        if not token:
            return redirect(f"{LASTFM_FRONTEND_REDIRECT_URI}/error?code=invalid_token")
        
        # Generar firma API
        api_sig = hashlib.md5(
            f"api_key{LASTFM_KEY}"
            f"methodauth.getSession"
            f"token{token}"
            f"{LASTFM_SECRET}".encode()
        ).hexdigest()
        
        # Obtener sesión
        response = requests.get(
            "https://ws.audioscrobbler.com/2.0/",
            params={
                'method': 'auth.getSession',
                'api_key': LASTFM_KEY,
                'token': token,
                'api_sig': api_sig,
                'format': 'json'
            }
        )
        
        data = response.json()
        if 'error' in data:
            current_app.logger.error(f"Last.fm API error: {data['message']}")
            return redirect(f"{LASTFM_FRONTEND_REDIRECT_URI}/error?code=lastfm_error")
        
        session_key = data['session']['key']
        username = data['session']['name']
        
        # Guardar en base de datos (ejemplo)
        # user = User.update_lastfm_session(username, session_key)
        
    
        # 3. Guardar en tu sistema (ejemplo básico)
        save_lastfm_session(session_key, username)

        return redirect(f"{LASTFM_FRONTEND_REDIRECT_URI}?lastfm_user={username}")
    
    except Exception as e:
        current_app.logger.error(f"Last.fm callback error: {str(e)}")
        return redirect(f"{LASTFM_FRONTEND_REDIRECT_URI}/error?code=auth_failed")