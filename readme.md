# 🧠 OpenAI Project — Flask RAG API
A lightweight, modular AI backend built with **Flask**, featuring:
- 🔹 Chat completion using OpenAI models
- 🔹 Image generation
- 🔹 RAG (Retrieval-Augmented Generation) using FAISS
- 🔹 Conversational memory
- 🔹 Simple Express (Node.js) frontend
- 🔹 Docker support
- 🔹 API documentation via swagger.yaml
- 🔹 Postman collection (postman.json) for easy testing
- 🔹 Automated tests included in the tests folder
- 🔹 CI pipeline for automated testing and building Docker images
This project aims to provide a clean, easy-to-extend API for AI-powered applications with minimal setup.

---

## 🚀 Features
- **Chat API** – send text and receive AI responses
- **Image Generation** – generate images from prompts
- **RAG** – upload text documents and ask questions
- **Session Memory** – persistent multi-turn conversations
- **Frontend** – a simple UI for interacting with the API
- **Dockerized** – works anywhere

---

## 📦 Installation
```bash
git clone https://github.com/Mohabb007-new/openai-project.git
cd openai-project
pip install -r requirements.txt
```

Create a `.env` file:
```
OPENAI_API_KEY=your-openai-key
API_KEY=your-api-key
```

---

## 🐳 Run with Docker
```bash
docker-compose up --build
```
API will run at:
```
http://localhost:5000
```
Frontend runs at:
```
http://localhost:3010
```

---

## 📡 API Overview
All protected routes require:
```
x-api-key: your-api-key
```

### **Chat** — POST `/chat`
Send a message and receive an AI response.

### **Image Generation** — POST `/generateImage`
Generate images as base64 or downloadable PNG.

### **RAG Upload** — POST `/upload_docs`
Upload text documents for semantic search.

### **Ask RAG** — POST `/ask_rag`
Ask questions based on uploaded documents.

### **Chat + Memory** — POST `/chat_rag_memory`
Interactive multi-turn chat with context.

---

## 🧪 Tests
Run unit tests:
```bash
pytest -v
```

---

## 🔁 CI/CD
Includes a GitHub Actions workflow for:
- Running tests
- Building Docker image
- Pushing image to Docker Hub

---

## 🛠️ Tech Stack
- **Python + Flask**
- **OpenAI API**
- **FAISS** (RAG)
- **Pytest**
- **Node.js (Frontend)**
- **Docker**
- **GitHub Actions**

---

## 📘 Purpose
The project was built to explore AI backend development, structured APIs, containerized deployment, and a representative full-stack workflow.

---

## 📄 License
This project is open-source under the MIT License.

