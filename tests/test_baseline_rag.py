"""
Pruebas del Módulo RAG Base Convencional.
"""
import pytest
from src.baseline_rag.pipeline import ConventionalRagPipeline


def test_conventional_rag_pipeline_execution():
    pipeline = ConventionalRagPipeline()
    query = "Cliente con score C solicita crédito vehicular con aval"
    result = pipeline.run(informal_requirement=query)

    assert result is not None
    assert len(result.retrieved_documents) > 0
    assert result.user_story != ""
    assert result.execution_time_seconds > 0
    assert result.total_tokens_estimated > 0
