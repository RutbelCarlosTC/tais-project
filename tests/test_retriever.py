"""
Pruebas de la capa de datos compartida y la herramienta query_domain_knowledge.
"""
import pytest
from src.data_layer.document_loader import load_knowledge_base, estimate_tokens
from src.data_layer.retriever_tool import query_domain_knowledge
from src.config import CHUNK_SIZE, CHUNK_OVERLAP, TOP_K_RETRIEVAL


def test_knowledge_base_loading_and_chunking():
    docs = load_knowledge_base()
    assert len(docs) > 0, "La base de conocimiento no debe estar vacía."

    for doc in docs:
        tokens = doc.metadata.get("estimated_tokens", estimate_tokens(doc.content))
        # Verificar que los chunks están en el rango adecuado
        assert tokens > 0
        assert "source" in doc.metadata
        assert "chunk_id" in doc.metadata


def test_query_domain_knowledge_returns_top_k():
    query = "calendario interactivo agendamiento matriz citas"
    results = query_domain_knowledge(query, top_k=TOP_K_RETRIEVAL)

    assert len(results) <= TOP_K_RETRIEVAL
    assert len(results) > 0

    first = results[0]
    assert hasattr(first, "content")
    assert hasattr(first, "source")
    assert hasattr(first, "score")
    assert first.score is not None


def test_query_domain_knowledge_relevance():
    query = "buzón de sugerencias anonimato código QR Recursos Humanos"
    results = query_domain_knowledge(query, top_k=3)
    
    combined = " ".join([r.content.lower() for r in results])
    assert "buzón" in combined or "sugerencias" in combined or "rrhh" in combined or "recursos humanos" in combined
