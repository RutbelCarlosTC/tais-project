"""
Orquestación del Sistema Multiagente mediante Grafo de Estados (LangGraph).
Implementa la topología jerárquica con bucle de crítica y corrección (Supervisor / Critique Loop).

Flujo:
[Requisito Informal]
        │
        ▼
┌──────────────────┐
│ Agente Analista  │ ◄─── Consulta RAG (query_domain_knowledge)
└────────┬─────────┘
        │ (Entidades, omisiones, reglas)
        ▼
┌──────────────────┐
│ Agente Redactor  │ ───► Genera HU + Gherkin inicial
└────────┬─────────┘
        │
        ▼
┌──────────────────┐
│ Agente Crítico   │ ◄─── Evalúa INVEST, fidelidad y alucinaciones
└────────┬─────────┘
        │
   ¿Pasa INVEST?
   ├── No (Iteración < 3) ──► Retorna al Agente Redactor con feedback
   └── Sí (o Max Iter)
        │
        ▼
┌──────────────────┐
│ Agente Validador │ ───► Verifica sintaxis Gherkin y emite output final
└──────────────────┘
"""
import time
from typing import Dict, Any, Optional
from langgraph.graph import StateGraph, START, END

from src.config import MAX_CRITIC_ITERATIONS, TOP_K_RETRIEVAL
from src.multiagent.state import MultiAgentState
from src.multiagent.agents.analyst import analyst_node
from src.multiagent.agents.writer import writer_node
from src.multiagent.agents.critic import critic_node
from src.multiagent.agents.validator import validator_node


def iteration_increment_node(state: MultiAgentState) -> MultiAgentState:
    """Nodo intermedio para incrementar el contador de iteraciones en el bucle de crítica."""
    current = state.get("iteration_count", 1)
    next_iter = current + 1
    return {
        **state,
        "iteration_count": next_iter,
        "current_step": f"correction_loop_to_{next_iter}"
    }


def route_after_critic(state: MultiAgentState) -> str:
    """
    Función de enrutamiento condicional post-crítico.
    Verifica si se aprobó el estándar INVEST o si se alcanzó el límite de iteraciones (ej. 3).
    """
    passed = state.get("is_approved", False)
    current_iter = state.get("iteration_count", 1)
    max_iter = state.get("max_iterations", MAX_CRITIC_ITERATIONS)

    if passed:
        return "validator"
    elif current_iter >= max_iter:
        # Alcanzado el límite máximo de intentos: pasar al validador final con advertencias
        return "validator"
    else:
        # Retorna al Agente Redactor mediante el incrementador
        return "increment_iteration"


def build_multiagent_graph():
    """
    Construye y compila el StateGraph de LangGraph con el bucle de crítica.
    """
    workflow = StateGraph(MultiAgentState)

    # 1. Agregar nodos
    workflow.add_node("analyst", analyst_node)
    workflow.add_node("writer", writer_node)
    workflow.add_node("critic", critic_node)
    workflow.add_node("increment_iteration", iteration_increment_node)
    workflow.add_node("validator", validator_node)

    # 2. Configurar aristas y flujo
    workflow.add_edge(START, "analyst")
    workflow.add_edge("analyst", "writer")
    workflow.add_edge("writer", "critic")

    # 3. Enrutamiento condicional desde el Crítico
    workflow.add_conditional_edges(
        "critic",
        route_after_critic,
        {
            "validator": "validator",
            "increment_iteration": "increment_iteration"
        }
    )

    # El incrementador vuelve a enviar al Redactor con el feedback del crítico
    workflow.add_edge("increment_iteration", "writer")

    # El Validador finaliza el grafo
    workflow.add_edge("validator", END)

    return workflow.compile()


class MultiAgentStorySystem:
    """
    Clase envoltorio para ejecutar el grafo de LangGraph de forma limpia y medir tiempos.
    """
    def __init__(self, max_iterations: int = MAX_CRITIC_ITERATIONS):
        self.max_iterations = max_iterations
        self.graph = build_multiagent_graph()

    def run(self, informal_requirement: str, top_k: int = TOP_K_RETRIEVAL) -> MultiAgentState:
        start_time = time.time()

        initial_state: MultiAgentState = {
            "informal_requirement": informal_requirement,
            "top_k": top_k,
            "iteration_count": 1,
            "max_iterations": self.max_iterations,
            "critic_feedback_history": [],
            "execution_history": [],
            "total_tokens_estimated": 0,
            "is_approved": False,
            "start_time": start_time
        }

        # Ejecución del grafo
        final_state = self.graph.invoke(initial_state)

        elapsed = time.time() - start_time
        final_state["execution_time_seconds"] = round(elapsed, 3)

        return final_state
