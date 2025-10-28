# app/rag_service.py
import faiss
import numpy as np
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# In-memory FAISS store
embedding_dim = 1536  # for text-embedding-3-small
index = faiss.IndexFlatL2(embedding_dim)
documents = []  # parallel list to store text data

def embed_text(texts):
    """Convert list of texts into embeddings using OpenAI."""
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
    """Retrieve context + ask GPT."""
    context = retrieve_context(query)
    context_text = "\n\n".join(context)
    prompt = f"Use the following context to answer:\n{context_text}\n\nQuestion: {query}"
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
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )
    response = completion.choices[0].message.content

    # Step 5: Update memory
    add_to_memory(session_id, "user", user_query)
    add_to_memory(session_id, "assistant", response)

    return response
