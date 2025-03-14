from flask import Blueprint, jsonify, request
from albums_pendientes.services import (
    get_all_albums_ptes, 
    get_albums_ptes_by_artist,
    get_albums_ptes_by_title, 
    get_albums_ptes_by_country, 
    get_albums_ptes_by_genre, 
    get_albums_ptes_by_subgenres, 
    get_albums_ptes_by_mood, 
    get_albums_ptes_by_format, 
    get_albums_ptes_by_compilations,
    get_albums_ptes_by_tracks,
    get_albums_ptes_by_duration,
    get_albums_ptes_by_year, 
    get_albums_ptes_by_year_range,
    get_albums_ptes_by_decade,
    get_albums_ptes_by_any_genres,
    get_albums_ptes_by_all_genres,
    get_albums_ptes_by_any_moods,
    get_albums_ptes_by_all_moods,
    get_albums_ptes_by_any_compilations,
    get_albums_ptes_by_all_compilations,
    get_filtered_albums_ptes,
    get_new_releases,
    get_anniversary_albums_ptes

)
from utils.helpers import convert_id, paginate_results
import logging

albums_ptes_blueprint = Blueprint('albums_ptes', __name__)

@albums_ptes_blueprint.route('/', methods=['GET'])
def albums_ptes():
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    pendientes = get_all_albums_ptes(rnd=True)
    paginated_albums_ptes = paginate_results(pendientes, page, limit)
    return jsonify(paginated_albums_ptes)

@albums_ptes_blueprint.route('/artist/<artist>', methods=['GET'])
def get_by_artist(artist):
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        pendientes = get_albums_ptes_by_artist(artist, rnd=True)
        logging.info(f"Entrando en el endpoint de artista: {artist}")
        logging.info(f"Registros encontrados: {len(pendientes)}")
        paginated_albums_ptes = paginate_results(pendientes, page, limit)
        logging.info(f"Registros mostrados: {len(paginated_albums_ptes)}")
        return jsonify([convert_id(album) for album in paginated_albums_ptes])
    except Exception as e:
        logging.error(f"Error al obtener álbumes por artista: {e}")
        return jsonify({"error": f"Error al obtener álbumes por artista: {str(e)}"}), 500
    
@albums_ptes_blueprint.route('/title/<title>', methods=['GET'])
def get_by_title(title):
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        pendientes = get_albums_ptes_by_title(title, rnd=True)
        logging.info(f"Entrando en el endpoint de title: {title}")
        logging.info(f"Registros encontrados: {len(pendientes)}")
        paginated_albums_ptes = paginate_results(pendientes, page, limit)
        logging.info(f"Registros mostrados: {len(paginated_albums_ptes)}")
        return jsonify([convert_id(album) for album in paginated_albums_ptes])
    except Exception as e:
        logging.error(f"Error al obtener álbumes por title: {e}")
        return jsonify({"error": f"Error al obtener álbumes por title: {str(e)}"}), 500

@albums_ptes_blueprint.route('/format/<format>', methods=['GET'])
def get_by_format(format):
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    pendientes_cursor = get_albums_ptes_by_format(format, rnd=True)
    pendientes = list(pendientes_cursor)  # Convertimos el cursor a lista
    logging.info(f"Entrando en el endpoint de formato: {format}")
    logging.info(f"Registros encontrados: {len(pendientes)}")
    paginated_albums_ptes = paginate_results(pendientes, page, limit)
    logging.info(f"Registros mostrados: {len(paginated_albums_ptes)}")
    return jsonify([convert_id(album) for album in paginated_albums_ptes])  # Usamos paginated_albums_ptes

@albums_ptes_blueprint.route('/genre/<genre>', methods=['GET'])
def get_by_genre(genre):
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    pendientes_cursor = get_albums_ptes_by_genre(genre, rnd=True)
    pendientes = list(pendientes_cursor)  # Convertimos el cursor a lista
    logging.info(f"Entrando en el endpoint de genre: {genre}")
    logging.info(f"Registros encontrados: {len(pendientes)}")
    paginated_albums_ptes = paginate_results(pendientes, page, limit)
    logging.info(f"Registros mostrados: {len(paginated_albums_ptes)}")
    return jsonify([convert_id(album) for album in paginated_albums_ptes])  # Usamos paginated_albums_ptes

@albums_ptes_blueprint.route('/subgenres/<subgenres>', methods=['GET'])
def get_by_subgenre(subgenres):
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    pendientes_cursor = get_albums_ptes_by_subgenres(subgenres, rnd=True)
    pendientes = list(pendientes_cursor)  # Convertimos el cursor a lista
    logging.info(f"Entrando en el endpoint de subgenres: {subgenres}")
    logging.info(f"Registros encontrados: {len(pendientes)}")
    paginated_albums_ptes = paginate_results(pendientes, page, limit)
    logging.info(f"Registros mostrados: {len(paginated_albums_ptes)}")
    return jsonify([convert_id(album) for album in paginated_albums_ptes])  # Usamos paginated_albums_ptes

@albums_ptes_blueprint.route('/mood/<mood>', methods=['GET'])
def get_by_mood(mood):
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    pendientes_cursor = get_albums_ptes_by_mood(mood, rnd=True)
    pendientes = list(pendientes_cursor)  # Convertimos el cursor a lista
    logging.info(f"Entrando en el endpoint de mood: {mood}")
    logging.info(f"Registros encontrados: {len(pendientes)}")
    paginated_albums_ptes = paginate_results(pendientes, page, limit)
    logging.info(f"Registros mostrados: {len(paginated_albums_ptes)}")
    return jsonify([convert_id(album) for album in paginated_albums_ptes])  # Usamos paginated_albums_ptes

@albums_ptes_blueprint.route('/compilations/<compilations>', methods=['GET'])
def get_by_compilations(compilations):
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    pendientes_cursor = get_albums_ptes_by_compilations(compilations, rnd=True)
    pendientes = list(pendientes_cursor)  # Convertimos el cursor a lista
    logging.info(f"Entrando en el endpoint de compilations: {compilations}")
    logging.info(f"Registros encontrados: {len(pendientes)}")
    paginated_albums_ptes = paginate_results(pendientes, page, limit)
    logging.info(f"Registros mostrados: {len(paginated_albums_ptes)}")
    return jsonify([convert_id(album) for album in paginated_albums_ptes])  # Usamos paginated_albums_ptes

@albums_ptes_blueprint.route('/country/<country>', methods=['GET'])
def get_by_country(country):
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        pendientes = get_albums_ptes_by_country(country, rnd=True)
        logging.info(f"Entrando en el endpoint de country: {country}")
        logging.info(f"Registros encontrados: {len(pendientes)}")
        paginated_albums_ptes = paginate_results(pendientes, page, limit)
        logging.info(f"Registros mostrados: {len(paginated_albums_ptes)}")
        return jsonify([convert_id(album) for album in paginated_albums_ptes])
    except Exception as e:
        logging.error(f"Error al obtener álbumes por country: {e}")
        return jsonify({"error": f"Error al obtener álbumes por country: {str(e)}"}), 500

# Endpoint para obtener álbumes por duración (con un rango de duración)
@albums_ptes_blueprint.route('/duration/<min_duration>/<max_duration>', methods=['GET'])
@albums_ptes_blueprint.route('/duration/<max_duration>', methods=['GET'])  # Caso de solo máximo
def get_by_duration(min_duration=None, max_duration=None):
    try:
        # Si solo se recibe uno, lo convertimos a int. Si ambos, convertimos ambos
        min_duration = int(min_duration) if min_duration is not None else None
        max_duration = int(max_duration) if max_duration is not None else None

        # Recuperar los parámetros de paginación
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))

        # Llamar a la función de servicio para obtener los álbumes
        pendientes = get_albums_ptes_by_duration(min_duration, max_duration, rnd=True)

        # Log para ver los resultados
        logging.info(f"Discos encontrados con duración entre {min_duration if min_duration else 'sin límite inferior'} y {max_duration if max_duration else 'sin límite superior'} minutos: {len(pendientes)}")

        # Aplicar la paginación
        paginated_albums_ptes = paginate_results(pendientes, page, limit)
        logging.info(f"Registros mostrados: {len(paginated_albums_ptes)}")

        # Devolver los resultados como JSON
        return jsonify([convert_id(album) for album in paginated_albums_ptes])

    except Exception as e:
        logging.error(f"Error al obtener álbumes por duración: {e}")
        return jsonify({"error": f"Error al obtener álbumes por duración: {str(e)}"}), 500

# Endpoint para obtener álbumes por número de pistas (con un rango de pistas)
@albums_ptes_blueprint.route('/tracks/<min_tracks>/<max_tracks>', methods=['GET'])
@albums_ptes_blueprint.route('/tracks/<max_tracks>', methods=['GET'])  # Caso de solo máximo
def get_by_tracks(min_tracks=None, max_tracks=None):
    try:
        # Si solo se recibe uno, lo convertimos a int. Si ambos, convertimos ambos
        min_tracks = int(min_tracks) if min_tracks is not None else None
        max_tracks = int(max_tracks) if max_tracks is not None else None

        # Recuperar los parámetros de paginación
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))

        # Llamar a la función de servicio para obtener los álbumes
        pendientes = get_albums_ptes_by_tracks(min_tracks, max_tracks, rnd=True)

        # Log para ver los resultados
        logging.info(f"Discos encontrados con pistas entre {min_tracks if min_tracks else 'sin límite inferior'} y {max_tracks if max_tracks else 'sin límite superior'}: {len(pendientes)}")

        # Aplicar la paginación
        paginated_albums_ptes = paginate_results(pendientes, page, limit)
        logging.info(f"Registros mostrados: {len(paginated_albums_ptes)}")

        # Devolver los resultados como JSON
        return jsonify([convert_id(album) for album in paginated_albums_ptes])

    except Exception as e:
        logging.error(f"Error al obtener álbumes por pistas: {e}")
        return jsonify({"error": f"Error al obtener álbumes por pistas: {str(e)}"}), 500



# Endpoint para obtener discos por año de lanzamiento
@albums_ptes_blueprint.route('/year/<year>', methods=['GET'])
def get_by_year(year):
    try:
        # Recuperar los parámetros de paginación
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))

        # Llamar a la función de servicio para obtener los álbumes
        pendientes = get_albums_ptes_by_year(year, rnd=True)

        # Log para ver los resultados
        logging.info(f"Discos encontrados con año {year}: {len(pendientes)}")

        # Aplicar la paginación
        paginated_albums_ptes = paginate_results(pendientes, page, limit)
        logging.info(f"Registros mostrados: {len(paginated_albums_ptes)}")

        # Devolver los resultados como JSON
        return jsonify([convert_id(album) for album in paginated_albums_ptes])

    except Exception as e:
        logging.error(f"Error al obtener álbumes por año: {e}")
        return jsonify({"error": f"Error al obtener álbumes por año: {str(e)}"}), 500

# Endpoint para obtener discos por rango de años
@albums_ptes_blueprint.route('/years/<start_year>/<end_year>', methods=['GET'])
def get_by_year_range(start_year, end_year):
    try:
        # Recuperar los parámetros de paginación
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))

        # Llamar a la función de servicio para obtener los álbumes
        pendientes = get_albums_ptes_by_year_range(start_year, end_year, rnd=True)

        # Log para ver los resultados
        logging.info(f"Discos encontrados con año entre {start_year} y {end_year}: {len(pendientes)}")

        # Aplicar la paginación
        paginated_albums_ptes = paginate_results(pendientes, page, limit)
        logging.info(f"Registros mostrados: {len(paginated_albums_ptes)}")

        # Devolver los resultados como JSON
        return jsonify([convert_id(album) for album in paginated_albums_ptes])

    except Exception as e:
        logging.error(f"Error al obtener álbumes por rango de años: {e}")
        return jsonify({"error": f"Error al obtener álbumes por rango de años: {str(e)}"}), 500

@albums_ptes_blueprint.route('/decade/<int:decade>', methods=['GET'])
def get_by_decade(decade):
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))

        pendientes = get_albums_ptes_by_decade(decade, rnd=True)
        logging.info(f"Discos encontrados en la década de {decade}: {len(pendientes)}")

        paginated_albums_ptes = paginate_results(pendientes, page, limit)
        logging.info(f"Registros mostrados: {len(paginated_albums_ptes)}")

        return jsonify([convert_id(album) for album in paginated_albums_ptes])
    except Exception as e:
        logging.error(f"Error al obtener álbumes por década: {e}")
        return jsonify({"error": f"Error al obtener álbumes por década: {str(e)}"}), 500


@albums_ptes_blueprint.route('/any-genres/<path:genres>', methods=['GET'])
def get_by_any_genres(genres):
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))

        genres_list = genres.split("/")  # Convertimos la cadena en una lista
        pendientes = get_albums_ptes_by_any_genres(genres_list, rnd=True)
        logging.info(f"Discos encontrados con géneros {genres_list}: {len(pendientes)}")

        paginated_albums_ptes = paginate_results(pendientes, page, limit)
        logging.info(f"Registros mostrados: {len(paginated_albums_ptes)}")

        return jsonify([convert_id(album) for album in paginated_albums_ptes])
    except Exception as e:
        logging.error(f"Error al obtener álbumes por géneros: {e}")
        return jsonify({"error": f"Error al obtener álbumes por géneros: {str(e)}"}), 500

@albums_ptes_blueprint.route('/all-genres/<path:genres>', methods=['GET'])
def get_by_all_genres(genres):
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))

        genres_list = genres.split("/")
        pendientes = get_albums_ptes_by_all_genres(genres_list, rnd=True)
        logging.info(f"Discos encontrados con todos los géneros {genres_list}: {len(pendientes)}")

        paginated_albums_ptes = paginate_results(pendientes, page, limit)
        logging.info(f"Registros mostrados: {len(paginated_albums_ptes)}")

        return jsonify([convert_id(album) for album in paginated_albums_ptes])
    except Exception as e:
        logging.error(f"Error al obtener álbumes con todos los géneros: {e}")
        return jsonify({"error": f"Error al obtener álbumes con todos los géneros: {str(e)}"}), 500


@albums_ptes_blueprint.route('/any-moods/<path:moods>', methods=['GET'])
def get_by_any_moods(moods):
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))

        moods_list = moods.split("/")  # Convertimos la cadena en una lista
        pendientes = get_albums_ptes_by_any_moods(moods_list, rnd=True)
        logging.info(f"Discos encontrados con moods {moods_list}: {len(pendientes)}")

        paginated_albums_ptes = paginate_results(pendientes, page, limit)
        logging.info(f"Registros mostrados: {len(paginated_albums_ptes)}")

        return jsonify([convert_id(album) for album in paginated_albums_ptes])
    except Exception as e:
        logging.error(f"Error al obtener álbumes por moods: {e}")
        return jsonify({"error": f"Error al obtener álbumes por moods: {str(e)}"}), 500

@albums_ptes_blueprint.route('/all-moods/<path:moods>', methods=['GET'])
def get_by_all_moods(moods):
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))

        moods_list = moods.split("/")
        pendientes = get_albums_ptes_by_all_moods(moods_list, rnd=True)
        logging.info(f"Discos encontrados con todos los moods {moods_list}: {len(pendientes)}")

        paginated_albums_ptes = paginate_results(pendientes, page, limit)
        logging.info(f"Registros mostrados: {len(paginated_albums_ptes)}")

        return jsonify([convert_id(album) for album in paginated_albums_ptes])
    except Exception as e:
        logging.error(f"Error al obtener álbumes con todos los moods: {e}")
        return jsonify({"error": f"Error al obtener álbumes con todos los moods: {str(e)}"}), 500


@albums_ptes_blueprint.route('/any-compilations/<path:compilations>', methods=['GET'])
def get_by_any_compilations(compilations):
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))

        compilations_list = compilations.split("/")  # Convertimos la cadena en una lista
        pendientes = get_albums_ptes_by_any_compilations(compilations_list, rnd=True)
        logging.info(f"Discos encontrados con compilations {compilations_list}: {len(pendientes)}")

        paginated_albums_ptes = paginate_results(pendientes, page, limit)
        logging.info(f"Registros mostrados: {len(paginated_albums_ptes)}")

        return jsonify([convert_id(album) for album in paginated_albums_ptes])
    except Exception as e:
        logging.error(f"Error al obtener álbumes por compilations: {e}")
        return jsonify({"error": f"Error al obtener álbumes por compilations: {str(e)}"}), 500

@albums_ptes_blueprint.route('/all-compilations/<path:compilations>', methods=['GET'])
def get_by_all_compilations(compilations):
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))

        compilations_list = compilations.split("/")
        pendientes = get_albums_ptes_by_all_compilations(compilations_list, rnd=True)
        logging.info(f"Discos encontrados con todos las compilations {compilations_list}: {len(pendientes)}")

        paginated_albums_ptes = paginate_results(pendientes, page, limit)
        logging.info(f"Registros mostrados: {len(paginated_albums_ptes)}")

        return jsonify([convert_id(album) for album in paginated_albums_ptes])
    except Exception as e:
        logging.error(f"Error al obtener álbumes con todos los compilations: {e}")
        return jsonify({"error": f"Error al obtener álbumes con todos los compilations: {str(e)}"}), 500

@albums_ptes_blueprint.route('/search', methods=['GET'])
def search_albums_ptes():
    try:
        # Obtener los parámetros de la consulta (opciones opcionales)
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        
        decade = request.args.get('decade')
        genre = request.args.get('genre')
        mood = request.args.get('mood')
        year = request.args.get('year')
        min_duration = request.args.get('min_duration')
        max_duration = request.args.get('max_duration')
        compilations = request.args.get('compilations')

        # Crear el filtro
        filters = {}
        
        if decade:
            filters['decade'] = int(decade)
        if genre:
            filters['genre'] = genre
        if mood:
            filters['mood'] = mood
        if year:
            filters['year'] = year
        if min_duration:
            filters['min_duration'] = int(min_duration)
        if max_duration:
            filters['max_duration'] = int(max_duration)
        if compilations:
            filters['compilations'] = compilations

        # Llamar al servicio correspondiente según los filtros
        pendientes = get_filtered_albums_ptes(filters, rnd=True)

        # Aplicar paginación
        paginated_albums_ptes = paginate_results(pendientes, page, limit)
        logging.info(f"Registros encontrados: {len(pendientes)}")
        logging.info(f"Registros mostrados: {len(paginated_albums_ptes)}")

        return jsonify([convert_id(album) for album in paginated_albums_ptes])

    except Exception as e:
        logging.error(f"Error al obtener los álbumes: {e}")
        return jsonify({"error": f"Error al obtener los álbumes: {str(e)}"}), 500



@albums_ptes_blueprint.route('/releases/<days>', methods=['GET'])
def get_releases(days):
    """
    Endpoint que devuelve álbumes lanzados en los últimos 'days' días.
    Se espera recibir 'days' (por query string) y opcionalmente 'rnd' para mezclar el orden.
    Ejemplo de uso: /releases/days
    """
    pendientes = get_new_releases(days, False)
    return jsonify(pendientes)


@albums_ptes_blueprint.route('/anniversary/<days>', methods=['GET'])
def get_anniversary(days):
    """
    Endpoint que devuelve álbumes que 'cumplen años' (el día y mes de date_release se aproxima a la fecha actual).
    Se espera recibir 'days' (por query string) y opcionalmente 'rnd' para mezclar el orden.
    Ejemplo de uso: /cumpleanos/days
    """

    pendientes = get_anniversary_albums_ptes(days, False)
    return jsonify(pendientes)