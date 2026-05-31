import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from pypdf import PdfReader
from app.services.document_service import clean_text, estimate_tokens

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = PROJECT_ROOT / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
INDEX_DIR = DATA_DIR / "indexes"

HEADING_KEYWORDS = [
    "what is covered",
    "what is not covered",
    "exclusions",
    "definitions",
    "making a claim",
    "claims",
    "your responsibilities",
    "general conditions",
    "policy conditions",
    "excess",
    "premium",
    "theft",
    "fire",
    "storm",
    "windscreen",
    "accidental damage",
    "legal liability",
    "complaints",
    "privacy",
    "cancellation"
]

def ensure_dirs():
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    INDEX_DIR.mkdir(parents=True, exist_ok=True)

def save_upload(upload_file, document_id):
    ensure_dirs()
    safe_filename = Path(upload_file.filename).name
    saved_path = UPLOAD_DIR / f"{document_id}_{safe_filename}"
    with saved_path.open("wb") as file:
        file.write(upload_file.file.read())
    return saved_path, safe_filename

def extract_pages(file_path, source_filename):
    suffix = Path(source_filename).suffix.lower()

    if suffix == ".pdf":
        reader = PdfReader(str(file_path))
        pages = []
        for page_number, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            pages.append({
                "page_number": page_number,
                "text": clean_text(text)
            })
        return pages

    if suffix in [".txt", ".md"]:
        text = file_path.read_text(encoding="utf-8", errors="ignore")
        return [{
            "page_number": 1,
            "text": clean_text(text)
        }]

    raise ValueError("Unsupported file type. Upload .pdf, .txt, or .md only.")

def is_probable_heading(line):
    value = line.strip()
    lower_value = value.lower()

    if not value:
        return False

    if len(value) > 120:
        return False

    if len(value.split()) > 14:
        return False

    for keyword in HEADING_KEYWORDS:
        if keyword == lower_value or lower_value.startswith(keyword):
            return True

    if re.match(r"^\d+(\.\d+)*\s+[A-Z][A-Za-z ,&/()-]+$", value):
        return True

    letters = [character for character in value if character.isalpha()]
    if letters:
        uppercase_count = sum(1 for character in letters if character.isupper())
        uppercase_ratio = uppercase_count / len(letters)
        if uppercase_ratio > 0.75 and len(value) >= 4:
            return True

    return False

def extract_headings_from_page(text):
    headings = []
    for line in text.splitlines():
        cleaned_line = line.strip()
        if is_probable_heading(cleaned_line):
            headings.append(cleaned_line)
    return headings[:20]

def split_pages_into_sections(pages):
    sections = []
    current_title = "Document Start"
    current_lines = []
    current_page_start = 1
    current_page_end = 1

    for page in pages:
        page_number = page["page_number"]
        text = page["text"]
        lines = text.splitlines()

        for line in lines:
            cleaned_line = line.strip()

            if is_probable_heading(cleaned_line):
                if current_lines:
                    sections.append({
                        "section_title": current_title,
                        "page_start": current_page_start,
                        "page_end": current_page_end,
                        "text": clean_text("\n".join(current_lines))
                    })

                current_title = cleaned_line
                current_lines = [cleaned_line]
                current_page_start = page_number
                current_page_end = page_number
            else:
                if cleaned_line:
                    current_lines.append(cleaned_line)
                    current_page_end = page_number

    if current_lines:
        sections.append({
            "section_title": current_title,
            "page_start": current_page_start,
            "page_end": current_page_end,
            "text": clean_text("\n".join(current_lines))
        })

    if not sections:
        combined_text = clean_text("\n\n".join(page["text"] for page in pages))
        if combined_text:
            sections.append({
                "section_title": "Document Body",
                "page_start": 1,
                "page_end": pages[-1]["page_number"] if pages else 1,
                "text": combined_text
            })

    return sections

def tokenise(text):
    return re.findall(r"\w+|[^\w\s]", text)

def detokenise(tokens):
    text = " ".join(tokens)
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)
    text = re.sub(r"([\(\[\{])\s+", r"\1", text)
    text = re.sub(r"\s+([\)\]\}])", r"\1", text)
    return text.strip()

def chunk_sections(sections, document_id, source_filename, chunk_token_size=650, overlap_tokens=90):
    chunks = []
    chunk_index = 1

    for section in sections:
        section_text = section["text"]
        tokens = tokenise(section_text)

        if not tokens:
            continue

        start = 0
        while start < len(tokens):
            end = min(start + chunk_token_size, len(tokens))
            chunk_tokens = tokens[start:end]
            chunk_text = detokenise(chunk_tokens)

            chunk_id = f"{document_id}_chunk_{chunk_index:04d}"

            metadata = {
                "source_filename": source_filename,
                "section_title": section["section_title"],
                "page_start": section["page_start"],
                "page_end": section["page_end"],
                "chunking_strategy": "section_aware_sliding_window",
                "chunk_token_size": chunk_token_size,
                "overlap_tokens": overlap_tokens,
                "created_at_utc": datetime.now(timezone.utc).isoformat()
            }

            chunks.append({
                "document_id": document_id,
                "chunk_id": chunk_id,
                "chunk_index": chunk_index,
                "text": chunk_text,
                "token_estimate": estimate_tokens(chunk_text),
                "source_filename": source_filename,
                "metadata": metadata
            })

            if end == len(tokens):
                break

            start = max(end - overlap_tokens, start + 1)
            chunk_index += 1

        chunk_index += 1

    return chunks

def preview_text(text, limit=320):
    cleaned = re.sub(r"\s+", " ", text).strip()
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[:limit] + "..."

def save_semantic_chunks(document_id, chunks):
    output_path = INDEX_DIR / f"{document_id}_chunks.json"
    output_path.write_text(json.dumps(chunks, indent=2), encoding="utf-8")
    return output_path

def semantic_ingest_document(upload_file):
    document_id = str(uuid.uuid4())
    saved_path, safe_filename = save_upload(upload_file, document_id)
    pages = extract_pages(saved_path, safe_filename)
    sections = split_pages_into_sections(pages)
    chunks = chunk_sections(sections, document_id, safe_filename)
    output_path = save_semantic_chunks(document_id, chunks)

    page_reports = []
    for page in pages:
        headings = extract_headings_from_page(page["text"])
        page_reports.append({
            "page_number": page["page_number"],
            "character_count": len(page["text"]),
            "detected_headings": headings
        })

    chunk_samples = []
    for chunk in chunks[:5]:
        metadata = chunk["metadata"]
        chunk_samples.append({
            "chunk_id": chunk["chunk_id"],
            "chunk_index": chunk["chunk_index"],
            "section_title": metadata["section_title"],
            "page_start": metadata["page_start"],
            "page_end": metadata["page_end"],
            "token_estimate": chunk["token_estimate"],
            "preview": preview_text(chunk["text"])
        })

    total_token_estimate = sum(chunk["token_estimate"] for chunk in chunks)

    return {
        "document_id": document_id,
        "source_filename": safe_filename,
        "total_pages": len(pages),
        "total_sections_detected": len(sections),
        "total_chunks_created": len(chunks),
        "total_token_estimate": total_token_estimate,
        "chunks_file": f"data/indexes/{output_path.name}",
        "page_reports": page_reports,
        "chunk_samples": chunk_samples
    }
