"""
Pipeline RAG Convencional (Baseline de contraste).
Consume exactamente el mismo contexto vectorial mediante query_domain_knowledge y el mismo LLM,
pero de forma directa en un único paso sin descomposición de roles ni bucle de crítica.
"""
import time
import re
from typing import List, Tuple
from src.config import TOP_K_RETRIEVAL
from src.data_layer.retriever_tool import query_domain_knowledge, format_domain_context
from src.models.schemas import ConventionalRagOutput, DomainDocument
from src.models.llm_factory import get_llm_client, BaseLLMClient
from src.data_layer.document_loader import estimate_tokens


RAG_SYSTEM_PROMPT = """Eres un asistente de ingeniería de software y análisis de requisitos.
Tu objetivo es redactar una Historia de Usuario estándar (Como [rol] quiero [acción] para [beneficio])
y criterios de aceptación en formato Gherkin (Feature, Scenario, Given, When, Then).
Debes basarte estrictamente en el contexto de dominio recuperado.
"""

RAG_USER_PROMPT_TEMPLATE = """REQUISITO INFORMAL:
"{informal_requirement}"

CONTEXTO DE DOMINIO RECUPERADO DE LA BASE DE CONOCIMIENTO:
{domain_context}

INSTRUCCIONES:
1. Genera una Historia de Usuario que formalice el requisito informal.
2. Genera los escenarios de prueba en formato Gherkin (Given-When-Then).
3. Asegúrate de incluir las reglas de negocio mencionadas en el contexto recuperado.
"""


class ConventionalRagPipeline:
    """
    Implementación del pipeline RAG convencional sin orquestación multiagente.
    Sirve como línea base (baseline) para contrastar rigor, alucinaciones y calidad INVEST.
    """
    def __init__(self, llm_client: BaseLLMClient = None):
        self.llm_client = llm_client or get_llm_client()

    def run(self, informal_requirement: str, top_k: int = TOP_K_RETRIEVAL) -> ConventionalRagOutput:
        start_time = time.time()

        # 1. Recuperación vectorial compartida
        retrieved_docs: List[DomainDocument] = query_domain_knowledge(
            query=informal_requirement,
            top_k=top_k
        )
        formatted_context = format_domain_context(retrieved_docs)

        # 2. Invocación LLM directa
        user_prompt = RAG_USER_PROMPT_TEMPLATE.format(
            informal_requirement=informal_requirement,
            domain_context=formatted_context
        )
        
        raw_response = self.llm_client.generate(
            system_prompt=RAG_SYSTEM_PROMPT,
            user_prompt=user_prompt
        )

        elapsed = time.time() - start_time
        total_tokens = estimate_tokens(RAG_SYSTEM_PROMPT + user_prompt + raw_response)

        # 3. Separación heurística básica de HU y Gherkin
        user_story, gherkin = self._extract_story_and_gherkin(raw_response)

        return ConventionalRagOutput(
            raw_response=raw_response,
            user_story=user_story,
            gherkin_scenarios=gherkin,
            retrieved_documents=retrieved_docs,
            execution_time_seconds=round(elapsed, 3),
            total_tokens_estimated=total_tokens
        )

    def _extract_story_and_gherkin(self, text: str) -> Tuple[str, str]:
        # Buscar bloques 'Feature:' o 'Scenario:'
        feature_match = re.search(r'(Feature:.*)', text, re.DOTALL | re.IGNORECASE)
        if feature_match:
            gherkin_part = feature_match.group(1).strip()
            story_part = text[:feature_match.start()].strip()
        else:
            story_part = text.strip()
            gherkin_part = ""

        # Limpiar encabezados si existen
        story_part = re.sub(r'^(HISTORIA DE USUARIO|HISTORIA|USER STORY):\s*', '', story_part, flags=re.IGNORECASE).strip()
        return story_part, gherkin_part
