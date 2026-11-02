"""
Agente 1: Analista de Dominio.
Responsabilidad:
Recibe el requisito informal, invoca la herramienta unificada query_domain_knowledge
y desglosa los actores involucrados, reglas de negocio detectadas en la normativa,
entidades clave del dominio, omisiones críticas y ambigüedades del usuario.
"""
from src.multiagent.state import MultiAgentState
from src.data_layer.retriever_tool import query_domain_knowledge, format_domain_context
from src.models.schemas import AnalystOutput
from src.models.llm_factory import get_llm_client
from src.data_layer.document_loader import estimate_tokens


ANALYST_SYSTEM_PROMPT = """Eres el Agente Analista de Dominio experto en sistemas clínicos, administrativos y regulatorios del Centro Psicológico Senses.
Tu objetivo es analizar un requisito informal en lenguaje natural y contrastarlo contra
la base de conocimiento de dominio recuperada.

Debes extraer rigurosamente:
1. Actores y roles involucrados.
2. Reglas de negocio normativas aplicables (con código de regla si existe).
3. Entidades clave del dominio.
4. Ambigüedades detectadas en la formulación informal del usuario.
5. Omisiones críticas identificadas respecto a las políticas institucionales.

NO inventes normas ni políticas fuera del contexto recuperado.
"""

ANALYST_USER_PROMPT_TEMPLATE = """REQUISITO INFORMAL:
"{informal_requirement}"

DOCUMENTOS DE DOMINIO RECUPERADOS (Base de Conocimiento):
{domain_context}

Realiza el desglose analítico riguroso identificando actores, reglas, entidades, ambigüedades y omisiones.
"""


def analyst_node(state: MultiAgentState) -> MultiAgentState:
    """Nodo LangGraph para el Agente Analista de Dominio."""
    informal_req = state.get("informal_requirement", "")
    top_k = state.get("top_k", 4)
    llm_client = get_llm_client()

    # 1. Invocación de la herramienta de recuperación vectorial unificada
    docs = query_domain_knowledge(query=informal_req, top_k=top_k)
    context_text = format_domain_context(docs)

    # 2. Generación estructurada del desglose analítico
    user_prompt = ANALYST_USER_PROMPT_TEMPLATE.format(
        informal_requirement=informal_req,
        domain_context=context_text
    )

    analyst_result: AnalystOutput = llm_client.generate_structured(
        system_prompt=ANALYST_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        schema_class=AnalystOutput
    )

    # 3. Métricas y trazabilidad
    tokens = estimate_tokens(ANALYST_SYSTEM_PROMPT + user_prompt + str(analyst_result.model_dump()))
    current_tokens = state.get("total_tokens_estimated", 0) + tokens

    history = state.get("execution_history", [])
    history.append({
        "step": "analyst",
        "actors": analyst_result.identified_actors,
        "rules_count": len(analyst_result.business_rules),
        "ambiguities_count": len(analyst_result.ambiguities_marked),
        "tokens": tokens
    })

    return {
        **state,
        "retrieved_docs": docs,
        "domain_context_text": context_text,
        "analyst_output": analyst_result,
        "total_tokens_estimated": current_tokens,
        "execution_history": history,
        "current_step": "analyst"
    }
