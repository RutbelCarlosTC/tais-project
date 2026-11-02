"""
Definición del Estado Compartido del Grafo Multiagente (LangGraph State).
"""
from typing import TypedDict, List, Dict, Any, Optional
from src.models.schemas import (
    DomainDocument,
    AnalystOutput,
    WriterOutput,
    CriticOutput,
    ValidatorOutput
)


class MultiAgentState(TypedDict, total=False):
    """
    Estado global transmitido a lo largo del grafo de ejecución en LangGraph.
    Contiene la entrada original, el contexto recuperado, las salidas de cada agente,
    el conteo de iteraciones del bucle de crítica y el historial de feedback.
    """
    # Entradas
    informal_requirement: str
    top_k: int
    
    # Capa de Dominio Compartida
    retrieved_docs: List[DomainDocument]
    domain_context_text: str
    
    # Salidas de Agentes
    analyst_output: Optional[AnalystOutput]
    writer_output: Optional[WriterOutput]
    critic_output: Optional[CriticOutput]
    validator_output: Optional[ValidatorOutput]
    
    # Control de Ciclos e Iteraciones
    iteration_count: int
    max_iterations: int
    critic_feedback_history: List[str]
    is_approved: bool
    
    # Trazabilidad y Métricas
    execution_history: List[Dict[str, Any]]
    total_tokens_estimated: int
    start_time: float
    execution_time_seconds: float
    current_step: str
