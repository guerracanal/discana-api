import google.generativeai as genai
import os
import json
import time
from lastfm.services import get_user_top_albums

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

def get_album_genres(album_title, artist, label, release_date, country):
    with open('llm/prompt.txt', 'r') as f:
        prompt_template = f.read()
    
    prompt = prompt_template.format(
        album_title=album_title, 
        artist=artist, 
        label=label, 
        release_date=release_date,
        country=country
    )

    response_text = ask_gemini(prompt)
    
    if response_text is None:
        return {"error": "Error al comunicarse con todos los modelos disponibles"}

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
        required_fields = ["primary_genres", "secondary_genres", "descriptors", "description", "country"]
        for field in required_fields:
            if field not in response_json:
                if field == "description" or field == "country":
                    response_json[field] = ""
                else:
                    response_json[field] = []
        
        return response_json
        
    except json.JSONDecodeError as e:
        # Si falla el parseo, devolvemos un error con más información
        return {
            "error": "No se pudo parsear el JSON devuelto por el modelo", 
            "raw": response_text,
            "json_error": str(e)
        }

def get_album_description_and_country(album_title, artist, label, release_date, country):
    with open('llm/prompt_description_country.txt', 'r') as f:
        prompt_template = f.read()
    
    prompt = prompt_template.format(
        album_title=album_title, 
        artist=artist, 
        label=label, 
        release_date=release_date,
        country=country
    )

    response_text = ask_gemini(prompt)
    
    if response_text is None:
        return {"error": "Error al comunicarse con todos los modelos disponibles"}

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
        required_fields = ["description", "country"]
        for field in required_fields:
            if field not in response_json:
                response_json[field] = ""
        
        return response_json
        
    except json.JSONDecodeError as e:
        # Si falla el parseo, devolvemos un error con más información
        return {
            "error": "No se pudo parsear el JSON devuelto por el modelo", 
            "raw": response_text,
            "json_error": str(e)
        }

def get_melomaniac_profile(user_id):
    """
    Genera un perfil melómano para un usuario basado en sus álbumes más escuchados.
    """
    try:
        # Obtener los álbumes más escuchados del usuario
        top_albums, _ = get_user_top_albums(user_id=user_id, period='overall', limit=20)

        if not top_albums:
            return {"error": "No se pudieron obtener los álbumes más escuchados del usuario."}

        # Construir el prompt para el modelo Gemini
        prompt = f"""
        Actúa como un experto musicólogo y melómano. A continuación, te proporciono una lista de los álbumes más escuchados por un usuario en Last.fm:

        {json.dumps(top_albums, indent=2)}

        Por favor, redacta un perfil melómano detallado para este usuario. El perfil debe incluir:

        1.  **Análisis de Gustos y Preferencias:** Describe en detalle los gustos musicales del usuario. ¿Qué géneros predominan? ¿Hay artistas o estilos recurrentes? ¿Prefiere la música de una década o país en particular?
        2.  **Álbumes Más Escuchados:** Comenta sobre los álbumes más importantes de la lista. ¿Qué los hace especiales? ¿Hay alguna conexión o historia entre ellos (por ejemplo, son del mismo artista, del mismo movimiento musical, etc.)?
        3.  **Recomendaciones Personales:** Basado en el análisis anterior, sugiere una lista de 5 a 10 artistas y álbumes que el usuario debería escuchar. Estas recomendaciones deben ser relevantes para sus gustos, pero no deben estar en la lista de los más escuchados. Justifica cada recomendación.

        El resultado debe ser un texto coherente, bien redactado y con un tono amigable y experto.
        """

        # Llamar al modelo Gemini
        profile_text = ask_gemini(prompt)

        if profile_text:
            return {"profile": profile_text}
        else:
            return {"error": "No se pudo generar el perfil melómano."}

    except Exception as e:
        return {"error": f"Ocurrió un error al generar el perfil: {str(e)}"}
