#!/usr/bin/env python3
"""
Edge TTS HTTP Server
Usa las voces de Microsoft Edge (gratuitas y de alta calidad)
"""

import asyncio
import io
import os
import edge_tts
from flask import Flask, request, Response, jsonify, send_file
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

PORT = int(os.environ.get('PORT', 5000))
DEFAULT_VOICE = os.environ.get('EDGE_TTS_VOICE', 'es-MX-DaliaNeural')

# Cache de voces disponibles
_voices_cache = None

async def get_voices_async():
    """Obtiene todas las voces disponibles de Edge TTS."""
    global _voices_cache
    if _voices_cache is None:
        _voices_cache = await edge_tts.list_voices()
    return _voices_cache

def get_voices():
    """Wrapper síncrono para obtener voces."""
    return asyncio.run(get_voices_async())

async def synthesize_async(text: str, voice: str) -> bytes:
    """Sintetiza texto a audio MP3."""
    import sys
    print(f"[synthesize_async] Iniciando síntesis: text='{text[:50]}...', voice='{voice}'", file=sys.stderr)
    sys.stderr.flush()
    
    try:
        communicate = edge_tts.Communicate(text, voice)
        audio_data = b""
        chunk_count = 0
        audio_chunks = 0
        
        async for chunk in communicate.stream():
            chunk_count += 1
            if chunk["type"] == "audio":
                audio_chunks += 1
                audio_data += chunk["data"]
        
        print(f"[synthesize_async] Completado: {chunk_count} chunks totales, {audio_chunks} chunks de audio, {len(audio_data)} bytes", file=sys.stderr)
        sys.stderr.flush()
        
        if len(audio_data) == 0:
            raise Exception(f"No se recibió audio. Chunks procesados: {chunk_count}, chunks de audio: {audio_chunks}")
        
        return audio_data
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"[synthesize_async] ERROR: {str(e)}", file=sys.stderr)
        print(f"[synthesize_async] Traceback:\n{error_trace}", file=sys.stderr)
        sys.stderr.flush()
        raise

def synthesize(text: str, voice: str) -> bytes:
    """Wrapper síncrono para sintetizar."""
    return asyncio.run(synthesize_async(text, voice))

def filter_voices(voices, language=None, gender=None, locale=None):
    """Filtra voces por idioma, género y locale."""
    result = voices
    
    if language:
        lang_prefix = "es" if language.lower() in ["spanish", "español", "es"] else "en"
        result = [v for v in result if v.get("Locale", "").startswith(lang_prefix)]
    
    if gender:
        gender_val = "Female" if gender.lower() in ["female", "f", "femenino", "femenina"] else "Male"
        result = [v for v in result if v.get("Gender") == gender_val]
    
    if locale:
        result = [v for v in result if v.get("Locale") == locale]
    
    return result

def format_voice(v):
    """Formatea una voz para la respuesta JSON."""
    return {
        "id": v.get("ShortName"),
        "name": v.get("FriendlyName", v.get("ShortName")),
        "locale": v.get("Locale"),
        "gender": v.get("Gender"),
        "language": "Spanish" if v.get("Locale", "").startswith("es") else "English" if v.get("Locale", "").startswith("en") else v.get("Locale", "")[:2]
    }

# ============================================
# ENDPOINTS
# ============================================

@app.route('/')
def index():
    """Info del servicio."""
    return jsonify({
        "service": "Edge TTS HTTP Server",
        "version": "1.0.0",
        "description": "Voces de Microsoft Edge - Gratuitas y de alta calidad",
        "default_voice": DEFAULT_VOICE,
        "endpoints": {
            "GET /api/health": "Estado del servicio",
            "GET /api/voices": "Todas las voces",
            "GET /api/voices/spanish": "Voces en español",
            "GET /api/voices/english": "Voces en inglés",
            "GET /api/voices/spanish/female": "Femeninas español",
            "GET /api/voices/spanish/male": "Masculinas español",
            "GET /api/voices/english/female": "Femeninas inglés",
            "GET /api/voices/english/male": "Masculinas inglés",
            "GET /api/voices/<locale>": "Por locale (es-MX, es-ES, en-US)",
            "POST /api/tts": "Sintetizar voz"
        }
    })

@app.route('/api/health')
def health():
    """Health check."""
    return jsonify({"status": "ok", "voice": DEFAULT_VOICE})

# ============================================
# LISTADO DE VOCES
# ============================================

@app.route('/api/voices')
def list_all_voices():
    """Lista todas las voces disponibles."""
    voices = get_voices()
    return jsonify({
        "total": len(voices),
        "voices": [format_voice(v) for v in voices]
    })

@app.route('/api/voices/spanish')
def list_spanish_voices():
    """Voces en español."""
    voices = filter_voices(get_voices(), language="spanish")
    return jsonify({
        "language": "Spanish",
        "total": len(voices),
        "voices": [format_voice(v) for v in voices]
    })

@app.route('/api/voices/english')
def list_english_voices():
    """Voces en inglés."""
    voices = filter_voices(get_voices(), language="english")
    return jsonify({
        "language": "English",
        "total": len(voices),
        "voices": [format_voice(v) for v in voices]
    })

@app.route('/api/voices/spanish/female')
def list_spanish_female():
    """Voces femeninas en español."""
    voices = filter_voices(get_voices(), language="spanish", gender="female")
    return jsonify({
        "language": "Spanish",
        "gender": "Female",
        "total": len(voices),
        "voices": [format_voice(v) for v in voices]
    })

@app.route('/api/voices/spanish/male')
def list_spanish_male():
    """Voces masculinas en español."""
    voices = filter_voices(get_voices(), language="spanish", gender="male")
    return jsonify({
        "language": "Spanish",
        "gender": "Male",
        "total": len(voices),
        "voices": [format_voice(v) for v in voices]
    })

@app.route('/api/voices/english/female')
def list_english_female():
    """Voces femeninas en inglés."""
    voices = filter_voices(get_voices(), language="english", gender="female")
    return jsonify({
        "language": "English",
        "gender": "Female",
        "total": len(voices),
        "voices": [format_voice(v) for v in voices]
    })

@app.route('/api/voices/english/male')
def list_english_male():
    """Voces masculinas en inglés."""
    voices = filter_voices(get_voices(), language="english", gender="male")
    return jsonify({
        "language": "English",
        "gender": "Male",
        "total": len(voices),
        "voices": [format_voice(v) for v in voices]
    })

@app.route('/api/voices/<locale>')
def list_voices_by_locale(locale):
    """Voces por locale específico (es-MX, es-ES, en-US, etc)."""
    voices = filter_voices(get_voices(), locale=locale)
    return jsonify({
        "locale": locale,
        "total": len(voices),
        "voices": [format_voice(v) for v in voices]
    })

# ============================================
# SÍNTESIS
# ============================================

@app.route('/api/tts', methods=['GET', 'POST'])
def tts():
    """Sintetizar texto a audio."""
    try:
        if request.method == 'POST':
            if request.content_type and 'application/json' in request.content_type:
                data = request.get_json()
                text = data.get('text', '')
                voice = data.get('voice', DEFAULT_VOICE)
                lang = data.get('lang', '')
                gender = data.get('gender', '')
                speakingRate = data.get('speakingRate', 1.0)
            else:
                text = request.get_data(as_text=True)
                voice = request.args.get('voice', DEFAULT_VOICE)
                lang = request.args.get('lang', '')
                gender = request.args.get('gender', '')
                speakingRate = float(request.args.get('speakingRate', 1.0))
        else:
            text = request.args.get('text', '')
            voice = request.args.get('voice', DEFAULT_VOICE)
            lang = request.args.get('lang', '')
            gender = request.args.get('gender', '')
            speakingRate = float(request.args.get('speakingRate', 1.0))
        
        if not text:
            return jsonify({"error": "No text provided"}), 400
        
        # Validar que la voz existe
        if voice:
            voices = get_voices()
            voice_found = any(v.get("ShortName") == voice for v in voices)
            if not voice_found:
                return jsonify({
                    "error": f"Voice '{voice}' not found. Use /api/voices to see available voices.",
                    "provided_voice": voice
                }), 400
        
        print(f"[TTS] Sintetizando: text='{text[:50]}...', voice='{voice}', lang='{lang}', gender='{gender}', rate={speakingRate}")
        
        audio_data = synthesize(text, voice)
        
        if not audio_data or len(audio_data) == 0:
            return jsonify({
                "error": "No audio was received. Please verify that your parameters are correct.",
                "text": text[:100],
                "voice": voice
            }), 500
        
        print(f"[TTS] Audio generado: {len(audio_data)} bytes")
        
        return Response(
            audio_data,
            mimetype='audio/mpeg',
            headers={
                'Content-Disposition': 'attachment; filename=speech.mp3',
                'Content-Length': str(len(audio_data))
            }
        )
    except Exception as e:
        import traceback
        import sys
        error_trace = traceback.format_exc()
        error_msg = str(e)
        print(f"[TTS] ERROR: {error_msg}", file=sys.stderr)
        print(f"[TTS] Traceback:\n{error_trace}", file=sys.stderr)
        # Siempre mostrar el traceback en los logs del contenedor
        sys.stderr.flush()
        return jsonify({
            "error": error_msg,
            "traceback": error_trace
        }), 500

if __name__ == '__main__':
    print(f"🎤 Edge TTS HTTP Server v1.0.0")
    print(f"   Default Voice: {DEFAULT_VOICE}")
    print(f"   Port: {PORT}")
    print(f"")
    print(f"   Voces de Microsoft Edge - GRATUITAS y de alta calidad")
    print(f"")
    print(f"Endpoints:")
    print(f"   GET  /                          - Info del servicio")
    print(f"   GET  /api/health                - Health check")
    print(f"   GET  /api/voices                - Todas las voces")
    print(f"   GET  /api/voices/spanish        - Voces español")
    print(f"   GET  /api/voices/english        - Voces inglés")
    print(f"   GET  /api/voices/spanish/female - Femeninas español")
    print(f"   GET  /api/voices/spanish/male   - Masculinas español")
    print(f"   GET  /api/voices/english/female - Femeninas inglés")
    print(f"   GET  /api/voices/english/male   - Masculinas inglés")
    print(f"   GET  /api/voices/<locale>       - Por locale (es-MX, es-ES)")
    print(f"   POST /api/tts                   - Sintetizar voz")
    print(f"")
    
    # Habilitar debug para ver tracebacks completos
    import sys
    debug_mode = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.config['DEBUG'] = debug_mode
    
    app.run(host='0.0.0.0', port=PORT, threaded=True, debug=debug_mode)


