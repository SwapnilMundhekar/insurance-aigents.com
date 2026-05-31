# Public Insurance PDF Testing Workflow

This project supports local testing with public insurance PDFs such as Product Disclosure Statements, claims process documents, and insurance code of practice documents.

## Important

Do not commit downloaded PDFs, generated chunks, vector indexes, or trace logs to GitHub.

Local test PDFs should be stored under:

```text
data/test_documents/raw/
```

This folder is ignored by Git.

## Test flow

1. Download a public insurance PDF.
2. Upload it to `POST /documents/pdf-quality`.
3. Review whether pages are readable, weak, or OCR required.
4. Upload it to `POST /documents/pdf-ingestion-test`.
5. Confirm extracted characters, token estimate, and chunk count.
6. Use the returned `document_id` in `POST /rag/index`.
7. Ask questions through `POST /agentic/rag-answer`.

## Example questions

- Is windscreen damage covered?
- What evidence may be required for a claim?
- What exclusions apply to mechanical failure?
- When should a claim be escalated for review?
- What obligations apply during claims handling?
