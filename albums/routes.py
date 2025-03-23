from flask import Blueprint, jsonify, request
from lastfm.services import get_user_top_albums
from utils.constants import Collections, Parameters, ParametersValues, Routes
from utils.helpers import handle_response, log_route_info
from albums.services import (
    get_all_albums, 
    get_albums_by_artist,
    get_albums_by_title, 
    get_albums_by_country, 
    get_albums_by_genres, 
    get_albums_by_moods, 
    get_albums_by_format, 
    get_albums_by_compilations,
    get_albums_by_year, 
    get_albums_by_year_range,
    get_albums_by_decade,
    get_new_releases,
    get_anniversary_albums,
    get_albums_by_type_service
)
from spotify.services import (
    get_albums_spotify,
    get_saved_albums_spotify, 
    get_new_releases_spotify, 
)

albums_blueprint = Blueprint(Parameters.ALBUMS, __name__)

@albums_blueprint.route(f'/{ParametersValues.COLLECTION}/', methods=['GET'])
@handle_response
@log_route_info
def albums(collection_name, **params):
    if collection_name == Collections.SPOTIFY:
        return get_saved_albums_from_spotify(**params)
    else:
        return get_all_albums(collection_name=collection_name, **params)

# GET Albums by Artist
@albums_blueprint.route(f'/{ParametersValues.COLLECTION}/{Routes.ARTIST}/', methods=['GET'])
@handle_response
@log_route_info
def get_by_artist(collection_name, artist, **params):
    return get_albums_by_artist(
        collection_name=collection_name,
        artist=artist,
        **params
    )

# Get Albums by Title
@albums_blueprint.route(f'/{ParametersValues.COLLECTION}/{Routes.TITLE}/', methods=['GET'])
@handle_response
@log_route_info
def get_by_title(collection_name, title, **params):
    return get_albums_by_title(
        collection_name=collection_name,
        title=title,
        **params
    )

# Get Albums by Format
@albums_blueprint.route(f'/{ParametersValues.COLLECTION}/{Routes.FORMAT}/', methods=['GET'])
@handle_response
@log_route_info
def get_by_format(collection_name, format, **params):
    return get_albums_by_format(
        collection_name=collection_name,
        format=format,
        **params
    )

# Get Albums by Genres
@albums_blueprint.route(f'/{ParametersValues.COLLECTION}/{Routes.GENRES}/', methods=['GET'])
@handle_response
@log_route_info
def get_by_genres(collection_name, genres, **params):
    return get_albums_by_genres(
        collection_name=collection_name,
        genres=genres, 
        **params
    )

# Get Albums by Moods
@albums_blueprint.route(f'/{ParametersValues.COLLECTION}/{Routes.MOODS}/', methods=['GET'])
@handle_response
@log_route_info
def get_by_moods(collection_name, moods, **params):
    return get_albums_by_moods(
        collection_name=collection_name,
        moods=moods, 
        **params
    )

#Get Albums by Compilations
@albums_blueprint.route(f'/{ParametersValues.COLLECTION}/{Routes.COMPILATIONS}/', methods=['GET'])
@handle_response
@log_route_info
def get_by_compilations(collection_name, compilations, **params):
    return get_albums_by_compilations(
        collection_name=collection_name,
        compilations=compilations, 
        **params
    )

#Get Albums by Country
@albums_blueprint.route(f'/{ParametersValues.COLLECTION}/{Routes.COUNTRY}/', methods=['GET'])
@handle_response
@log_route_info
def get_by_country(collection_name, country, **params):
    return get_albums_by_country(
        collection_name=collection_name,
        country=country,
        **params
    )

# Get Albums by Year
@albums_blueprint.route(f'/{ParametersValues.COLLECTION}/{Routes.YEAR}/', methods=['GET'])
@handle_response
@log_route_info
def get_by_year(collection_name, year, **params):
    return get_albums_by_year(
        collection_name=collection_name,
        year=year, 
        **params
    )

# Get Albums by Year Range
@albums_blueprint.route(f'/{ParametersValues.COLLECTION}/{Routes.YEARS}/', methods=['GET'])
@handle_response
@log_route_info
def get_by_year_range(collection_name, start_year, end_year, **params):
    return get_albums_by_year_range(
        collection_name=collection_name,
        start_year=int(start_year),
        end_year=int(end_year),
        **params
    )

# Get Albums by Decade
@albums_blueprint.route(f'/{ParametersValues.COLLECTION}/{Routes.DECADE}/', methods=['GET'])
@handle_response
@log_route_info
def get_by_decade(collection_name, decade, **params):
    return get_albums_by_decade(
        collection_name=collection_name,
        decade=decade,
        **params
    )

# Get New Releases
@albums_blueprint.route(f'/{ParametersValues.COLLECTION}/{Routes.RELEASE}/', methods=['GET'])
@handle_response
@log_route_info
def get_releases(collection_name, days, **params):
   return get_new_releases(
        collection_name=collection_name,
        days=days,
        **params
    )

# Get Anniversary Albums
@albums_blueprint.route(f'/{ParametersValues.COLLECTION}/{Routes.ANNIVERSARY}/', methods=['GET'])
@handle_response
@log_route_info
def get_anniversary(collection_name, days, **params):
    return get_anniversary_albums(
        collection_name=collection_name,
        days=int(days),
        **params
    )

# Get Albums by Type
@albums_blueprint.route(f'/{ParametersValues.COLLECTION}/{Routes.TYPE}/', methods=['GET'])
@handle_response
@log_route_info
def get_albums_by_type_route(collection_name, type, **params):
    return get_albums_by_type_service(
        collection_name=collection_name,
        type=type,
        **params
    )

#####################
# SPOTIFY ENDPOINTS #
#####################

# Get Saved Albums from Spotify
@albums_blueprint.route(f'/{Collections.SPOTIFY}/{Parameters.ME}/', methods=['GET'])
@handle_response
@log_route_info
def get_saved_albums_from_spotify(**params):
    return get_saved_albums_spotify(
        **params
    )

# Get New Releases from Spotify
@albums_blueprint.route(f'/{Collections.SPOTIFY}/{Parameters.NEW}/{ParametersValues.COUNTRY}', methods=['GET'])
@handle_response
@log_route_info
def get_new_releases_from_spotify(country, **params):
    return get_new_releases_spotify(
        country=country,
        **params
    )

# Get Albums from Spotify
@albums_blueprint.route(f'/{Collections.SPOTIFY}/{Parameters.ALBUMS}/{ParametersValues.TYPE}', methods=['GET'])
@handle_response
@log_route_info
def get_albums_from_spotify(type, **params):
    return get_albums_spotify(
        type=type,
        **params
    )

#####################
# Last.FM ENDPOINTS #
#####################

# Get Saved Albums from Spotify
@albums_blueprint.route(f'/{Collections.LASTFM}/{Parameters.ME}/', methods=['GET'])
@handle_response
@log_route_info
def get_user_top_albums_from_lastfm(**params):
    return get_user_top_albums(
        **params
    )