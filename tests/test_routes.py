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

# --- Test POST /generateImage endpoint ---
def test_generate_image():
    data = {"content": "A red elephant"}
    headers = {"x-api-key": "my-secret-key", "response-type": "base64"}
    response = client.post("/generateImage", json=data, headers=headers)
    assert response.status_code == 200
    assert "version" in response.json

