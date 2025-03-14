from flask import Blueprint, jsonify, request
from utils.helpers import handle_response

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
from utils.helpers import convert_id, paginate_results
import logging

albums_blueprint = Blueprint('albums', __name__)

@albums_blueprint.route('/', methods=['GET'])
@handle_response
def albums(**params):
    return get_all_albums(**params)

@albums_blueprint.route('/artist/<artist>', methods=['GET'])
@handle_response
def get_by_artist(artist, **params):
    return get_albums_by_artist(
        artist=artist,
        **params
    )

@albums_blueprint.route('/title/<title>', methods=['GET'])
@handle_response
def get_by_title(title, **params):
    return get_albums_by_title(
        title=title,
        **params
    )

@albums_blueprint.route('/format/<format>', methods=['GET'])
@handle_response
def get_by_format(format, **params):
    return get_albums_by_format(
        format=format,
        **params
    )

@albums_blueprint.route('/genres/<path:genres>', methods=['GET'])
@handle_response
def get_by_genres(genres, **params):
    logging.info(f"Entrando en el endpoint de genres: {genres}")
    logging.info(f"Parámetros: {params}")
    return get_albums_by_genres(
        genres=genres, 
        **params
    )

@albums_blueprint.route('/moods/<path:moods>', methods=['GET'])
@handle_response
def get_by_moods(moods, **params):
    logging.info(f"Entrando en el endpoint de moods: {moods}")
    logging.info(f"Parámetros: {params}")
    return get_albums_by_moods(
        moods=moods, 
        **params
    )

@albums_blueprint.route('/compilations/<path:compilations>', methods=['GET'])
@handle_response
def get_by_compilations(compilations, **params):
    logging.info(f"Entrando en el endpoint de compilations: {compilations}")
    logging.info(f"Parámetros: {params}")
    return get_albums_by_compilations(
        compilations=compilations, 
        **params
    )

@albums_blueprint.route('/country/<country>', methods=['GET'])
@handle_response
def get_by_country(country, **params):
    return get_albums_by_country(
        country=country,
        **params
    )


# Endpoint para obtener discos por año de lanzamiento
@albums_blueprint.route('/year/<year>', methods=['GET'])
@handle_response
def get_by_year(year, **params):
    return get_albums_by_year(
        year=year, 
        **params
    )


@albums_blueprint.route('/years/<start_year>/<end_year>', methods=['GET'])
@handle_response
def get_by_year_range(start_year, end_year, **params):
    return get_albums_by_year_range(
        start_year=int(start_year),
        end_year=int(end_year),
        **params
    )


@albums_blueprint.route('/decade/<int:decade>', methods=['GET'])
@handle_response
def get_by_decade(decade, **params):
    return get_albums_by_decade(
        decade=decade,
        **params
    )

@albums_blueprint.route('/releases/<days>', methods=['GET'])
@handle_response
def get_releases(days, **params):
   return get_new_releases(
        days=days,
        **params
    )

@albums_blueprint.route('/anniversary/<days>', methods=['GET'])
@handle_response
def get_anniversary(days, **params):
    return get_anniversary_albums(
        days=int(days),
        **params
    )

@albums_blueprint.route('/type/<tipo>', methods=['GET'])
@handle_response
def get_albums_by_type_route(tipo, **params):
    return get_albums_by_type_service(
        tipo=tipo,
        **params
    )
