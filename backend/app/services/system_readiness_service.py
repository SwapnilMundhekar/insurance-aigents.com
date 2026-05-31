import json
import urllib.error
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
INDEX_DIR = PROJECT_ROOT / 'data' / 'indexes'

OLLAMA_TAGS_URL = 'http://127.0.0.1:11434/api/tags'
REQUIRED_MODELS = ['llama3.1:8b', 'nomic-embed-text']

def get_ollama_models():
    try:
        with urllib.request.urlopen(OLLAMA_TAGS_URL, timeout=2) as response:
            payload = json.loads(response.read().decode('utf-8'))
        models = []
        for model in payload.get('models', []):
            name = model.get('name', '')
            if name:
                models.append(name)
        return True, models
    except Exception:
        return False, []

def get_chunks_files():
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    files = sorted(INDEX_DIR.glob('*_chunks.json'), key=lambda path: path.stat().st_mtime, reverse=True)
    return files

def check_system_readiness():
    ollama_available, detected_models = get_ollama_models()
    chunks_files = get_chunks_files()
    indexed_documents_available = len(chunks_files) > 0
    latest_chunks_file = ''

    if chunks_files:
        latest_chunks_file = f'data/indexes/{chunks_files[0].name}'

    missing_models = []
    detected_base_names = set(detected_models)

    for required_model in REQUIRED_MODELS:
        found = False
        for detected_model in detected_base_names:
            if detected_model == required_model or detected_model.startswith(required_model + ':'):
                found = True
        if not found:
            missing_models.append(required_model)

    recommendations = []

    if not ollama_available:
        recommendations.append('Start Ollama with: ollama serve')

    if ollama_available and missing_models:
        for model in missing_models:
            recommendations.append(f'Install model with: ollama pull {model}')

    if not indexed_documents_available:
        recommendations.append('Upload or ingest an insurance policy document, then run the RAG indexing step.')

    ready = ollama_available and indexed_documents_available and len(missing_models) == 0

    return {
        'ready_for_agentic_rag': ready,
        'ollama_available': ollama_available,
        'indexed_documents_available': indexed_documents_available,
        'chunks_files_found': len(chunks_files),
        'latest_chunks_file': latest_chunks_file,
        'required_models': REQUIRED_MODELS,
        'detected_models': detected_models,
        'missing_models': missing_models,
        'recommendations': recommendations
    }
