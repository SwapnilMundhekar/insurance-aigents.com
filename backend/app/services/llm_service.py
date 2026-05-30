import os
import httpx

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")

def generate_with_ollama(prompt):
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }

    url = f"{OLLAMA_BASE_URL}/api/generate"

    try:
        response = httpx.post(url, json=payload, timeout=120)
        response.raise_for_status()
        data = response.json()
        output_text = data.get("response", "")
        return {
            "ok": True,
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "response": output_text,
            "input_characters": len(prompt),
            "output_characters": len(output_text)
        }
    except Exception as error:
        return {
            "ok": False,
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "response": "",
            "input_characters": len(prompt),
            "output_characters": 0,
            "error": str(error)
        }