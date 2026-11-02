"""
Métricas de evaluación comparativa para contrastar el RAG Convencional vs Sistema Multiagente.
Evalúa:
1. Puntuación de calidad INVEST (0 a 10).
2. Fidelidad de Dominio / Groundedness (0.0 a 1.0) y detección de alucinaciones.
3. Validez sintáctica de Gherkin (True/False, % de escenarios válidos).
4. Cobertura de reglas normativas del dominio.
5. Eficiencia operativa (latencia en segundos y consumo de tokens).
"""
import re
from typing import Dict, Any, List, Tuple
from src.models.schemas import DomainDocument
from src.multiagent.agents.validator import lint_gherkin_text


def evaluate_invest_rubric(user_story_text: str, gherkin_text: str) -> Dict[str, Any]:
    """
    Rúbrica determinista de evaluación INVEST sobre la HU y escenarios producidos.
    Asigna una calificación numérica de 0.0 a 10.0 en cada dimensión:
    - Independent: ausencia de acoplamiento rígido no resuelto
    - Negotiable: presencia de rol, acción y propósito sin micro-gestión técnica en la historia
    - Valuable: beneficio claro y explícito de negocio ('para ...')
    - Estimable: detalle y delimitación claros
    - Small: acotado a un objetivo específico
    - Testable: escenarios Given-When-Then sintácticamente completos
    """
    scores = {}
    lower_story = user_story_text.lower()
    lower_gherkin = gherkin_text.lower()

    # 1. Independent (desacoplada)
    has_isolated_scope = "depende de la historia" not in lower_story and "bloqueado por" not in lower_story
    scores["Independent"] = 9.0 if has_isolated_scope else 5.0

    # 2. Negotiable (fórmula estándar de rol, acción y propósito)
    has_standard_formula = "como" in lower_story and "quiero" in lower_story and "para" in lower_story
    scores["Negotiable"] = 8.5 if has_standard_formula else 5.0

    # 3. Valuable (beneficio explícito de negocio vs implementación puramente técnica)
    benefit_match = re.search(r'para\s+([^\.\n]+)', lower_story)
    has_purely_technical_benefit = bool(re.search(r'(guardar.*base de datos|guardar.*sistema|atenderlo|tomar medidas|no tener que crear)', lower_story))
    if benefit_match and not has_purely_technical_benefit and len(benefit_match.group(1).strip()) > 25:
        scores["Valuable"] = 9.5
    elif benefit_match and not has_purely_technical_benefit:
        scores["Valuable"] = 7.5
    elif benefit_match:
        scores["Valuable"] = 6.0
    else:
        scores["Valuable"] = 3.5

    # 4. Estimable (presencia de reglas, parámetros numéricos o métricas del dominio en escenarios)
    has_params = bool(re.search(r'(\$|\%|\d+\s*(meses|años|días|sesiones|puntos|usd|soles|horas|semanas)|sug-\d{4}|ruc\s*\d+)', lower_gherkin))
    scores["Estimable"] = 9.0 if has_params else 6.0

    # 5. Small (tamaño acotado, entre 1 y 5 escenarios)
    scenarios_count = len(re.findall(r'Scenario:', gherkin_text, re.IGNORECASE))
    if 2 <= scenarios_count <= 4:
        scores["Small"] = 9.0
    elif scenarios_count == 1:
        scores["Small"] = 7.5
    elif scenarios_count > 6:
        scores["Small"] = 5.5
    else:
        scores["Small"] = 7.0

    # 6. Testable (calidad Given-When-Then y cobertura de casos negativos/rechazo BDD)
    is_valid, errors, sc_found = lint_gherkin_text(gherkin_text)
    has_negative_case = bool(re.search(r'(rechaz|bloque|error|alerta|fall|denieg|incomplet|conflicto|expir)', lower_gherkin))
    if is_valid and sc_found >= 2 and has_negative_case:
        scores["Testable"] = 9.5
    elif is_valid and sc_found >= 2:
        scores["Testable"] = 7.0
    elif is_valid:
        scores["Testable"] = 6.0
    elif sc_found > 0:
        scores["Testable"] = 5.0
    else:
        scores["Testable"] = 2.0

    avg_score = round(sum(scores.values()) / len(scores), 2)
    return {
        "overall_score": avg_score,
        "criteria": scores
    }


def evaluate_domain_faithfulness(generated_text: str, domain_docs: List[DomainDocument]) -> Dict[str, Any]:
    """
    Evalúa la fidelidad con la base de conocimiento y detecta afirmaciones sin sustento (alucinaciones).
    Compara las reglas normativas y términos clave citados en el texto contra los fragmentos recuperados.
    """
    if not domain_docs:
        return {"faithfulness_score": 0.5, "hallucinations": [], "grounded_ratio": 0.5}

    combined_domain_text = " ".join([d.content for d in domain_docs]).lower()
    
    # Extraer menciones de códigos normativos (ej. HU-0001, EDU-0002, FUE-0001, ACT-0002, RN-CLI-001, RN-ADM-002)
    rule_pattern = r'(?:HU-\d{4}|EDU-\d{4}|FUE-\d{4}|ACT-\d{4}|RN-[A-Z]+-\d{3}|SEC-[A-Z]+-\d{3}|MAN-[A-Z]+-[A-Z]+-\d{3}|SUG-\d{4}-\d{3})'
    cited_rules = re.findall(rule_pattern, generated_text, re.IGNORECASE)
    
    grounded_rules = []
    ungrounded_rules = []

    for rule in cited_rules:
        if rule.lower() in combined_domain_text:
            grounded_rules.append(rule)
        else:
            ungrounded_rules.append(rule)

    # Buscar menciones de porcentajes o cifras críticas (ej. 18%, 40%, 7 días, 6 a 8 sesiones, 24 horas, 2 horas)
    ciphers = re.findall(r'(\d+%|\d+\s*(?:horas|meses|días|sesiones|usd|soles|puntos))', generated_text, re.IGNORECASE)
    grounded_ciphers = []
    ungrounded_ciphers = []
    for c in ciphers:
        if c.lower() in combined_domain_text:
            grounded_ciphers.append(c)
        else:
            ungrounded_ciphers.append(c)

    total_checks = len(cited_rules) + len(ciphers)
    if total_checks == 0:
        # Si la respuesta es genérica y no cita reglas normativas ni cifras del dominio
        score = 0.40
    else:
        supported = len(grounded_rules) + len(grounded_ciphers)
        # Ratio de afirmaciones respaldadas
        precision = supported / total_checks
        # Cobertura de reglas normativas presentes en el contexto recuperado
        available_rules = set(re.findall(rule_pattern, combined_domain_text, re.IGNORECASE))
        rule_coverage = min(1.0, len(grounded_rules) / max(1, len(available_rules))) if available_rules else 1.0
        # Ponderación: 70% precisión libre de alucinaciones + 30% cobertura de reglas
        score = round((0.70 * precision) + (0.30 * rule_coverage), 2)

    return {
        "faithfulness_score": max(0.0, min(1.0, score)),
        "hallucinations": ungrounded_rules + ungrounded_ciphers,
        "hallucinations_count": len(ungrounded_rules) + len(ungrounded_ciphers),
        "grounded_rules": list(set(grounded_rules))
    }


def evaluate_gherkin_syntax(gherkin_text: str) -> Dict[str, Any]:
    """Evalúa la corrección sintáctica del bloque Gherkin."""
    is_valid, errors, scenario_count = lint_gherkin_text(gherkin_text)
    return {
        "is_valid": is_valid,
        "errors_count": len(errors),
        "errors": [e.model_dump() for e in errors],
        "scenario_count": scenario_count
    }
