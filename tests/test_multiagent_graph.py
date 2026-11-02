"""
Pruebas del Grafo de Estados Multiagente LangGraph.
"""
import pytest
from src.multiagent.graph import MultiAgentStorySystem, build_multiagent_graph
from src.multiagent.agents.validator import lint_gherkin_text


def test_build_multiagent_graph():
    graph = build_multiagent_graph()
    assert graph is not None


def test_multiagent_system_full_flow():
    system = MultiAgentStorySystem(max_iterations=3)
    query = "Cliente con score C solicita crédito vehicular con aval"
    final_state = system.run(informal_requirement=query)

    assert final_state is not None
    assert final_state.get("analyst_output") is not None
    assert final_state.get("writer_output") is not None
    assert final_state.get("critic_output") is not None
    assert final_state.get("validator_output") is not None

    # Verificar que el Analista extrajo roles y reglas
    analyst = final_state["analyst_output"]
    assert len(analyst.identified_actors) > 0
    assert len(analyst.business_rules) > 0

    # Verificar que el Validador formateó la especificación
    validator = final_state["validator_output"]
    assert validator.total_scenarios_count >= 1
    assert "Feature:" in validator.formatted_gherkin_feature


def test_gherkin_linter():
    valid_text = (
        "Feature: Prueba de Linter\n\n"
        "  Scenario: Caso válido\n"
        "    Given que el cliente tiene fondos\n"
        "    When realiza un retiro\n"
        "    Then se actualiza el saldo\n"
    )
    is_valid, errors, count = lint_gherkin_text(valid_text)
    assert is_valid is True
    assert count == 1
    assert len(errors) == 0

    invalid_text = (
        "Scenario: Sin Feature\n"
        "  Given paso\n"
    )
    is_valid_inv, errors_inv, count_inv = lint_gherkin_text(invalid_text)
    assert is_valid_inv is False
    assert len(errors_inv) > 0
