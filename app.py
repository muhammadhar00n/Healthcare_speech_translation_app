from flask import Flask, request, jsonify, send_file, render_template
import speech_recognition as sr
from gtts import gTTS
import io
from deep_translator import GoogleTranslator

app = Flask(__name__)

# Root route serves the index.html file from the templates folder
@app.route('/')
def index():
    return render_template('index.html')

# Voice-to-Text endpoint
@app.route('/transcribe', methods=['POST'])
def transcribe():
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files['audio']
    recognizer = sr.Recognizer()

    with sr.AudioFile(audio_file) as source:
        audio_data = recognizer.record(source)
    
    try:
        transcript = recognizer.recognize_google(audio_data)
        return jsonify({"transcript": transcript})
    except sr.RequestError as e:
        return jsonify({"error": f"API unavailable: {e}"}), 500
    except sr.UnknownValueError:
        return jsonify({"error": "Unable to recognize speech"}), 400

# Translation endpoint using deep-translator
@app.route('/translate', methods=['POST'])
def translate_text():
    data = request.get_json()
    text = data.get('text', '')
    target_lang = data.get('target_lang', 'es')  # Default target language: Spanish

    try:
        translated_text = GoogleTranslator(source='auto', target=target_lang).translate(text)
        return jsonify({"translated_text": translated_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Text-to-Speech endpoint
@app.route('/speak', methods=['POST'])
def speak():
    data = request.get_json()
    text = data.get('text', '')
    lang = data.get('lang', 'en')

    # Check for empty text
    if not text.strip():
        return jsonify({"error": "No text provided"}), 400

    try:
        tts = gTTS(text=text, lang=lang)
        audio_fp = io.BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)
        return send_file(audio_fp, mimetype="audio/mp3", as_attachment=True, download_name="speech.mp3")
    except Exception as e:
        print("Error in /speak:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
