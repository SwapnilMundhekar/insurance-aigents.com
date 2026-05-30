import os
import httpx

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")

def embed_text(text, prefix="search_document: "):
    prepared_text = prefix + text

    modern_payload = {
        "model": OLLAMA_EMBED_MODEL,
        "input": prepared_text
    }

    modern_url = f"{OLLAMA_BASE_URL}/api/embed"

    try:
        response = httpx.post(modern_url, json=modern_payload, timeout=120)
        response.raise_for_status()
        data = response.json()
        embeddings = data.get("embeddings", [])
        if embeddings and isinstance(embeddings[0], list):
            return embeddings[0]
    except Exception:
        pass

    legacy_payload = {
        "model": OLLAMA_EMBED_MODEL,
        "prompt": prepared_text
    }

    legacy_url = f"{OLLAMA_BASE_URL}/api/embeddings"

    response = httpx.post(legacy_url, json=legacy_payload, timeout=120)
    response.raise_for_status()
    data = response.json()
    embedding = data.get("embedding", [])

    if not embedding:
        raise ValueError("No embedding returned from Ollama.")

    return embedding