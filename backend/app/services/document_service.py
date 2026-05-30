import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from pypdf import PdfReader
from app.schemas.documents import DocumentChunk

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = PROJECT_ROOT / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
INDEX_DIR = DATA_DIR / "indexes"

def ensure_data_dirs():
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    INDEX_DIR.mkdir(parents=True, exist_ok=True)

def clean_text(text):
    text = text.replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()

def estimate_tokens(text):
    if not text:
        return 0
    words = re.findall(r"\w+|[^\w\s]", text)
    return len(words)

def extract_text_from_pdf(file_path):
    reader = PdfReader(str(file_path))
    page_texts = []
    for page_number, page in enumerate(reader.pages, start=1):
        extracted = page.extract_text() or ""
        if extracted.strip():
            page_texts.append(f"[PAGE {page_number}]\n{extracted}")
    return "\n\n".join(page_texts)

def extract_text(file_path, filename):
    suffix = Path(filename).suffix.lower()
    if suffix == ".pdf":
        return extract_text_from_pdf(file_path)
    if suffix in [".txt", ".md"]:
        return file_path.read_text(encoding="utf-8", errors="ignore")
    raise ValueError("Unsupported file type. Upload .txt, .md, or .pdf only.")

def chunk_text(text, document_id, source_filename, chunk_token_size=500, overlap_tokens=80):
    words = re.findall(r"\w+|[^\w\s]", text)
    chunks = []
    start = 0
    chunk_index = 1

    while start < len(words):
        end = min(start + chunk_token_size, len(words))
        chunk_words = words[start:end]
        chunk_text_value = " ".join(chunk_words)
        chunk_text_value = re.sub(r"\s+([,.;:!?])", r"\1", chunk_text_value)

        chunk_id = f"{document_id}_chunk_{chunk_index:04d}"

        metadata = {
            "source_filename": source_filename,
            "chunking_strategy": "sliding_window_word_chunking",
            "chunk_token_size": chunk_token_size,
            "overlap_tokens": overlap_tokens,
            "created_at_utc": datetime.now(timezone.utc).isoformat()
        }

        chunks.append(DocumentChunk(
            document_id=document_id,
            chunk_id=chunk_id,
            chunk_index=chunk_index,
            text=chunk_text_value,
            token_estimate=estimate_tokens(chunk_text_value),
            source_filename=source_filename,
            metadata=metadata
        ))

        if end == len(words):
            break

        start = max(end - overlap_tokens, start + 1)
        chunk_index += 1

    return chunks

def save_chunks(document_id, chunks):
    output_path = INDEX_DIR / f"{document_id}_chunks.json"
    serialised = [chunk.model_dump() for chunk in chunks]
    output_path.write_text(json.dumps(serialised, indent=2), encoding="utf-8")
    return output_path

def ingest_document(upload_file):
    ensure_data_dirs()
    document_id = str(uuid.uuid4())
    safe_filename = Path(upload_file.filename).name
    saved_path = UPLOAD_DIR / f"{document_id}_{safe_filename}"

    with saved_path.open("wb") as file:
        file.write(upload_file.file.read())

    raw_text = extract_text(saved_path, safe_filename)
    cleaned = clean_text(raw_text)
    chunks = chunk_text(cleaned, document_id, safe_filename)
    save_chunks(document_id, chunks)

    return {
        "document_id": document_id,
        "source_filename": safe_filename,
        "total_characters": len(cleaned),
        "total_token_estimate": estimate_tokens(cleaned),
        "total_chunks": len(chunks),
        "chunks": chunks
    }