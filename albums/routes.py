from flask import Blueprint, jsonify, request
from utils.helpers import handle_response, convert_id, paginate_results
from logging_config import logger
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
    get_saved_albums_spotify, 
    get_new_releases_spotify, 
    get_recommended_albums_spotify
)

albums_blueprint = Blueprint('albums', __name__)

@albums_blueprint.route('/<collection_name>/', methods=['GET'])
@handle_response
def albums(collection_name, **params):
    if collection_name == 'spotify':
        user_id = params.get('user_id')
        if not user_id:
            raise ValueError("El parámetro 'user_id' es obligatorio cuando 'collection_name' es 'spotify'.")
        return get_saved_albums_spotify(**params)
    else:
        return get_all_albums(collection_name=collection_name, **params)
    
    #return {"formatted_albums": formatted_albums, "total": total}

@albums_blueprint.route('/<collection_name>/artist/<artist>', methods=['GET'])
@handle_response
def get_by_artist(collection_name, artist, **params):
    return get_albums_by_artist(
        collection_name=collection_name,
        artist=artist,
        **params
    )

@albums_blueprint.route('/<collection_name>/title/<title>', methods=['GET'])
@handle_response
def get_by_title(collection_name, title, **params):
    return get_albums_by_title(
        collection_name=collection_name,
        title=title,
        **params
    )

@albums_blueprint.route('/<collection_name>/format/<format>', methods=['GET'])
@handle_response
def get_by_format(collection_name, format, **params):
    return get_albums_by_format(
        collection_name=collection_name,
        format=format,
        **params
    )

@albums_blueprint.route('/<collection_name>/genres/<path:genres>', methods=['GET'])
@handle_response
def get_by_genres(collection_name, genres, **params):
    logger.info(f"Entrando en el endpoint de genres: {genres}")
    logger.info(f"Parámetros: {params}")
    return get_albums_by_genres(
        collection_name=collection_name,
        genres=genres, 
        **params
    )

@albums_blueprint.route('/<collection_name>/moods/<path:moods>', methods=['GET'])
@handle_response
def get_by_moods(collection_name, moods, **params):
    logger.info(f"Entrando en el endpoint de moods: {moods}")
    logger.info(f"Parámetros: {params}")
    return get_albums_by_moods(
        collection_name=collection_name,
        moods=moods, 
        **params
    )

@albums_blueprint.route('/<collection_name>/compilations/<path:compilations>', methods=['GET'])
@handle_response
def get_by_compilations(collection_name, compilations, **params):
    logger.info(f"Entrando en el endpoint de compilations: {compilations}")
    logger.info(f"Parámetros: {params}")
    return get_albums_by_compilations(
        collection_name=collection_name,
        compilations=compilations, 
        **params
    )

@albums_blueprint.route('/<collection_name>/country/<country>', methods=['GET'])
@handle_response
def get_by_country(collection_name, country, **params):
    return get_albums_by_country(
        collection_name=collection_name,
        country=country,
        **params
    )

@albums_blueprint.route('/<collection_name>/year/<year>', methods=['GET'])
@handle_response
def get_by_year(collection_name, year, **params):
    return get_albums_by_year(
        collection_name=collection_name,
        year=year, 
        **params
    )

@albums_blueprint.route('/<collection_name>/years/<start_year>/<end_year>', methods=['GET'])
@handle_response
def get_by_year_range(collection_name, start_year, end_year, **params):
    return get_albums_by_year_range(
        collection_name=collection_name,
        start_year=int(start_year),
        end_year=int(end_year),
        **params
    )

@albums_blueprint.route('/<collection_name>/decade/<int:decade>', methods=['GET'])
@handle_response
def get_by_decade(collection_name, decade, **params):
    return get_albums_by_decade(
        collection_name=collection_name,
        decade=decade,
        **params
    )

@albums_blueprint.route('/<collection_name>/releases/<days>', methods=['GET'])
@handle_response
def get_releases(collection_name, days, **params):
   return get_new_releases(
        collection_name=collection_name,
        days=days,
        **params
    )

@albums_blueprint.route('/<collection_name>/anniversary/<days>', methods=['GET'])
@handle_response
def get_anniversary(collection_name, days, **params):
    return get_anniversary_albums(
        collection_name=collection_name,
        days=int(days),
        **params
    )

@albums_blueprint.route('/<collection_name>/type/<tipo>', methods=['GET'])
@handle_response
def get_albums_by_type_route(collection_name, tipo, **params):
    return get_albums_by_type_service(
        collection_name=collection_name,
        tipo=tipo,
        **params
    )

@albums_blueprint.route('/spotify/me', methods=['GET'])
@handle_response
def get_saved_albums_from_spotify(**params):
    return get_saved_albums_spotify(
        **params
    )

@albums_blueprint.route('/spotify/new/<country>', methods=['GET'])
@handle_response
def get_new_releases_from_spotify(country, **params):
    return get_new_releases_spotify(
        country=country,
        **params
    )

@albums_blueprint.route('/spotify/recommended/<type>', methods=['GET'])
@handle_response
def get_recommended_albums_from_spotify(type, **params):
    return get_recommended_albums_spotify(
        type=type,
        **params
    )