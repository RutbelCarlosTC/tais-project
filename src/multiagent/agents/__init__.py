"""
Módulos de Agentes Especializados del Sistema Multiagente.
"""
from src.multiagent.agents.analyst import analyst_node
from src.multiagent.agents.writer import writer_node
from src.multiagent.agents.critic import critic_node
from src.multiagent.agents.validator import validator_node

__all__ = ["analyst_node", "writer_node", "critic_node", "validator_node"]
