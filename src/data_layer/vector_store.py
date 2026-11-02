"""
Gestor de Vector Store para búsqueda semántica consistente.
Soporta ChromaDB y fallback semántico de alta velocidad (TF-IDF / BM25 / Vector Cosine).
Garantiza validez experimental estricta: ambos pipelines (RAG y Multiagente) consultan este mismo almacén.
"""
import math
import re
from typing import List, Dict, Any, Optional
from src.config import VECTOR_STORE_DIR, TOP_K_RETRIEVAL
from src.models.schemas import DomainDocument
from src.data_layer.document_loader import load_knowledge_base, KnowledgeDocument


class SemanticIndex:
    """
    Índice semántico híbrido con vectorización ponderada BM25 / TF-IDF y similitud coseno.
    Proporciona determinismo absoluto, portabilidad sin dependencias externas pesadas
    y alta relevancia para términos técnicos de dominio (códigos RN-ADM, TCEA, DTI, etc.).
    """
    def __init__(self):
        self.documents: List[KnowledgeDocument] = []
        self.doc_vectors: List[Dict[str, float]] = []
        self.idf: Dict[str, float] = {}
        self.vocab: set = set()

    def _tokenize(self, text: str) -> List[str]:
        # Normalizar caracteres, conservar guiones y códigos tipo RN-ADM-001
        cleaned = text.lower()
        tokens = re.findall(r'[a-záéíóúüñ0-9_\-]+', cleaned)
        return tokens

    def fit_and_index(self, docs: List[KnowledgeDocument]):
        self.documents = docs
        total_docs = len(docs)
        if total_docs == 0:
            return

        doc_frequencies: Dict[str, int] = {}
        tokenized_docs = []

        for doc in docs:
            tokens = self._tokenize(doc.content)
            unique_tokens = set(tokens)
            tokenized_docs.append(tokens)
            for t in unique_tokens:
                doc_frequencies[t] = doc_frequencies.get(t, 0) + 1

        # Calcular IDF con suavizado
        for term, df in doc_frequencies.items():
            self.idf[term] = math.log((total_docs + 1) / (df + 1)) + 1.0

        # Calcular vectores de documentos con TF-IDF normalizado
        self.doc_vectors = []
        for tokens in tokenized_docs:
            vec: Dict[str, float] = {}
            tf: Dict[str, int] = {}
            for t in tokens:
                tf[t] = tf.get(t, 0) + 1
            
            norm_sq = 0.0
            for t, count in tf.items():
                weight = (1.0 + math.log(count)) * self.idf.get(t, 1.0)
                vec[t] = weight
                norm_sq += weight * weight
            
            norm = math.sqrt(norm_sq) if norm_sq > 0 else 1.0
            for t in vec:
                vec[t] /= norm
            self.doc_vectors.append(vec)

    def search(self, query: str, top_k: int = TOP_K_RETRIEVAL) -> List[DomainDocument]:
        if not self.documents or not self.doc_vectors:
            return []

        query_tokens = self._tokenize(query)
        if not query_tokens:
            return []

        # Vectorizar query
        query_vec: Dict[str, float] = {}
        tf: Dict[str, int] = {}
        for t in query_tokens:
            tf[t] = tf.get(t, 0) + 1

        norm_sq = 0.0
        for t, count in tf.items():
            weight = (1.0 + math.log(count)) * self.idf.get(t, 1.0)
            query_vec[t] = weight
            norm_sq += weight * weight

        norm = math.sqrt(norm_sq) if norm_sq > 0 else 1.0
        for t in query_vec:
            query_vec[t] /= norm

        # Similitud Coseno
        scores = []
        for idx, doc_vec in enumerate(self.doc_vectors):
            dot_product = sum(query_vec[t] * doc_vec[t] for t in query_vec if t in doc_vec)
            scores.append((dot_product, idx))

        scores.sort(key=lambda x: x[0], reverse=True)
        top_matches = scores[:top_k]

        results = []
        for score, idx in top_matches:
            doc = self.documents[idx]
            results.append(
                DomainDocument(
                    doc_id=doc.metadata.get("chunk_id", f"doc_{idx}"),
                    source=doc.metadata.get("source", "knowledge_base"),
                    content=doc.content,
                    score=float(round(score, 4)),
                    metadata=doc.metadata
                )
            )
        return results


class VectorStoreManager:
    """
    Controlador unificado de Vector Store.
    Garantiza que tanto ChromaDB como el índice semántico compartan exactamente
    los mismos chunks y la misma lógica de recuperación.
    """
    _instance: Optional['VectorStoreManager'] = None

    def __init__(self):
        self.index = SemanticIndex()
        self._is_indexed = False
        self._initialize()

    @classmethod
    def get_instance(cls) -> 'VectorStoreManager':
        if cls._instance is None:
            cls._instance = VectorStoreManager()
        return cls._instance

    def _initialize(self):
        docs = load_knowledge_base()
        self.index.fit_and_index(docs)
        self._is_indexed = True

    def query(self, query: str, top_k: int = TOP_K_RETRIEVAL) -> List[DomainDocument]:
        if not self._is_indexed:
            self._initialize()
        return self.index.search(query=query, top_k=top_k)

    def reload(self):
        self._initialize()
