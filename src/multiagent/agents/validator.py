"""
Agente 4: Validador de Sintaxis & Formato.
Responsabilidad:
Recibe la versión aprobada (o final por límite de iteraciones) de la HU y Gherkin.
Ejecuta un linter sintáctico riguroso sobre las cláusulas Gherkin mediante expresiones
regulares y reglas formales de BDD.
Produce el artefacto estructurado final (archivo .feature limpio y JSON de entrega).
"""
import re
from typing import List, Tuple
from src.multiagent.state import MultiAgentState
from src.models.schemas import ValidatorOutput, GherkinLintError


def lint_gherkin_text(raw_text: str) -> Tuple[bool, List[GherkinLintError], int]:
    """
    Linter sintáctico para especificaciones BDD en formato Gherkin.
    Valida presencia de Feature, Scenarios, estructura secuencial Given-When-Then,
    y detecta pasos vacíos o mal formados.
    """
    errors: List[GherkinLintError] = []
    lines = raw_text.splitlines()

    has_feature = False
    scenarios_found = 0
    current_scenario = None
    has_given = False
    has_when = False
    has_then = False

    gherkin_step_pattern = re.compile(r'^\s*(Given|When|Then|And|But|Dado|Cuando|Entonces|Y|Pero)\s+(.+)$', re.IGNORECASE)
    scenario_pattern = re.compile(r'^\s*(Scenario|Escenario|Scenario Outline|Esquema del escenario):\s*(.+)$', re.IGNORECASE)
    feature_pattern = re.compile(r'^\s*(Feature|Característica|Funcionalidad):\s*(.+)$', re.IGNORECASE)

    for line_idx, raw_line in enumerate(lines, start=1):
        line = raw_line.strip()
        if not line or line.startswith('#') or line.startswith('@'):
            continue

        feat_m = feature_pattern.match(line)
        if feat_m:
            has_feature = True
            continue

        scen_m = scenario_pattern.match(line)
        if scen_m:
            # Validar escenario previo antes de empezar el siguiente
            if current_scenario is not None:
                if not (has_when and has_then):
                    errors.append(GherkinLintError(
                        line=line_idx,
                        error_type="INCOMPLETE_SCENARIO",
                        message=f"El escenario '{current_scenario}' no contiene la secuencia completa When y Then."
                    ))

            current_scenario = scen_m.group(2)
            scenarios_found += 1
            has_given = False
            has_when = False
            has_then = False
            continue

        step_m = gherkin_step_pattern.match(line)
        if step_m:
            keyword = step_m.group(1).lower()
            if keyword in ['given', 'dado']:
                has_given = True
            elif keyword in ['when', 'cuando']:
                has_when = True
            elif keyword in ['then', 'entonces']:
                has_then = True
        else:
            # Si no es cabecera de historia ni paso reconocido
            if current_scenario and not (line.lower().startswith("como") or line.lower().startswith("quiero") or line.lower().startswith("para")):
                errors.append(GherkinLintError(
                    line=line_idx,
                    step=line,
                    error_type="UNKNOWN_GHERKIN_STEP",
                    message=f"Línea no reconocida como paso Gherkin válido: '{line}'"
                ))

    # Validar el último escenario
    if current_scenario is not None and not (has_when and has_then):
        errors.append(GherkinLintError(
            error_type="INCOMPLETE_SCENARIO",
            message=f"El escenario '{current_scenario}' no contiene la secuencia completa When y Then."
        ))

    if not has_feature:
        errors.append(GherkinLintError(
            error_type="MISSING_FEATURE_KEYWORD",
            message="No se encontró la declaración inicial 'Feature:' o 'Característica:'."
        ))

    if scenarios_found == 0:
        errors.append(GherkinLintError(
            error_type="NO_SCENARIOS_FOUND",
            message="No se encontró ningún escenario de prueba válido."
        ))

    is_valid = len(errors) == 0
    return is_valid, errors, scenarios_found


def format_gherkin_feature(writer_out) -> str:
    """Genera una versión estandarizada e indentada del archivo .feature."""
    if not writer_out:
        return ""

    lines = []
    lines.append(f"Feature: {writer_out.feature_name or writer_out.title}")
    lines.append(f"  {writer_out.gherkin_feature_description or 'Especificación ejecutable generada por el Sistema Multiagente.'}")
    lines.append("")
    lines.append(f"  # {writer_out.user_story.full_text}")
    lines.append("")

    for sc in writer_out.scenarios:
        lines.append(f"  Scenario: {sc.name}")
        for step in sc.steps:
            # Asegurar indentación de 4 espacios
            clean_step = step.strip()
            lines.append(f"    {clean_step}")
        lines.append("")

    return "\n".join(lines).strip()


def validator_node(state: MultiAgentState) -> MultiAgentState:
    """Nodo LangGraph para el Agente Validador de Sintaxis & Formato."""
    writer_out = state.get("writer_output")
    critic_out = state.get("critic_output")
    analyst_out = state.get("analyst_output")
    raw_feature = writer_out.raw_feature_text if writer_out else ""

    is_valid, lint_errors, scenario_count = lint_gherkin_text(raw_feature)
    formatted_feature = format_gherkin_feature(writer_out)

    if is_valid and (critic_out and critic_out.passed):
        status = "APPROVED"
    elif is_valid:
        status = "APPROVED_WITH_WARNINGS"
    else:
        status = "FAILED_LINT"

    structured_json = {
        "title": writer_out.title if writer_out else "N/A",
        "user_story": writer_out.user_story.model_dump() if writer_out else {},
        "business_rules_addressed": writer_out.business_rules_addressed if writer_out else [],
        "scenarios_count": scenario_count,
        "invest_score": critic_out.overall_invest_score if critic_out else 0.0,
        "is_approved_by_critic": critic_out.passed if critic_out else False,
        "iterations_required": state.get("iteration_count", 1),
        "validation_status": status,
        "analyst_summary": analyst_out.domain_summary if analyst_out else ""
    }

    validator_result = ValidatorOutput(
        is_valid_gherkin=is_valid,
        total_scenarios_count=scenario_count,
        lint_errors=lint_errors,
        formatted_gherkin_feature=formatted_feature,
        structured_json=structured_json,
        validation_status=status
    )

    history = state.get("execution_history", [])
    history.append({
        "step": "validator",
        "validation_status": status,
        "scenarios_validated": scenario_count,
        "lint_errors_count": len(lint_errors)
    })

    return {
        **state,
        "validator_output": validator_result,
        "execution_history": history,
        "current_step": "validator"
    }
