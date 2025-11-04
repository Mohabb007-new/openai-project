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

# --- Test POST /upload_docs endpoint ---
def test_upload_docs():
    data = {"texts": ["Lebanon is a country.", "Beirut is its capital."]}
    response = client.post("/upload_docs", json=data, headers={"x-api-key": "my-secret-key"})
    assert response.status_code == 200
    assert "Stored" in response.json["message"]

# --- Test POST /ask_rag endpoint ---
def test_ask_rag():
    # First upload documents
    client.post("/upload_docs", json={"texts": ["Lebanon is a country.", "Beirut is its capital."]}, headers={"x-api-key": "my-secret-key"})
    
    # Then ask a question
    data = {"query": "What is the capital of Lebanon?"}
    response = client.post("/ask_rag", json=data, headers={"x-api-key": "my-secret-key"})
    assert response.status_code == 200
    assert "response" in response.json

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
