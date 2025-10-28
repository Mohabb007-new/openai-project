# app/memory_service.py
from collections import defaultdict

# Stores memory per user/session
chat_memory = defaultdict(list)

def add_to_memory(session_id, role, content):
    """Append a message to memory."""
    chat_memory[session_id].append({"role": role, "content": content})

def get_memory(session_id):
    """Get chat history for a session."""
    return chat_memory[session_id][-5:]  # Keep last 5 turns only

def clear_memory(session_id):
    """Reset the conversation memory."""
    chat_memory[session_id] = []
