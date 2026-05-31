import re
import uuid
from pathlib import Path
from pypdf import PdfReader
from app.services.document_service import clean_text, chunk_text, estimate_tokens, save_chunks
from app.services.pdf_quality_service import calculate_garbled_character_ratio, calculate_readable_character_ratio, calculate_whitespace_ratio, classify_page_quality, count_words

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = PROJECT_ROOT / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
INDEX_DIR = DATA_DIR / "indexes"

def ensure_dirs():
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    INDEX_DIR.mkdir(parents=True, exist_ok=True)

def save_pdf(upload_file, document_id):
    ensure_dirs()
    safe_filename = Path(upload_file.filename).name
    saved_path = UPLOAD_DIR / f"{document_id}_{safe_filename}"
    with saved_path.open("wb") as file:
        file.write(upload_file.file.read())
    return saved_path, safe_filename

def preview_text(text, limit=320):
    cleaned = re.sub(r"\s+", " ", text).strip()
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[:limit] + "..."

def run_pdf_ingestion_test(upload_file):
    document_id = str(uuid.uuid4())
    saved_path, safe_filename = save_pdf(upload_file, document_id)
    reader = PdfReader(str(saved_path))

    page_reports = []
    page_texts = []
    readable_pages = 0
    weak_extraction_pages = 0
    ocr_required_pages = 0

    for page_index, page in enumerate(reader.pages, start=1):
        extracted_text = page.extract_text() or ""
        stripped_text = extracted_text.strip()
        character_count = len(stripped_text)
        word_count = count_words(stripped_text)
        readable_ratio = calculate_readable_character_ratio(stripped_text)
        garbled_ratio = calculate_garbled_character_ratio(stripped_text)
        whitespace_ratio = calculate_whitespace_ratio(stripped_text)

        status, page_recommendation = classify_page_quality(
            character_count,
            word_count,
            readable_ratio,
            garbled_ratio,
            whitespace_ratio
        )

        if status == "readable":
            readable_pages += 1
        elif status == "weak_extraction":
            weak_extraction_pages += 1
        else:
            ocr_required_pages += 1

        page_reports.append({
            "page_number": page_index,
            "character_count": character_count,
            "word_count": word_count,
            "readability_status": status,
            "recommendation": page_recommendation
        })

        if stripped_text:
            page_texts.append(f"[PAGE {page_index}]\n{stripped_text}")

    total_pages = len(reader.pages)
    combined_text = clean_text("\n\n".join(page_texts))
    total_characters = len(combined_text)
    total_tokens = estimate_tokens(combined_text)

    if total_pages == 0:
        overall_quality = "empty_pdf"
        recommendation = "No pages were found in the PDF."
    elif ocr_required_pages == total_pages:
        overall_quality = "ocr_required"
        recommendation = "All pages appear to require OCR before useful chunking."
    elif ocr_required_pages > 0 or weak_extraction_pages > 0:
        overall_quality = "mixed"
        recommendation = "Use extracted text for readable pages and OCR fallback for weak or failed pages."
    else:
        overall_quality = "readable"
        recommendation = "Normal PDF text extraction appears sufficient for ingestion."

    chunks = []
    chunks_file = ""

    if combined_text:
        chunks = chunk_text(
            combined_text,
            document_id,
            safe_filename,
            chunk_token_size=500,
            overlap_tokens=80
        )
        output_path = save_chunks(document_id, chunks)
        chunks_file = f"data/indexes/{output_path.name}"

    chunk_samples = []
    for chunk in chunks[:5]:
        chunk_samples.append({
            "chunk_id": chunk.chunk_id,
            "chunk_index": chunk.chunk_index,
            "token_estimate": chunk.token_estimate,
            "preview": preview_text(chunk.text)
        })

    return {
        "document_id": document_id,
        "source_filename": safe_filename,
        "total_pages": total_pages,
        "readable_pages": readable_pages,
        "weak_extraction_pages": weak_extraction_pages,
        "ocr_required_pages": ocr_required_pages,
        "overall_quality": overall_quality,
        "recommendation": recommendation,
        "total_extracted_characters": total_characters,
        "total_token_estimate": total_tokens,
        "total_chunks_created": len(chunks),
        "chunks_file": chunks_file,
        "page_reports": page_reports,
        "chunk_samples": chunk_samples
    }
