from app.services.vector_search_service import search_vector_index
from app.services.llm_service import generate_with_ollama

def build_grounded_prompt(query, search_results):
    context_sections = []

    for index, result in enumerate(search_results, start=1):
        section_lines = [
            f"SOURCE {index}",
            f"Document ID: {result['document_id']}",
            f"Chunk ID: {result['chunk_id']}",
            f"Source file: {result['source_filename']}",
            f"Similarity score: {result['score']}",
            "Context text:",
            result["text"]
        ]
        context_sections.append("\n".join(section_lines))

    context_text = "\n\n---\n\n".join(context_sections)

    prompt_lines = [
        "You are an insurance policy analysis assistant.",
        "Answer the user's question using only the provided retrieved context.",
        "Do not invent facts that are not present in the context.",
        "If the context does not contain the answer, say that the provided documents do not contain enough information.",
        "Give a clear answer first, then briefly explain the evidence.",
        "Mention source chunk IDs used in the explanation.",
        "",
        "USER QUESTION:",
        query,
        "",
        "RETRIEVED CONTEXT:",
        context_text,
        "",
        "FINAL ANSWER:"
    ]

    return "\n".join(prompt_lines)

def answer_with_rag(query, document_id=None, top_k=3):
    search_response = search_vector_index(query=query, document_id=document_id, top_k=top_k)
    results = search_response["results"]

    if not results:
        return {
            "query": query,
            "answer": "The provided documents do not contain enough information to answer this question.",
            "llm_model": "none",
            "embedding_model": search_response["embedding_model"],
            "total_sources_used": 0,
            "sources": [],
            "prompt_character_count": 0
        }

    prompt = build_grounded_prompt(query, results)
    llm_response = generate_with_ollama(prompt)

    if not llm_response["ok"]:
        raise RuntimeError(llm_response.get("error", "LLM generation failed"))

    sources = []
    for result in results:
        sources.append({
            "document_id": result["document_id"],
            "chunk_id": result["chunk_id"],
            "chunk_index": result["chunk_index"],
            "score": result["score"],
            "source_filename": result["source_filename"],
            "text": result["text"]
        })

    return {
        "query": query,
        "answer": llm_response["response"],
        "llm_model": llm_response["model"],
        "embedding_model": search_response["embedding_model"],
        "total_sources_used": len(sources),
        "sources": sources,
        "prompt_character_count": len(prompt)
    }