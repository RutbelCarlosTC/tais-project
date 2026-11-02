"""
Agente 3: Crítico INVEST (QA / Reviewer).
Responsabilidad:
Evalúa la Historia de Usuario y los escenarios Gherkin generados por el Redactor
frente a los criterios INVEST (Independent, Negotiable, Valuable, Estimable, Small, Testable),
la fidelidad con la base de conocimiento (detección de alucinaciones) y desvíos semánticos no deseados.
Emite una decisión de aprobación ('passed') o retroalimentación precisa para el bucle de corrección.
"""
from src.multiagent.state import MultiAgentState
from src.models.schemas import CriticOutput
from src.models.llm_factory import get_llm_client
from src.data_layer.document_loader import estimate_tokens
from src.config import INVEST_PASS_THRESHOLD


CRITIC_SYSTEM_PROMPT = """Eres el Agente Crítico de Calidad, QA y Evaluador de Requisitos Ágiles.
Tu misión es actuar como el filtro riguroso de calidad antes de que los requisitos pasen a desarrollo.

DEBES EVALUAR CON MÁXIMO RIGOR:
1. Criterios INVEST (califica de 0.0 a 10.0 cada uno con justificación):
   - I: Independent (¿Está desacoplada o lista para implementarse sin bloqueos?)
   - N: Negotiable (¿Permite diálogo sobre detalles técnicos sin perder el objetivo?)
   - V: Valuable (¿El beneficio aporta valor tangible de negocio o mitigación de riesgo?)
   - E: Estimable (¿Tiene claridad suficiente para que los desarrolladores estimen su esfuerzo?)
   - S: Small (¿Es suficientemente acotada para un sprint o es un épica encubierta?)
   - T: Testable (¿Los escenarios Gherkin tienen criterios de éxito y rechazo verificables?)
2. Detección de Alucinaciones:
   - Identifica cualquier cláusula, número, regla o porcentaje que el Redactor haya inventado
     y que NO figure en los documentos de dominio recuperados.
3. Desvíos Semánticos no deseados:
   - Verifica si la HU se alejó de la intención real del requerimiento original del usuario.
4. Reglas del dominio omitidas:
   - Revisa si el Analista identificó reglas que el Redactor ignoró.

DECISIÓN DE APROBACIÓN:
- 'passed': True únicamente si el promedio INVEST es >= 7.5 Y no hay alucinaciones críticas ni omisiones graves.
- Si 'passed' es False, redacta 'actionable_feedback' detallado y constructivo indicando exactamente qué debe cambiar.
"""

CRITIC_USER_PROMPT_TEMPLATE = """REQUISITO ORIGINAL DEL USUARIO:
"{informal_requirement}"

HISTORIA DE USUARIO GENERADA POR EL REDACTOR:
- Título: {story_title}
- Formato: {user_story_text}

ESCENARIOS GHERKIN GENERADOS:
{gherkin_scenarios}

DOCUMENTOS RECUPERADOS DE LA BASE DE CONOCIMIENTO (Contexto de verdad):
{domain_context}

REGLAS DETECTADAS POR EL ANALISTA:
{analyst_rules}

Evalúa exhaustivamente bajo INVEST, detecta alucinaciones, desvíos semánticos y emite tu veredicto y feedback.
"""


def critic_node(state: MultiAgentState) -> MultiAgentState:
    """Nodo LangGraph para el Agente Crítico INVEST."""
    informal_req = state.get("informal_requirement", "")
    writer_out = state.get("writer_output")
    analyst_out = state.get("analyst_output")
    context_text = state.get("domain_context_text", "")
    iteration = state.get("iteration_count", 0)
    llm_client = get_llm_client()

    story_title = writer_out.title if writer_out else "Sin título"
    story_text = writer_out.user_story.full_text if writer_out else "N/A"
    gherkin_text = writer_out.raw_feature_text if writer_out else "N/A"
    rules_str = "; ".join([f"{r.code}: {r.description}" for r in analyst_out.business_rules]) if analyst_out else "N/A"

    user_prompt = CRITIC_USER_PROMPT_TEMPLATE.format(
        informal_requirement=informal_req,
        story_title=story_title,
        user_story_text=story_text,
        gherkin_scenarios=gherkin_text,
        domain_context=context_text,
        analyst_rules=rules_str
    )

    critic_result: CriticOutput = llm_client.generate_structured(
        system_prompt=CRITIC_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        schema_class=CriticOutput
    )

    # Validar consistencia de umbral
    if critic_result.overall_invest_score < INVEST_PASS_THRESHOLD:
        critic_result.passed = False

    tokens = estimate_tokens(CRITIC_SYSTEM_PROMPT + user_prompt + str(critic_result.model_dump()))
    current_tokens = state.get("total_tokens_estimated", 0) + tokens

    critic_history = list(state.get("critic_feedback_history", []))
    critic_history.append(critic_result.actionable_feedback)

    history = state.get("execution_history", [])
    history.append({
        "step": f"critic_iteration_{iteration}",
        "iteration": iteration,
        "passed": critic_result.passed,
        "invest_score": critic_result.overall_invest_score,
        "hallucinations_count": len(critic_result.hallucinations_detected),
        "tokens": tokens
    })

    return {
        **state,
        "critic_output": critic_result,
        "is_approved": critic_result.passed,
        "critic_feedback_history": critic_history,
        "total_tokens_estimated": current_tokens,
        "execution_history": history,
        "current_step": "critic"
    }
