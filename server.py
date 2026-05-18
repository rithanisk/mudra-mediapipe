import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import requests

load_dotenv()

app = Flask(__name__)
CORS(app)

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"
ELEVENLABS_MODEL = "eleven_multilingual_v2"

BASE_DIR = Path(__file__).resolve().parent
TASK_FILE = BASE_DIR / "bharatanatyam_mudras.task"


@app.route("/")
def index():
    return send_file("index.html")


@app.route("/bharatanatyam_mudras.task")
def serve_model():
    return send_file(TASK_FILE, mimetype="application/octet-stream")


@app.route("/speak", methods=["POST"])
def speak():
    data = request.get_json(silent=True)
    if not data or "text" not in data:
        return jsonify({"error": "Missing 'text' field"}), 400

    if not ELEVENLABS_API_KEY or ELEVENLABS_API_KEY == "your_key_here":
        return jsonify({"error": "ElevenLabs API key not configured"}), 503

    text = data["text"]
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"

    resp = requests.post(
        url,
        json={
            "text": text,
            "model_id": ELEVENLABS_MODEL,
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
        },
        headers={
            "xi-api-key": ELEVENLABS_API_KEY,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        },
        timeout=10,
    )

    if resp.status_code != 200:
        return jsonify({"error": "TTS request failed", "status": resp.status_code}), 502

    return resp.content, 200, {"Content-Type": "audio/mpeg"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
