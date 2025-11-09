import os
#os.environ["FORCE_FAKE_OPENAI"] = "1"
from app import create_app

# Create a test version of your app
app = create_app()
app.config["TESTING"] = True
client = app.test_client()

# --- Test the GET / endpoint ---
def test_home():
    response = client.get("/", headers={"x-api-key": "my-secret-key"})
    assert response.status_code == 200
    assert response.json["response"] == "Hello, World!"

# --- Test missing API key ---
def test_home_missing_key():
    response = client.get("/")
    assert response.status_code == 401
    assert "error" in response.json

# --- Test POST /chat endpoint ---
def test_chat():
    data = {"content": "Hello!"}
    response = client.post("/chat", json=data, headers={"x-api-key": "my-secret-key"})
    assert response.status_code == 200
    assert "response" in response.json

def test_chat_missing_content():
    data = {}  # Missing "content"
    response = client.post("/chat", json=data, headers={"x-api-key": "my-secret-key"})
    assert response.status_code == 400  
    assert "error" in response.json

def test_chat_empty_content():
    data = {"content": ""}  # Empty string
    response = client.post("/chat", json=data, headers={"x-api-key": "my-secret-key"})
    assert response.status_code == 400
    assert "error" in response.json

# --- Test POST /chat with missing API key ---
def test_chat_missing_api_key():
    data = {"content": "Hello!"}
    response = client.post("/chat", json=data)  # No header
    assert response.status_code == 401
    assert "error" in response.json


# --- Test POST /generateImage endpoint ---
def test_generate_image_base64():
    """Check if the endpoint returns valid base64 JSON"""
    data = {"content": "A red elephant"}
    headers = {"x-api-key": "my-secret-key", "response-type": "base64"}
    response = client.post("/generateImage", json=data, headers=headers)

    assert response.status_code == 200
    json_data = response.get_json()
    assert "base64" in json_data
    assert "version" in json_data
    
def test_generate_image_file():
    """Check if the endpoint returns an image stream"""
    data = {"content": "A red elephant"}
    headers = {"x-api-key": "my-secret-key", "response-type": "image"}
    response = client.post("/generateImage", json=data, headers=headers)

    assert response.status_code == 200
    assert response.mimetype == "image/png"
    assert len(response.data) > 0  # image bytes exist

def test_generate_image_invalid_type():
    """Ensure invalid response-type returns 400 with a clear error message"""
    data = {"content": "A red elephant"}
    headers = {"x-api-key": "my-secret-key", "response-type": "invalid-type"}
    response = client.post("/generateImage", json=data, headers=headers)

    assert response.status_code == 402
    json_data = response.get_json()
    assert "error" in json_data
    assert "Invalid response-type" in json_data["error"]

def test_generate_image_missing_content():
    """Missing 'content' key should return 400"""
    data = {}  # no content
    headers = {"x-api-key": "my-secret-key", "response-type": "base64"}
    response = client.post("/generateImage", json=data, headers=headers)

    assert response.status_code == 400
    json_data = response.get_json()
    assert "error" in json_data


def test_generate_image_empty_content():
    """Empty 'content' should return 400"""
    data = {"content": ""}
    headers = {"x-api-key": "my-secret-key", "response-type": "image"}
    response = client.post("/generateImage", json=data, headers=headers)

    assert response.status_code == 400
    json_data = response.get_json()
    assert "error" in json_data


def test_generate_image_missing_api_key():
    """Requests without the API key should be rejected with 401"""
    data = {"content": "A red elephant"}
    headers = {"response-type": "base64"}  # no x-api-key
    response = client.post("/generateImage", json=data, headers=headers)

    assert response.status_code == 401
    json_data = response.get_json()
    assert "error" in json_data

# --- Test POST /upload_docs endpoint ---
def test_upload_docs():
    data = {"texts": ["Lebanon is a country.", "Beirut is its capital."]}
    response = client.post("/upload_docs", json=data, headers={"x-api-key": "my-secret-key"})
    assert response.status_code == 200
    assert "Stored" in response.json["message"]


def test_upload_docs_missing_texts():
    """Missing 'texts' key should return 400"""
    data = {}
    response = client.post("/upload_docs", json=data, headers={"x-api-key": "my-secret-key"})

    assert response.status_code == 400
    json_data = response.get_json()
    assert "error" in json_data


def test_upload_docs_empty_texts():
    """Empty list for 'texts' should return 400"""
    data = {"texts": []}
    response = client.post("/upload_docs", json=data, headers={"x-api-key": "my-secret-key"})

    assert response.status_code == 400
    json_data = response.get_json()
    assert "error" in json_data


def test_upload_docs_texts_wrong_type():
    """Wrong type for 'texts' should return 400"""
    data = {"texts": "not-a-list"}
    response = client.post("/upload_docs", json=data, headers={"x-api-key": "my-secret-key"})

    assert response.status_code == 400
    json_data = response.get_json()
    assert "error" in json_data

# --- Test POST /ask_rag endpoint ---
def test_ask_rag():
    # First upload documents
    client.post("/upload_docs", json={"texts": ["Lebanon is a country.", "Beirut is its capital."]}, headers={"x-api-key": "my-secret-key"})
    
    # Then ask a question
    data = {"query": "What is the capital of Lebanon?"}
    response = client.post("/ask_rag", json=data, headers={"x-api-key": "my-secret-key"})
    assert response.status_code == 200
    assert "response" in response.json


def test_ask_rag_missing_query():
    """Missing 'query' should return 400"""
    data = {}
    response = client.post("/ask_rag", json=data, headers={"x-api-key": "my-secret-key"})

    assert response.status_code == 400
    json_data = response.get_json()
    assert "error" in json_data


def test_ask_rag_empty_query():
    """Empty 'query' should return 400"""
    data = {"query": ""}
    response = client.post("/ask_rag", json=data, headers={"x-api-key": "my-secret-key"})

    assert response.status_code == 400
    json_data = response.get_json()
    assert "error" in json_data

# --- Test POST /chat_rag_memory endpoint ---
def test_chat_rag_memory():
    session_id = "test_user"
    
    # Upload some documents first
    client.post("/upload_docs", json={"texts": ["Lebanon is a country.", "Beirut is its capital."]}, headers={"x-api-key": "my-secret-key"})
    
    # Ask first question
    data1 = {"session_id": session_id, "query": "Tell me about Lebanon"}
    response1 = client.post("/chat_rag_memory", json=data1, headers={"x-api-key": "my-secret-key"})
    assert response1.status_code == 200
    assert "response" in response1.json
    
    # Ask a follow-up question to check memory
    data2 = {"session_id": session_id, "query": "What is its capital?"}
    response2 = client.post("/chat_rag_memory", json=data2, headers={"x-api-key": "my-secret-key"})
    assert response2.status_code == 200
    assert "response" in response2.json


def test_chat_rag_memory_missing_query():
    """Missing 'query' should return 400"""
    data = {"session_id": "test_user"}
    response = client.post("/chat_rag_memory", json=data, headers={"x-api-key": "my-secret-key"})

    assert response.status_code == 400
    json_data = response.get_json()
    assert "error" in json_data


def test_chat_rag_memory_empty_query():
    """Empty 'query' should return 400"""
    data = {"session_id": "test_user", "query": ""}
    response = client.post("/chat_rag_memory", json=data, headers={"x-api-key": "my-secret-key"})

    assert response.status_code == 400
    json_data = response.get_json()
    assert "error" in json_data


def test_chat_rag_memory_missing_api_key():
    """Requests without API key should be rejected with 401"""
    data = {"session_id": "test_user", "query": "Hello"}
    response = client.post("/chat_rag_memory", json=data)  # no header

    assert response.status_code == 401
    json_data = response.get_json()
    assert "error" in json_data


def test_chat_rag_memory_missing_session_id_defaults():
    """If session_id is missing the endpoint should still work (uses default)"""
    data = {"query": "Tell me about Lebanon"}
    response = client.post("/chat_rag_memory", json=data, headers={"x-api-key": "my-secret-key"})

    assert response.status_code == 200
    json_data = response.get_json()
    assert "response" in json_data
