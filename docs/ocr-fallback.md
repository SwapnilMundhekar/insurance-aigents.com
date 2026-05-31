# OCR Fallback Design

OCR means Optical Character Recognition. It is used when a PDF page does not contain reliable extractable text.

## Automated flow

1. The system first attempts normal PDF text extraction.
2. The system scores each page for readability.
3. Pages marked readable use normal extracted text.
4. Pages marked weak or OCR required are rendered as images.
5. Tesseract OCR reads text from those rendered page images.
6. The system compares normal extracted text with OCR text.
7. The better text is selected for ingestion.
8. The final merged text is chunked for Agentic RAG.

## Why OCR is page-level

Many insurance PDFs are mixed. Some pages contain selectable digital text, while others contain scanned forms or image-heavy pages. Page-level OCR avoids wasting compute on readable pages.
