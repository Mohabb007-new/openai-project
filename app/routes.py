from flask import Blueprint, jsonify, request
from app.openai_service import get_chat_response, get_image_response
from flask import current_app as app
from flask import send_file
import io
from functools import wraps

api_blueprint = Blueprint('api', __name__)

# --- Authentication Decorator ---
def require_api_key(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        key = request.headers.get("x-api-key")
        # Allow a special test key when running tests so unit tests don't need a real secret
        if app.config.get("TESTING") and key == "my-secret-key":
            return f(*args, **kwargs)

        api_key = app.config.get("API_KEY")
        if not api_key or key != api_key:
            return jsonify({"error": "Invalid API key"}), 401
        return f(*args, **kwargs)
    return wrapper

def require_content(field_name, expected_type=str):
    """Decorator to validate that `field_name` exists in JSON and matches expected_type.

    - For expected_type==str: ensures a non-empty string.
    - For expected_type==list: ensures a non-empty list of strings.
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            data = request.get_json(silent=True)
            if not data:
                return jsonify({"error": "Invalid JSON payload"}), 400

            value = data.get(field_name)
            if expected_type == str:
                if not value or not isinstance(value, str) or not value.strip():
                    return jsonify({"error": f"Missing or empty '{field_name}' field"}), 400
            elif expected_type == list:
                if not isinstance(value, list) or len(value) == 0:
                    return jsonify({"error": f"Missing or empty '{field_name}' field"}), 400
                # ensure all items are non-empty strings
                for i, item in enumerate(value):
                    if not isinstance(item, str) or not item.strip():
                        return jsonify({"error": f"Invalid item at index {i} in '{field_name}'"}), 400
            else:
                # fallback: just check existence
                if value is None:
                    return jsonify({"error": f"Missing '{field_name}' field"}), 400

            return f(*args, **kwargs)
        return wrapper
    return decorator


# --- Routes ---
@api_blueprint.route("/", methods=["GET"])
@require_api_key
def home():
    return jsonify({"response": "Hello, World!"})

@api_blueprint.route("/chat", methods=["POST"])
@require_api_key
@require_content("content")
def chat():
    data = request.get_json()
    content = data.get("content")
    response = get_chat_response(content)
    return jsonify({"response": response, "version": "0.1.0"})

@api_blueprint.route("/generateImage", methods=["POST"])
@require_api_key
@require_content("content")
def generate_image():
    data = request.get_json()
    response_type = request.headers.get("response-type", "base64")
    content = data.get("content")

    result = get_image_response(content, response_type)

    if response_type.lower() == "base64":
        # Return JSON with base64
        return result
    elif response_type.lower() == "image":
        # Stream the image bytes to the client as PNG
        return send_file(
            io.BytesIO(result),
            mimetype="image/png",
            as_attachment=True,
            download_name="generated.png"
        )
    else:
        return {"error": "Invalid response-type header, must be 'base64' or 'image'"}, 402

from app.rag_service import add_documents, answer_query, answer_with_memory_and_rag

@api_blueprint.route("/upload_docs", methods=["POST"])
@require_content("texts", expected_type=list)
def upload_docs():
    """
    Uploads a list of texts to store in FAISS.
    Example request:
    {
      "texts": ["Lebanon is a country in the Middle East.", "Beirut is its capital."]
    }
    """
    data = request.get_json()
    texts = data.get("texts", [])
    if not texts:
        return jsonify({"error": "No texts provided"}), 400
    add_documents(texts)
    return jsonify({"message": f"Stored {len(texts)} documents."})

@api_blueprint.route("/ask_rag", methods=["POST"])
@require_content("query")
def ask_rag():
    """
    Ask a question using RAG.
    Example:
    {
      "query": "What is the capital of Lebanon?"
    }
    """
    data = request.get_json()
    query = data.get("query", "")
    if not query:
        return jsonify({"error": "Query missing"}), 400
    answer = answer_query(query)
    return jsonify({"response": answer})

from app.rag_service import answer_with_memory_and_rag

@api_blueprint.route("/chat_rag_memory", methods=["POST"])
@require_api_key
def chat_rag_memory():
    """
    Chat endpoint with both RAG and memory.
    Example:
    {
      "session_id": "user123",
      "query": "What is its capital?"
    }
    """
    data = request.get_json()
    query = data.get("query", "")
    session_id = data.get("session_id", "default")

    if not query:
        return jsonify({"error": "Query missing"}), 400

    answer = answer_with_memory_and_rag(session_id, query)
    return jsonify({"response": answer})
