import faiss
import numpy as np
from openai import OpenAI
import os

# Determine fake mode at runtime using env var or Flask testing config
def _is_fake_mode() -> bool:
    # explicit override to force fake
    if os.getenv("FORCE_FAKE_OPENAI"):
        return True

    # if a real API key is present, prefer real mode even during TESTING
    if os.getenv("OPENAI_API_KEY"):
        return False

    try:
        from flask import current_app

        if current_app and current_app.config.get("TESTING"):
            return True
    except Exception:
        pass
    # fallback: if no API key configured, default to fake
    return True


_client = None
def _get_client():
    global _client
    if _is_fake_mode():
        return None
    if _client is None:
        _client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    return _client

# In-memory FAISS store
embedding_dim = 1536  # for text-embedding-3-small
index = faiss.IndexFlatL2(embedding_dim)
documents = []  # parallel list to store text data


def embed_text(texts):
    """Convert list of texts into embeddings.

    If running in fake mode, return simple deterministic vectors so tests
    can run offline.
    """
    if _is_fake_mode():
        # deterministic pseudo-embeddings: depend on text length and index
        embeddings = []
        for i, t in enumerate(texts):
            vec = np.full((embedding_dim,), float((i + 1) % 10), dtype=np.float32)
            # mix in length to vary values
            vec += float(len(t) % 5)
            embeddings.append(vec)
        return embeddings

    client = _get_client()
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=texts
    )
    return [np.array(d.embedding, dtype=np.float32) for d in response.data]


def add_documents(text_list):
    """Store text data + embeddings in FAISS."""
    global documents
    embeddings = embed_text(text_list)
    faiss_matrix = np.vstack(embeddings)
    index.add(faiss_matrix)
    documents.extend(text_list)


def retrieve_context(query, top_k=3):
    """Find most relevant documents for a query."""
    query_emb = embed_text([query])[0].reshape(1, -1)
    distances, indices = index.search(query_emb, top_k)
    results = [documents[i] for i in indices[0] if i < len(documents)]
    return results


def answer_query(query):
    """Retrieve context + ask GPT. In fake mode, return a canned response."""
    context = retrieve_context(query)
    if _is_fake_mode():
        return f"(test) Answer to: {query}"

    context_text = "\n\n".join(context)
    prompt = f"Use the following context to answer:\n{context_text}\n\nQuestion: {query}"
    client = _get_client()
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return completion.choices[0].message.content


from app.memory_service import add_to_memory, get_memory


def answer_with_memory_and_rag(session_id, user_query):
    """Combine RAG context and chat memory for a better answer."""

    # Step 1: Retrieve relevant RAG context
    context = retrieve_context(user_query)
    context_text = "\n\n".join(context) if context else "No external context found."

    # Step 2: Get chat memory
    history = get_memory(session_id)

    # Step 3: Construct messages
    messages = history + [
        {"role": "system", "content": f"Use the following context:\n{context_text}"},
        {"role": "user", "content": user_query},
    ]

    # Step 4: Query the model
    if _is_fake_mode():
        response = f"(test) Memory+RAG answer to: {user_query}"
    else:
        client = _get_client()
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
        response = completion.choices[0].message.content

    # Step 5: Update memory
    add_to_memory(session_id, "user", user_query)
    add_to_memory(session_id, "assistant", response)

    return response
