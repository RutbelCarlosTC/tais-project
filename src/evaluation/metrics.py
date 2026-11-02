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

    # 2. Negotiable
    has_standard_formula = "como" in lower_story and "quiero" in lower_story and "para" in lower_story
    scores["Negotiable"] = 8.5 if has_standard_formula else 5.0

    # 3. Valuable (beneficio explícito)
    benefit_match = re.search(r'para\s+([^\.\n]+)', lower_story)
    if benefit_match and len(benefit_match.group(1).strip()) > 15:
        scores["Valuable"] = 9.5
    elif benefit_match:
        scores["Valuable"] = 7.0
    else:
        scores["Valuable"] = 4.0

    # 4. Estimable (presencia de reglas o parámetros numéricos en escenarios)
    has_params = bool(re.search(r'(\$|\%|\d+\s*(meses|años|días|puntos|usd))', lower_gherkin))
    scores["Estimable"] = 8.5 if has_params else 6.0

    # 5. Small (no es una épica con más de 8 escenarios ni texto kilométrico)
    scenarios_count = len(re.findall(r'Scenario:', gherkin_text, re.IGNORECASE))
    if 1 <= scenarios_count <= 4:
        scores["Small"] = 9.0
    elif scenarios_count > 6:
        scores["Small"] = 5.5
    else:
        scores["Small"] = 7.0

    # 6. Testable (calidad de los pasos Given-When-Then)
    is_valid, errors, sc_found = lint_gherkin_text(gherkin_text)
    if is_valid and sc_found >= 2:
        scores["Testable"] = 9.5
    elif is_valid:
        scores["Testable"] = 8.0
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
    
    # Extraer menciones de códigos normativos (ej. RN-ADM-002, SEC-MFA-001)
    cited_rules = re.findall(r'(?:RN-[A-Z]+-\d{3}|SEC-[A-Z]+-\d{3})', generated_text)
    
    grounded_rules = []
    ungrounded_rules = []

    for rule in cited_rules:
        if rule.lower() in combined_domain_text:
            grounded_rules.append(rule)
        else:
            ungrounded_rules.append(rule)

    # Buscar menciones de porcentajes o cifras críticas (ej. 40%, 20%, 35%, 2 horas)
    ciphers = re.findall(r'(\d+%(?:\s+de\s+cuota)?|\d+\s*(?:horas|meses|usd))', generated_text, re.IGNORECASE)
    grounded_ciphers = []
    ungrounded_ciphers = []
    for c in ciphers:
        if c.lower() in combined_domain_text:
            grounded_ciphers.append(c)
        else:
            ungrounded_ciphers.append(c)

    total_checks = len(cited_rules) + len(ciphers)
    if total_checks == 0:
        # Si la respuesta es genérica y no cita reglas normativas ni cifras del dominio,
        # su fidelidad y especificidad respecto al dominio bancario es baja.
        score = 0.40
    else:
        supported = len(grounded_rules) + len(grounded_ciphers)
        # Ratio de afirmaciones respaldadas
        precision = supported / total_checks
        # Cobertura de reglas normativas presentes en el contexto recuperado
        available_rules = set(re.findall(r'(?:RN-[A-Z]+-\d{3}|SEC-[A-Z]+-\d{3})', combined_domain_text, re.IGNORECASE))
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
