"""
Cargador y divisor de documentos para la base de conocimiento de dominio.
Cumple con chunks de 500-800 tokens con 10-15% de solapamiento.
"""
import re
from pathlib import Path
from typing import List, Dict, Any
from src.config import KNOWLEDGE_BASE_DIR, CHUNK_SIZE, CHUNK_OVERLAP


class KnowledgeDocument:
    def __init__(self, content: str, metadata: Dict[str, Any]):
        self.content = content
        self.metadata = metadata

    def __repr__(self):
        return f"<KnowledgeDocument source={self.metadata.get('source')} len={len(self.content)}>"


def estimate_tokens(text: str) -> int:
    """Estimación heurística estándar: ~4 caracteres por token en español/inglés."""
    return max(1, len(text) // 4)


def split_text_into_chunks(text: str, target_tokens: int = CHUNK_SIZE, overlap_tokens: int = CHUNK_OVERLAP) -> List[str]:
    """
    Divide un texto en bloques de target_tokens (500-800 tokens) con overlap_tokens (10-15% solapamiento).
    Preserva límites de párrafos o secciones Markdown cuando es posible.
    """
    target_chars = target_tokens * 4
    overlap_chars = overlap_tokens * 4
    
    # Dividir preferentemente por secciones Markdown (## ) o párrafos dobles (\n\n)
    sections = re.split(r'(\n(?=## ))', text)
    unified_blocks = []
    
    current_block = ""
    for sec in sections:
        if len(current_block) + len(sec) <= target_chars:
            current_block += sec
        else:
            if current_block.strip():
                unified_blocks.append(current_block.strip())
            current_block = sec
    if current_block.strip():
        unified_blocks.append(current_block.strip())

    # Si algún bloque supera target_chars, subdividir con solapamiento
    final_chunks = []
    for block in unified_blocks:
        if len(block) <= target_chars:
            final_chunks.append(block)
        else:
            start = 0
            while start < len(block):
                end = min(start + target_chars, len(block))
                # Intentar cortar en fin de oración o salto de línea
                if end < len(block):
                    cut = block.rfind('\n', start, end)
                    if cut == -1 or cut <= start + (target_chars // 2):
                        cut = block.rfind('. ', start, end)
                    if cut != -1 and cut > start + (target_chars // 2):
                        end = cut + 1
                chunk_str = block[start:end].strip()
                if chunk_str:
                    final_chunks.append(chunk_str)
                if end >= len(block):
                    break
                start = end - overlap_chars
                if start < 0:
                    start = 0
    return final_chunks


def load_knowledge_base(kb_dir: Path = KNOWLEDGE_BASE_DIR) -> List[KnowledgeDocument]:
    """
    Carga todos los archivos Markdown de la base de conocimiento y los particiona.
    """
    docs = []
    if not kb_dir.exists():
        return docs

    for md_file in sorted(kb_dir.glob("*.md")):
        with open(md_file, "r", encoding="utf-8") as f:
            content = f.read()

        file_chunks = split_text_into_chunks(content, target_tokens=CHUNK_SIZE, overlap_tokens=CHUNK_OVERLAP)
        for idx, chunk_text in enumerate(file_chunks):
            doc = KnowledgeDocument(
                content=chunk_text,
                metadata={
                    "source": md_file.name,
                    "file_path": str(md_file),
                    "chunk_id": f"{md_file.stem}_chunk_{idx}",
                    "estimated_tokens": estimate_tokens(chunk_text)
                }
            )
            docs.append(doc)
    return docs
