"""
Pruebas del Banco de Evaluación Experimental y Métricas Comparativas.
"""
import pytest
from src.evaluation.benchmark import ExperimentalBenchmarkRunner
from src.evaluation.metrics import evaluate_invest_rubric, evaluate_domain_faithfulness
from src.models.schemas import DomainDocument


def test_evaluate_invest_rubric():
    story = "Como cliente con Score C, quiero solicitar un crédito con aval para comprar un auto sin exceder mi límite."
    gherkin = (
        "Feature: Crédito\n\n"
        "  Scenario: Aprobación\n"
        "    Given que el cliente tiene 25 años\n"
        "    When solicita $10,000 USD\n"
        "    Then se aprueba el crédito\n"
    )
    result = evaluate_invest_rubric(story, gherkin)
    assert result["overall_score"] > 0
    assert "Independent" in result["criteria"]
    assert "Testable" in result["criteria"]


def test_evaluate_domain_faithfulness():
    docs = [
        DomainDocument(
            doc_id="doc1",
            source="manual.md",
            content="La regla RN-ADM-002 exige un DTI máximo del 40% para créditos vehiculares."
        )
    ]
    supported_text = "Se aplica la regla RN-ADM-002 verificando el 40% de endeudamiento."
    res = evaluate_domain_faithfulness(supported_text, docs)
    assert res["faithfulness_score"] >= 0.8
    assert len(res["hallucinations"]) == 0


def test_benchmark_runner_single_case():
    runner = ExperimentalBenchmarkRunner()
    single_case = [{
        "id": "TEST-001",
        "title": "Caso de Prueba",
        "requirement": "Cliente solicita crédito vehicular con aval solidario"
    }]
    report = runner.run_benchmark(test_suite=single_case)

    assert report.total_cases_evaluated == 1
    assert report.average_rag_invest > 0
    assert report.average_multiagent_invest > 0
    assert len(report.individual_results) == 1
