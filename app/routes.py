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

from app.rag_service import add_documents, answer_query, answer_with_memory_and_rag

api_blueprint = Blueprint("api", __name__)

@api_blueprint.route("/upload_docs", methods=["POST"])
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
