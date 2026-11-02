"""
Agente 2: Redactor de Historias de Usuario (Product Owner).
Responsabilidad:
Toma el desglose del Analista de Dominio y el feedback acumulado del Agente Crítico
para redactar una Historia de Usuario en formato estándar:
'Como [rol] quiero [acción] para [beneficio]'
junto con escenarios de prueba exhaustivos en sintaxis Gherkin (Given-When-Then),
abarcando camino feliz, condiciones de borde y validaciones de rechazo normativo.
"""
from src.multiagent.state import MultiAgentState
from src.models.schemas import WriterOutput
from src.models.llm_factory import get_llm_client
from src.data_layer.document_loader import estimate_tokens


WRITER_SYSTEM_PROMPT = """Eres el Agente Redactor de Historias de Usuario y Product Owner técnico.
Tu responsabilidad es transformar el análisis de dominio en una Historia de Usuario profesional,
ágil y rigurosa, acompañada de escenarios de aceptación estructurados en sintaxis Gherkin (Given-When-Then).

ESTÁNDARES A SEGUIR:
1. Formato de HU estricto: 'Como [rol específico], quiero [acción precisa], para [beneficio de negocio medible]'.
2. Los escenarios Gherkin deben cubrir:
   - Happy Path (aprobación / ejecución exitosa).
   - Validaciones de rechazo basadas en las reglas normativas detectadas.
   - Casos borde o condiciones de seguridad.
3. Si recibes RETROALIMENTACIÓN DEL AGENTE CRÍTICO (en una iteración de corrección),
   es MANDATORIO atender cada una de las observaciones para subsanar omisiones o alucinaciones.
"""

WRITER_USER_PROMPT_TEMPLATE = """REQUISITO ORIGINAL:
"{informal_requirement}"

DESGLOSE DEL ANALISTA DE DOMINIO:
- Actores: {actors}
- Reglas de negocio clave: {rules}
- Entidades del dominio: {entities}
- Ambigüedades detectadas: {ambiguities}
- Omisiones detectadas: {omissions}
- Resumen analítico: {summary}

{critic_feedback_section}

INSTRUCCIONES:
Redacta la Historia de Usuario completa y los escenarios Gherkin formales asegurando
cobertura total de las reglas y subsanación de cualquier feedback previo.
"""


def writer_node(state: MultiAgentState) -> MultiAgentState:
    """Nodo LangGraph para el Agente Redactor de Historias."""
    informal_req = state.get("informal_requirement", "")
    analyst_out = state.get("analyst_output")
    critic_history = state.get("critic_feedback_history", [])
    iteration = state.get("iteration_count", 0)
    llm_client = get_llm_client()

    # Formatear sección de feedback si venimos de un bucle de corrección
    if critic_history and iteration > 0:
        latest_feedback = critic_history[-1]
        critic_section = (
            f"--- ATENCIÓN: RETROALIMENTACIÓN DEL CRÍTICO INVEST (Iteración {iteration}) ---\n"
            f"El crítico rechazó la versión anterior con las siguientes observaciones:\n"
            f"{latest_feedback}\n"
            f"DEBES AJUSTAR Y REFINAR LOS ESCENARIOS Y LA HU PARA CORREGIR ESTO ESPECÍFICAMENTE.\n"
            f"----------------------------------------------------------------------------------"
        )
    else:
        critic_section = "Primera iteración: genera la versión inicial de la Historia de Usuario y escenarios."

    actors_str = ", ".join(analyst_out.identified_actors) if analyst_out else "Usuario"
    rules_str = "; ".join([f"{r.code}: {r.description}" for r in analyst_out.business_rules]) if analyst_out else "N/A"
    entities_str = ", ".join(analyst_out.domain_entities) if analyst_out else "N/A"
    ambiguities_str = "; ".join(analyst_out.ambiguities_marked) if analyst_out else "Ninguna"
    omissions_str = "; ".join(analyst_out.omissions_detected) if analyst_out else "Ninguna"
    summary_str = analyst_out.domain_summary if analyst_out else ""

    user_prompt = WRITER_USER_PROMPT_TEMPLATE.format(
        informal_requirement=informal_req,
        actors=actors_str,
        rules=rules_str,
        entities=entities_str,
        ambiguities=ambiguities_str,
        omissions=omissions_str,
        summary=summary_str,
        critic_feedback_section=critic_section
    )

    writer_result: WriterOutput = llm_client.generate_structured(
        system_prompt=WRITER_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        schema_class=WriterOutput
    )

    tokens = estimate_tokens(WRITER_SYSTEM_PROMPT + user_prompt + str(writer_result.model_dump()))
    current_tokens = state.get("total_tokens_estimated", 0) + tokens

    history = state.get("execution_history", [])
    history.append({
        "step": f"writer_iteration_{iteration}",
        "iteration": iteration,
        "title": writer_result.title,
        "scenarios_count": len(writer_result.scenarios),
        "tokens": tokens
    })

    return {
        **state,
        "writer_output": writer_result,
        "total_tokens_estimated": current_tokens,
        "execution_history": history,
        "current_step": "writer"
    }
