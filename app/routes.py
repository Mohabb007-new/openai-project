from flask import Blueprint, jsonify, request
from app.openai_service import get_chat_response, get_image_response
from flask import current_app as app

api_blueprint = Blueprint('api', __name__)

# --- Authentication Decorator ---
def require_api_key(f):
    def wrapper(*args, **kwargs):
        key = request.headers.get("x-api-key")
        if key != app.config["API_KEY"]:
            return jsonify({"error": "Invalid API key"}), 401
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

# --- Routes ---
@api_blueprint.route("/", methods=["GET"])
@require_api_key
def home():
    return jsonify({"response": "Hello, World!"})

@api_blueprint.route("/chat", methods=["POST"])
@require_api_key
def chat():
    data = request.get_json()
    content = data.get("content")
    response = get_chat_response(content)
    return jsonify({"response": response, "version": "0.1.0"})

@api_blueprint.route("/generateImage", methods=["POST"])
@require_api_key
def generate_image():
    data = request.get_json()
    response_type = request.headers.get("response-type", "base64")
    content = data.get("content")
    result = get_image_response(content, response_type)
    return jsonify(result)
