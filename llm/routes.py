from flask import Blueprint, jsonify, request
from utils.helpers import require_admin_token
import google.generativeai as genai
import os
import json
import time

# Configurar la API key de Gemini
genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))

def get_available_models():
    """
    Obtiene todos los modelos disponibles de la API y los ordena por preferencia
    """
    try:
        models = genai.list_models()
        
        # Filtrar solo modelos que soportan generateContent
        generate_content_models = [
            model for model in models 
            if 'generateContent' in model.supported_generation_methods
        ]
        
        # Definir orden de preferencia basado en características conocidas
        preference_order = {
            # Modelos 2.5 (más nuevos, mejores límites)
            'gemini-2.5-flash-lite': 1,
            'gemini-2.5-flash': 2,
            'gemini-2.5-pro': 3,
            
            # Modelos 2.0  
            'gemini-2.0-flash-lite': 4,
            'gemini-2.0-flash': 5,
            
            # Modelos 1.5 (más antiguos pero estables)
            'gemini-1.5-pro': 6,
            'gemini-1.5-flash': 7,
            'gemini-1.5-flash-8b': 8,
            
            # Modelos legacy
            'gemini-pro': 9,
            'gemini-1.0-pro': 10,
        }
        
        # Extraer nombres de modelos y ordenar por preferencia
        model_names = []
        for model in generate_content_models:
            model_name = model.name.replace('models/', '')
            model_names.append(model_name)
        
        # Ordenar por preferencia (menor número = mayor preferencia)
        def get_preference(model_name):
            for key, value in preference_order.items():
                if key in model_name.lower():
                    return value
            return 999  # Modelos no conocidos al final
        
        sorted_models = sorted(model_names, key=get_preference)
        
        print(f"Modelos disponibles ordenados por preferencia: {sorted_models}")
        return sorted_models
        
    except Exception as e:
        print(f"Error obteniendo modelos disponibles: {e}")
        # Fallback a lista estática si la API falla
        return [
            'gemini-2.0-flash',
            'gemini-1.5-pro', 
            'gemini-1.5-flash',
            'gemini-pro'
        ]

def ask_gemini(prompt, max_retries=3, cooldown_seconds=2):
    """
    Función que llama al modelo Gemini con reintentos y múltiples modelos
    """
    # Lista de modelos para probar (en orden de preferencia)
    models_to_try = get_available_models()

    
    last_error = ""
    
    for model_name in models_to_try:
        print(f"Probando modelo: {model_name}")
        
        try:
            model = genai.GenerativeModel(model_name)
            
            for attempt in range(1, max_retries + 1):
                try:
                    print(f"  Intento {attempt}/{max_retries} con {model_name}")
                    
                    response = model.generate_content(
                        prompt,
                        generation_config=genai.types.GenerationConfig(
                            temperature=0.1,
                            max_output_tokens=1000,
                            top_p=0.8,
                            top_k=10
                        )
                    )
                    
                    if response.text:
                        print(f"  ✅ Éxito con {model_name} en intento {attempt}")
                        return response.text
                    else:
                        last_error = f"{model_name} - Intento {attempt}: Respuesta vacía"
                        
                except Exception as e:
                    error_msg = str(e).lower()
                    last_error = f"{model_name} - Intento {attempt}: {str(e)}"
                    print(f"  ❌ {last_error}")
                    
                    # Si es rate limit, esperar más tiempo
                    if 'quota' in error_msg or 'rate' in error_msg or 'limit' in error_msg:
                        wait_time = attempt * cooldown_seconds * 2  # Backoff exponencial
                        print(f"  ⏳ Rate limit detectado. Esperando {wait_time} segundos...")
                        time.sleep(wait_time)
                        continue
                    
                    # Si el modelo no existe, probar el siguiente
                    if 'not found' in error_msg or 'not supported' in error_msg:
                        print(f"  ⚠️ Modelo {model_name} no disponible")
                        break  # Salir del loop de reintentos para este modelo
                    
                    # Otros errores, esperar y reintentar
                    if attempt < max_retries:
                        wait_time = attempt * cooldown_seconds
                        print(f"  ⏳ Esperando {wait_time} segundos antes del siguiente intento...")
                        time.sleep(wait_time)
                        
        except Exception as model_error:
            last_error = f"{model_name}: {str(model_error)}"
            print(f"❌ Error inicializando modelo {model_name}: {model_error}")
            continue
    
    print(f"❌ Todos los modelos fallaron. Último error: {last_error}")
    return None

llm_blueprint = Blueprint('llm', __name__)

@llm_blueprint.route('/genre', methods=['POST'])
@require_admin_token
def genre():
    data = request.json
    album_title = data.get("title", "")
    artist = data.get("artist", "")
    label = data.get("label", "")
    release_date = data.get("release_date", "")

    prompt = f"""
    A continuación tienes información de un lanzamiento musical (puede ser álbum, EP, single, recopilatorio, directo, etc.).
    Título: {album_title}
    Artista: {artist}
    Sello: {label}
    Fecha de lanzamiento: {release_date}

    Devuelve únicamente un JSON válido con **exactamente** estos cuatro atributos:

    - "primary_genres": lista de 2 a 4 géneros principales.
    - "secondary_genres": lista de géneros secundarios (puede estar vacía).
    - "descriptors": lista de etiquetas descriptivas tomadas ÚNICAMENTE del listado proporcionado (4-10 etiquetas).
    - "description": texto en español sobre el lanzamiento (puede estar vacío si no tienes información fiable).

    **DESCRIPTORS VÁLIDOS - SOLO puedes usar etiquetas de esta lista:**
    angry, aggressive, anxious, bittersweet, calm, meditative, disturbing, energetic, manic, happy, playful, lethargic, longing, mellow, soothing, passionate, quirky, romantic, sad, depressive, lonely, melancholic, sombre, sensual, sentimental, uplifting, triumphant, apocalyptic, cold, dark, funereal, infernal, ominous, scary, epic, ethereal, futuristic, hypnotic, martial, mechanical, medieval, mysterious, natural, aquatic, desert, forest, rain, tropical, nocturnal, party, pastoral, peaceful, psychedelic, ritualistic, seasonal, autumn, spring, summer, winter, space, spiritual, surreal, suspenseful, tribal, urban, warm, bright, storm, beach, hazy, tone, altruistic, apathetic, boastful, cryptic, deadpan, hateful, humorous, insecure, menacing, misanthropic, optimistic, pessimistic, poetic, provocative, rebellious, sarcastic, satirical, serious, vulgar, dark humor, anthemic, atmospheric, atonal, avant-garde, chaotic, complex, dense, dissonant, eclectic, heavy, lush, melodic, microtonal, minimalistic, noisy, polyphonic, progressive, raw, repetitive, rhythmic, soft, sparse, technical, polyrhythmic, theatrical, bouncy, angular, maximalist, piercing, smooth, punchy, lyrical dissonance, narrative, stream of consciousness, crime, death, suicide, drugs, alcohol, violence, war, self-hatred, nihilistic, macabre, homicide, fantasy, folklore, mythology, occult, paranormal, science fiction, dreams, spirituality, introspective, alienation, political, protest, socialism, anarchism, nationalism, propaganda, anti-religious, feminism, LGBTQ, transgender, lesbian, gay, nonbinary, holiday, Christmas, Halloween, Carnaval, travel, food, leisure, dancing, video games, film, music, religious, Christian, Islamic, Hindu, Sikh, Buddhist, Bahá'í, Judaic, Rastafari, pagan, family, friendship, parenthood, love, breakup, infidelity, ageing, childhood, mental health, health, social issues, regret, envy, obsession, grief, anxiety, self-love, loyalty, failure, community, comics, internet, gambling, hallucinogens, wrestling, anime and manga, escapism, cocaine, opioids, cannabis, police, prison, pirates, guns, addiction, history, antiquity, conspiracy, cyberpunk, philosophy, existential, dystopian, literature, ballad, carol, children's music, fairy tale, lullaby, nursery rhyme, concept album, rock opera, concerto, ensemble, a cappella, acoustic, androgynous vocals, chamber music, string quartet, choral, female vocalist, instrumental, male vocalist, nonbinary vocalist, orchestral, vocal group, hymn, jingle, madrigal, mashup, medley, monologue, novelty, opera, oratorio, parody, poem, section, interlude, intro, movement, outro, reprise, silence, skit, sonata, stem, suite, symphony, tone poem, waltz, duet, diss, posse cut, pastiche, composition, aleatory, generative music, improvisation, uncommon time signatures, production, lobit, lo-fi, sampling, Wall of Sound, through-composed, call and response, jamming, free rhythm, triple metre, rubato

    **Instrucciones estrictas para DESCRIPTION:**
    - Describe el lanzamiento de forma precisa y factual
    - Puede ser una reseña, valoración, nota de prensa o descripción del mood/géneros
    - NO inventes información, NO alucines datos
    - Si no tienes información fiable sobre este lanzamiento específico, deja el campo VACÍO ("")
    - Considera que puede ser álbum, EP, single, recopilatorio, directo, etc.
    - Máximo 100 palabras en español

    **Instrucciones estrictas para DESCRIPTORS:**
    - Elige ÚNICAMENTE de la lista proporcionada
    - Entre 4 y 10 etiquetas
    - Que sean coherentes con el lanzamiento
    - Si no puedes elegir etiquetas apropiadas de la lista, deja el array VACÍO []

    **Formato JSON requerido:**
    1. No añadas texto fuera del JSON.
    2. No pongas comillas adicionales ni escapes innecesarios.
    3. Usa listas en formato JSON válido.
    4. El atributo description debe ser string (puede ser vacío "").
    
    Ejemplo:
    {{
        "primary_genres": ["Rock", "Alternative"],
        "secondary_genres": ["Indie", "Post-punk"],
        "descriptors": ["melancholic", "energetic", "raw", "rebellious"],
        "description": "Descripción factual del lanzamiento o cadena vacía si no tienes información fiable."
    }}
    """

    response_text = ask_gemini(prompt)
    
    if response_text is None:
        return jsonify({"error": "Error al comunicarse con todos los modelos disponibles"})

    try:
        # Limpiar la respuesta por si tiene markdown o texto adicional
        clean_response = response_text.strip()
        if clean_response.startswith('```json'):
            clean_response = clean_response[7:]
        if clean_response.endswith('```'):
            clean_response = clean_response[:-3]
        clean_response = clean_response.strip()
        
        # Convertir el texto JSON devuelto por el modelo en un diccionario real
        response_json = json.loads(clean_response)
        
        # Validar que tiene los campos requeridos
        required_fields = ["primary_genres", "secondary_genres", "descriptors", "description"]
        for field in required_fields:
            if field not in response_json:
                response_json[field] = [] if field != "description" else ""
        
        return jsonify(response_json)
        
    except json.JSONDecodeError as e:
        # Si falla el parseo, devolvemos un error con más información
        response_json = {
            "error": "No se pudo parsear el JSON devuelto por el modelo", 
            "raw": response_text,
            "json_error": str(e)
        }
        return jsonify(response_json)

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