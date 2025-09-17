from flask import Blueprint, jsonify, request
from utils.helpers import require_admin_token
from llm.services import get_album_genres, get_album_description_and_country, get_available_models, get_melomaniac_profile
import google.generativeai as genai
from spotify.services import make_spotify_request, get_album_by_id

llm_blueprint = Blueprint('llm', __name__)

@llm_blueprint.route('/genre', methods=['POST'])
@require_admin_token
def genre():
    data = request.json
    album_title = data.get("title", "")
    artist = data.get("artist", "")
    label = data.get("label", "")
    release_date = data.get("release_date", "")
    country = data.get("country", "")

    response_json = get_album_genres(album_title, artist, label, release_date, country)
    
    return jsonify(response_json)

@llm_blueprint.route('/genre/<spotify_id>', methods=['GET'])
@require_admin_token
def genre_by_spotify_id(spotify_id):
    """
    Endpoint to get genres for a given Spotify album ID.
    """
    try:
        # Get user_id from the request arguments, required by get_album_by_id
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({"error": "user_id parameter is required"}), 400

        # Get album data from Spotify
        album_data = get_album_by_id(spotify_id, user_id=user_id)
        if not album_data:
            return jsonify({"error": "Album not found"}), 404

        # Extract album details for genre lookup
        album_title = album_data.get("title", "")
        artist = album_data.get("artist", "")
        # These fields are not available from spotify service
        label = ""
        release_date = album_data.get("date_release", "")
        # This is not available from spotify service.
        country = ""

        # Get album genres
        response_json = get_album_genres(album_title, artist, label, release_date, country)
        
        return jsonify(response_json)

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@llm_blueprint.route('/description_country/<spotify_id>', methods=['GET'])
@require_admin_token
def description_country_by_spotify_id(spotify_id):
    """
    Endpoint to get description and country for a given Spotify album ID.
    """
    try:
        # Get album data from Spotify
        album_data = make_spotify_request(endpoint=f"albums/{spotify_id}", no_user_neccessary=True)
        if not album_data:
            return jsonify({"error": "Album not found"}), 404

        # Extract album details for the LLM prompt
        album_title = album_data.get("name", "")
        artist = ", ".join(artist.get("name") for artist in album_data.get("artists", []))
        label = album_data.get("label", "")
        release_date = album_data.get("release_date", "")
        country = ""

        # Get album description and country
        response_json = get_album_description_and_country(album_title, artist, label, release_date, country)
        
        return jsonify(response_json)

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# Endpoint adicional para listar todos los modelos disponibles
@llm_blueprint.route('/list-models', methods=['GET'])
@require_admin_token  
def list_models():
    """Endpoint para listar todos los modelos disponibles con detalles"""
    try:
        models = genai.list_models()
        
        model_details = []
        for model in models:
            model_info = {
                "name": model.name.replace('models/', ''),
                "display_name": getattr(model, 'display_name', 'N/A'),
                "description": getattr(model, 'description', 'N/A'),
                "supported_methods": getattr(model, 'supported_generation_methods', []),
                "supports_generate_content": 'generateContent' in getattr(model, 'supported_generation_methods', [])
            }
            model_details.append(model_info)
        
        # Separar los que soportan generateContent
        generate_content_models = [m for m in model_details if m['supports_generate_content']]
        other_models = [m for m in model_details if not m['supports_generate_content']]
        
        return jsonify({
            "generate_content_models": generate_content_models,
            "other_models": other_models,
            "total_models": len(model_details),
            "usable_for_genre": len(generate_content_models)
        })
        
    except Exception as e:
        return jsonify({"error": f"Error obteniendo modelos: {str(e)}"})

@llm_blueprint.route('/test-models', methods=['GET'])
@require_admin_token  
def test_models():
    """Endpoint para probar qué modelos funcionan realmente"""
    
    # Obtener modelos disponibles dinámicamente
    models_to_test = get_available_models()
    
    results = {}
    
    for model_name in models_to_test[:5]:  # Probar solo los 5 mejores para no saturar
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(
                "Di solo 'OK'",
                generation_config=genai.types.GenerationConfig(max_output_tokens=10)
            )
            results[model_name] = "✅ Disponible" if response.text else "❌ Sin respuesta"
        except Exception as e:
            results[model_name] = f"❌ Error: {str(e)}"
    
    return jsonify({
        "tested_models": results,
        "available_models_count": len(get_available_models()),
        "recommendation": "Usa el primer modelo con ✅ para mejor rendimiento"
    })

@llm_blueprint.route('/profile/<user_id>', methods=['GET'])
@require_admin_token
def melomaniac_profile(user_id):
    """
    Genera un perfil melómano para un usuario.
    """
    try:
        response_json = get_melomaniac_profile(user_id)
        return jsonify(response_json)
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
