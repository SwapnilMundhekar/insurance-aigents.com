# Semantic Chunking Design

The project originally used simple sliding-window chunking. That is useful for a first Retrieval Augmented Generation pipeline, but insurance documents are structured by sections, clauses, definitions, conditions, exclusions, and page references.

## Improved approach

The semantic ingestion endpoint performs:

1. Page-level text extraction.
2. Heading detection.
3. Section grouping.
4. Section-aware chunking.
5. Page metadata preservation.
6. RAG-compatible JSON chunk output.

## Metadata added to each chunk

```json
{
  "section_title": "What is covered",
  "page_start": 12,
  "page_end": 13,
  "chunking_strategy": "section_aware_sliding_window"
}
```

## Why this matters

When the Agentic RAG supervisor answers a policy question, it can now retrieve chunks that include page and section context. This improves explainability, traceability, and auditability.
