import re
import uuid
from pathlib import Path
from pypdf import PdfReader

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = PROJECT_ROOT / "data"
UPLOAD_DIR = DATA_DIR / "uploads"

def ensure_upload_dir():
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def count_words(text):
    return len(re.findall(r"\b\w+\b", text))

def calculate_readable_character_ratio(text):
    if not text:
        return 0.0
    readable_count = 0
    for character in text:
        if character.isalnum() or character.isspace() or character in ".,;:!?()[]{}'\"-/&%$#@+*=\n\t":
            readable_count += 1
    return round(readable_count / len(text), 4)

def calculate_whitespace_ratio(text):
    if not text:
        return 1.0
    whitespace_count = 0
    for character in text:
        if character.isspace():
            whitespace_count += 1
    return round(whitespace_count / len(text), 4)

def calculate_garbled_character_ratio(text):
    if not text:
        return 1.0
    garbled_count = 0
    for character in text:
        if not character.isalnum() and not character.isspace() and character not in ".,;:!?()[]{}'\"-/&%$#@+*=\n\t":
            garbled_count += 1
    return round(garbled_count / len(text), 4)

def classify_page_quality(character_count, word_count, readable_ratio, garbled_ratio, whitespace_ratio):
    if character_count < 80 or word_count < 20:
        return "ocr_required", "Very little extractable text found. Page is likely scanned or image based."

    if garbled_ratio > 0.15:
        return "ocr_required", "Extracted text contains too many unusual characters."

    if readable_ratio < 0.75:
        return "weak_extraction", "Extracted text quality is weak and may need OCR or better parsing."

    if whitespace_ratio > 0.65:
        return "weak_extraction", "Extracted text contains too much whitespace and may be poorly parsed."

    if character_count < 250 or word_count < 50:
        return "weak_extraction", "Some text was extracted, but the page may be incomplete."

    return "readable", "Normal text extraction appears sufficient for this page."

def save_uploaded_pdf(upload_file):
    ensure_upload_dir()
    safe_filename = Path(upload_file.filename).name
    saved_path = UPLOAD_DIR / f"quality_check_{uuid.uuid4()}_{safe_filename}"
    with saved_path.open("wb") as file:
        file.write(upload_file.file.read())
    return saved_path, safe_filename

def analyze_pdf_quality(upload_file):
    saved_path, safe_filename = save_uploaded_pdf(upload_file)
    reader = PdfReader(str(saved_path))
    page_reports = []

    readable_pages = 0
    weak_extraction_pages = 0
    ocr_required_pages = 0

    for page_index, page in enumerate(reader.pages, start=1):
        extracted_text = page.extract_text() or ""
        character_count = len(extracted_text.strip())
        word_count = count_words(extracted_text)
        readable_ratio = calculate_readable_character_ratio(extracted_text)
        garbled_ratio = calculate_garbled_character_ratio(extracted_text)
        whitespace_ratio = calculate_whitespace_ratio(extracted_text)

        status, recommendation = classify_page_quality(
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
            "readable_character_ratio": readable_ratio,
            "garbled_character_ratio": garbled_ratio,
            "whitespace_ratio": whitespace_ratio,
            "readability_status": status,
            "recommendation": recommendation
        })

    total_pages = len(reader.pages)

    if total_pages == 0:
        overall_quality = "empty_pdf"
        recommendation = "No pages found in PDF."
    elif ocr_required_pages == total_pages:
        overall_quality = "ocr_required"
        recommendation = "All pages appear to require OCR before chunking."
    elif ocr_required_pages > 0 or weak_extraction_pages > 0:
        overall_quality = "mixed"
        recommendation = "Use normal extraction for readable pages and OCR fallback for weak or failed pages."
    else:
        overall_quality = "readable"
        recommendation = "Normal PDF text extraction appears sufficient."

    return {
        "source_filename": safe_filename,
        "total_pages": total_pages,
        "readable_pages": readable_pages,
        "weak_extraction_pages": weak_extraction_pages,
        "ocr_required_pages": ocr_required_pages,
        "overall_quality": overall_quality,
        "recommendation": recommendation,
        "pages": page_reports
    }