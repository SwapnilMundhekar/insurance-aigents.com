import io
import re
import shutil
import uuid
from pathlib import Path
import fitz
import pytesseract
from PIL import Image
from pypdf import PdfReader
from app.services.document_service import clean_text, chunk_text, estimate_tokens, save_chunks
from app.services.pdf_quality_service import calculate_garbled_character_ratio, calculate_readable_character_ratio, calculate_whitespace_ratio, classify_page_quality, count_words

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = PROJECT_ROOT / "data"
UPLOAD_DIR = DATA_DIR / "uploads"

def ensure_dirs():
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def is_tesseract_available():
    return shutil.which("tesseract") is not None

def save_pdf(upload_file, document_id):
    ensure_dirs()
    safe_filename = Path(upload_file.filename).name
    saved_path = UPLOAD_DIR / f"{document_id}_{safe_filename}"
    with saved_path.open("wb") as file:
        file.write(upload_file.file.read())
    return saved_path, safe_filename

def render_page_to_image(pdf_path, page_index_zero_based, zoom=2.0):
    document = fitz.open(str(pdf_path))
    page = document.load_page(page_index_zero_based)
    matrix = fitz.Matrix(zoom, zoom)
    pixmap = page.get_pixmap(matrix=matrix, alpha=False)
    image_bytes = pixmap.tobytes("png")
    document.close()
    return Image.open(io.BytesIO(image_bytes))

def ocr_page(pdf_path, page_index_zero_based):
    image = render_page_to_image(pdf_path, page_index_zero_based)
    text = pytesseract.image_to_string(image)
    return text or ""

def preview_text(text, limit=320):
    cleaned = re.sub(r"\s+", " ", text).strip()
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[:limit] + "..."

def assess_text_quality(text):
    stripped_text = text.strip()
    character_count = len(stripped_text)
    word_count = count_words(stripped_text)
    readable_ratio = calculate_readable_character_ratio(stripped_text)
    garbled_ratio = calculate_garbled_character_ratio(stripped_text)
    whitespace_ratio = calculate_whitespace_ratio(stripped_text)
    status, recommendation = classify_page_quality(
        character_count,
        word_count,
        readable_ratio,
        garbled_ratio,
        whitespace_ratio
    )
    return status, recommendation, character_count, word_count

def ingest_pdf_with_ocr(upload_file):
    document_id = str(uuid.uuid4())
    saved_path, safe_filename = save_pdf(upload_file, document_id)
    reader = PdfReader(str(saved_path))
    ocr_available = is_tesseract_available()

    page_reports = []
    final_page_texts = []
    pages_using_pdf_text = 0
    pages_using_ocr = 0
    pages_with_no_text = 0

    for page_index, page in enumerate(reader.pages, start=1):
        normal_text = page.extract_text() or ""
        status, recommendation, normal_character_count, normal_word_count = assess_text_quality(normal_text)

        extraction_method = "pdf_text"
        ocr_text = ""
        final_text = normal_text

        if status in ["weak_extraction", "ocr_required"]:
            if ocr_available:
                ocr_text = ocr_page(saved_path, page_index - 1)
                ocr_status, ocr_recommendation, ocr_character_count, ocr_word_count = assess_text_quality(ocr_text)
                if len(ocr_text.strip()) > len(normal_text.strip()):
                    final_text = ocr_text
                    extraction_method = "ocr"
                    pages_using_ocr += 1
                    recommendation = "OCR fallback used because it produced more text than normal PDF extraction."
                else:
                    pages_using_pdf_text += 1
                    recommendation = "OCR was attempted, but normal PDF extraction produced equal or better text."
            else:
                pages_using_pdf_text += 1
                recommendation = recommendation + " Tesseract OCR is not available, so OCR fallback could not run."
        else:
            pages_using_pdf_text += 1

        final_text_cleaned = final_text.strip()

        if not final_text_cleaned:
            pages_with_no_text += 1
        else:
            final_page_texts.append(f"[PAGE {page_index} | METHOD {extraction_method}]\n{final_text_cleaned}")

        final_status, final_recommendation, final_character_count, final_word_count = assess_text_quality(final_text_cleaned)

        page_reports.append({
            "page_number": page_index,
            "extraction_method": extraction_method,
            "readability_status": final_status,
            "normal_text_characters": normal_character_count,
            "ocr_text_characters": len(ocr_text.strip()),
            "final_text_characters": final_character_count,
            "word_count": final_word_count,
            "recommendation": recommendation
        })

    combined_text = clean_text("\n\n".join(final_page_texts))
    total_characters = len(combined_text)
    total_tokens = estimate_tokens(combined_text)

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
        "total_pages": len(reader.pages),
        "pages_using_pdf_text": pages_using_pdf_text,
        "pages_using_ocr": pages_using_ocr,
        "pages_with_no_text": pages_with_no_text,
        "total_extracted_characters": total_characters,
        "total_token_estimate": total_tokens,
        "total_chunks_created": len(chunks),
        "chunks_file": chunks_file,
        "ocr_engine_available": ocr_available,
        "page_reports": page_reports,
        "chunk_samples": chunk_samples
    }
