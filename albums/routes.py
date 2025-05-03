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
    get_albums_by_type_service,
    get_album_by_title_and_artist,
    get_album_by_spotify_id,
    get_album_by_db_id,
    get_album_by_mbid,
    get_album_by_discogs_id,
    get_album_details
)
from spotify.services import (
    get_albums_spotify,
    get_saved_albums_spotify, 
    get_new_releases_spotify, 
)
from discogs.services import (
    get_user_collection,
    get_new_releases_discogs
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

# Get Album Details by ID or Title and Artist
@albums_blueprint.route(f'/{ParametersValues.COLLECTION}/{Routes.DETAIL}/', methods=['GET'])
@log_route_info
def get_album_detail(collection_name):
    album_id = request.args.get('id')
    title = request.args.get('title')
    artist = request.args.get('artist')
    spotify_user_id = request.args.get('spotify_user_id')
    discogs_user_id = request.args.get('discogs_user_id')
    lastfm_user_id = request.args.get('lastfm_user_id')
    
    if album_id:
        return get_album_by_id(collection_name=collection_name, album_id=album_id)
    elif title and artist:
        return get_album_by_title_and_artist(
            collection_name=collection_name,
            title=title,
            artist=artist,
            spotify_user_id=spotify_user_id,
            discogs_user_id=discogs_user_id,
            lastfm_user_id=lastfm_user_id
        )
    else:
        return jsonify({"error": "Provide either 'id' or both 'title' and 'artist'"}), 400

# Get Album Details by Spotify ID
@albums_blueprint.route(f'/{ParametersValues.COLLECTION}/{Routes.DETAIL}/spotify/', methods=['GET'])
@log_route_info
def get_album_detail_by_spotify_id(collection_name):
    spotify_id = request.args.get('spotify_id')
    spotify_user_id = request.args.get('spotify_user_id')
    discogs_user_id = request.args.get('discogs_user_id')
    lastfm_user_id = request.args.get('lastfm_user_id')

    if not spotify_id:
        return jsonify({"error": "Provide 'spotify_id'"}), 400

    return get_album_by_spotify_id(
        spotify_id=spotify_id,
        collection_name=collection_name,
        spotify_user_id=spotify_user_id,
        discogs_user_id=discogs_user_id,
        lastfm_user_id=lastfm_user_id
    )

# Get Album Details by Mongo ID
@albums_blueprint.route(f'/{ParametersValues.COLLECTION}/{Routes.DETAIL}/db/', methods=['GET'])
@log_route_info
def get_album_detail_by_mongo_id(collection_name):
    mongo_id = request.args.get('mongo_id')
    spotify_user_id = request.args.get('spotify_user_id')
    discogs_user_id = request.args.get('discogs_user_id')
    lastfm_user_id = request.args.get('lastfm_user_id')

    if not mongo_id:
        return jsonify({"error": "Provide 'mongo_id'"}), 400

    return get_album_by_db_id(
        mongo_id=mongo_id,
        collection_name=collection_name,
        spotify_user_id=spotify_user_id,
        discogs_user_id=discogs_user_id,
        lastfm_user_id=lastfm_user_id
    )

# Get Album Details by MBID
@albums_blueprint.route(f'/{ParametersValues.COLLECTION}/{Routes.DETAIL}/mbid/', methods=['GET'])
@log_route_info
def get_album_detail_by_mbid(collection_name):
    mbid = request.args.get('mbid')
    spotify_user_id = request.args.get('spotify_user_id')
    discogs_user_id = request.args.get('discogs_user_id')
    lastfm_user_id = request.args.get('lastfm_user_id')

    if not mbid:
        return jsonify({"error": "Provide 'mbid'"}), 400

    return get_album_by_mbid(
        mbid=mbid,
        collection_name=collection_name,
        spotify_user_id=spotify_user_id,
        discogs_user_id=discogs_user_id,
        lastfm_user_id=lastfm_user_id
    )

# Get Album Details by Discogs ID
@albums_blueprint.route(f'/{ParametersValues.COLLECTION}/{Routes.DETAIL}/discogs/', methods=['GET'])
@log_route_info
def get_album_detail_by_discogs_id(collection_name):
    discogs_id = request.args.get('discogs_id')
    spotify_user_id = request.args.get('spotify_user_id')
    discogs_user_id = request.args.get('discogs_user_id')
    lastfm_user_id = request.args.get('lastfm_user_id')

    if not discogs_id:
        return jsonify({"error": "Provide 'discogs_id'"}), 400

    return get_album_by_discogs_id(
        discogs_id=discogs_id,
        collection_name=collection_name,
        spotify_user_id=spotify_user_id,
        discogs_user_id=discogs_user_id,
        lastfm_user_id=lastfm_user_id
    )

# Get Album Details (prioritizing IDs)
@albums_blueprint.route(f'/{ParametersValues.COLLECTION}/{Routes.DETAIL}/{Routes.ALL}/', methods=['GET'])
@log_route_info
def get_album_details_route(collection_name):
    db_id = request.args.get('db_id')
    spotify_id = request.args.get('spotify_id')
    mbid = request.args.get('mbid')
    discogs_id = request.args.get('discogs_id')
    title = request.args.get('title')
    artist = request.args.get('artist')
    spotify_user_id = request.args.get('spotify_user_id')
    discogs_user_id = request.args.get('discogs_user_id')
    lastfm_user_id = request.args.get('lastfm_user_id')

    if not (db_id or spotify_id or mbid or discogs_id or (title and artist)):
        return jsonify({"error": "Provide at least one ID (db_id, spotify_id, mbid, discogs_id) or both 'title' and 'artist'"}), 400

    return get_album_details(
        collection_name=collection_name,
        db_id=db_id,
        spotify_id=spotify_id,
        mbid=mbid,
        discogs_id=discogs_id,
        title=title,
        artist=artist,
        spotify_user_id=spotify_user_id,
        discogs_user_id=discogs_user_id,
        lastfm_user_id=lastfm_user_id
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

#####################
# Discogs ENDPOINTS #
#####################

# Get User Collection from Discogs
@albums_blueprint.route(f'/{Collections.DISCOGS}/{Parameters.ALBUMS}/', methods=['GET'])
@handle_response
@log_route_info
def get_albums_from_discogs(**params):
    return get_user_collection(
        **params
    )

# Get New Releases from Discogs
@albums_blueprint.route(f'/{Collections.DISCOGS}/{Parameters.NEW}/', methods=['GET'])
@handle_response
@log_route_info
def get_new_from_discogs(**params):
    return get_new_releases_discogs(
        **params
    )



