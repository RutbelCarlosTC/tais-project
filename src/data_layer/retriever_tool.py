"""
Retriever Tool unificada para el RAG convencional y el Sistema Multiagente.
Asegura la validez interna del experimento al exponer exactamente la misma interfaz y datos.
"""
from typing import List
from src.config import TOP_K_RETRIEVAL
from src.models.schemas import DomainDocument
from src.data_layer.vector_store import VectorStoreManager


def get_retriever_instance() -> VectorStoreManager:
    """Devuelve la instancia singleton del gestor vectorial."""
    return VectorStoreManager.get_instance()


def query_domain_knowledge(query: str, top_k: int = TOP_K_RETRIEVAL) -> List[DomainDocument]:
    """
    Función canónica de recuperación de conocimiento de dominio.
    
    Esta única función es invocada directamente por el módulo RAG base
    y expuesta como herramienta para los agentes del grafo LangGraph.
    
    Args:
        query: Consulta en lenguaje natural o palabras clave del requisito.
        top_k: Número máximo de fragmentos relevantes a recuperar (por defecto 4).
        
    Returns:
        Lista de fragmentos DomainDocument con su fuente, contenido y score de relevancia.
    """
    retriever = get_retriever_instance()
    results = retriever.query(query=query, top_k=top_k)
    return results


def format_domain_context(docs: List[DomainDocument]) -> str:
    """Convierte una lista de DomainDocument a un bloque de texto legible para prompts."""
    if not docs:
        return "No se recuperaron documentos de dominio relevantes."

    formatted_parts = []
    for idx, doc in enumerate(docs, start=1):
        formatted_parts.append(
            f"--- Fragmento {idx} [Fuente: {doc.source} | ID: {doc.doc_id} | Score: {doc.score}] ---\n"
            f"{doc.content}\n"
        )
    return "\n".join(formatted_parts)
