"""
Esquemas Pydantic para intercambio tipado entre agentes, pipelines y evaluación.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Esquemas para la Capa de Datos y Recuperación
# ---------------------------------------------------------------------------
class DomainDocument(BaseModel):
    """Documento o fragmento recuperado de la base de conocimiento."""
    doc_id: str
    source: str
    content: str
    score: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# 1. Salida del Agente Analista de Dominio
# ---------------------------------------------------------------------------
class BusinessRuleDetected(BaseModel):
    code: str = Field(description="Código de la regla detectada, ej: RN-ADM-002")
    description: str = Field(description="Descripción y aplicación al requisito")
    source_reference: Optional[str] = Field(default=None, description="Documento o sección de origen")


class AnalystOutput(BaseModel):
    """Requisito desglosado producido por el Agente Analista."""
    identified_actors: List[str] = Field(description="Actores o roles involucrados (ej. Cliente con Score C, Aval Solidario, Operador)")
    business_rules: List[BusinessRuleDetected] = Field(description="Reglas de negocio aplicables extraídas de la base de conocimiento")
    domain_entities: List[str] = Field(description="Entidades clave del dominio (ej. DTI, TCEA, Garantía Mobiliaria)")
    ambiguities_marked: List[str] = Field(description="Ambigüedades detectadas en el requisito informal")
    omissions_detected: List[str] = Field(description="Omisiones críticas detectadas respecto a la política del banco")
    domain_summary: str = Field(description="Resumen contextualizado del dominio recuperado")


# ---------------------------------------------------------------------------
# 2. Salida del Agente Redactor de Historias (Product Owner)
# ---------------------------------------------------------------------------
class GherkinStep(BaseModel):
    keyword: str = Field(description="Given, When, Then, And, But")
    text: str = Field(description="Texto del paso")


class GherkinScenario(BaseModel):
    name: str = Field(description="Nombre descriptivo del escenario")
    scenario_type: str = Field(default="Scenario", description="Scenario o Scenario Outline")
    steps: List[str] = Field(description="Pasos Given-When-Then en formato de texto plano")


class UserStoryStructure(BaseModel):
    role: str = Field(description="Rol o actor: Como [rol]")
    action: str = Field(description="Acción deseada: Quiero [acción]")
    benefit: str = Field(description="Beneficio de negocio: Para [beneficio]")
    full_text: str = Field(description="Texto completo: Como ... quiero ... para ...")


class WriterOutput(BaseModel):
    """Historia de Usuario y criterios de aceptación generados por el Agente Redactor."""
    title: str = Field(description="Título formal de la Historia de Usuario")
    user_story: UserStoryStructure = Field(description="Estructura estándar de la HU")
    feature_name: str = Field(description="Nombre de la funcionalidad para el archivo Gherkin")
    gherkin_feature_description: str = Field(description="Descripción del bloque Feature")
    scenarios: List[GherkinScenario] = Field(description="Escenarios de prueba en Gherkin (Happy path, Reglas de rechazo, Casos borde)")
    raw_feature_text: str = Field(description="Texto completo de la especificación Gherkin (.feature format)")
    business_rules_addressed: List[str] = Field(default_factory=list, description="Códigos de reglas de negocio cubiertas")


# ---------------------------------------------------------------------------
# 3. Salida del Agente Crítico INVEST (QA / Reviewer)
# ---------------------------------------------------------------------------
class InvestCriterionScore(BaseModel):
    criterion: str = Field(description="I (Independent), N (Negotiable), V (Valuable), E (Estimable), S (Small), T (Testable)")
    score: float = Field(description="Puntaje de 0.0 a 10.0")
    justification: str = Field(description="Justificación detallada del puntaje asignado")
    improvement_recommendation: Optional[str] = Field(default=None, description="Sugerencia específica si score < 8")


class CriticOutput(BaseModel):
    """Evaluación rigurosa del Agente Crítico con control de bucle de corrección."""
    passed: bool = Field(description="True si cumple el umbral de calidad INVEST y fidelidad de dominio")
    overall_invest_score: float = Field(description="Promedio ponderado de INVEST (0 a 10)")
    invest_breakdown: List[InvestCriterionScore] = Field(description="Evaluación individual por cada letra de INVEST")
    hallucinations_detected: List[str] = Field(default_factory=list, description="Alertas de información inventada o sin respaldo en la base de conocimiento")
    unwanted_semantic_drifts: List[str] = Field(default_factory=list, description="Desviaciones respecto al requisito informal original")
    missing_domain_rules: List[str] = Field(default_factory=list, description="Reglas del dominio que fueron ignoradas por el Redactor")
    actionable_feedback: str = Field(description="Retroalimentación precisa y accionable para la siguiente iteración del Redactor")


# ---------------------------------------------------------------------------
# 4. Salida del Agente Validador de Sintaxis & Formato
# ---------------------------------------------------------------------------
class GherkinLintError(BaseModel):
    line: Optional[int] = None
    step: Optional[str] = None
    error_type: str
    message: str


class ValidatorOutput(BaseModel):
    """Resultado de la verificación de sintaxis Gherkin y estructuración final."""
    is_valid_gherkin: bool = Field(description="True si pasa todas las reglas de sintaxis Gherkin")
    total_scenarios_count: int = Field(description="Cantidad total de escenarios validados")
    lint_errors: List[GherkinLintError] = Field(default_factory=list, description="Errores de sintaxis detectados")
    formatted_gherkin_feature: str = Field(description="Contenido del archivo .feature final formateado e indentado")
    structured_json: Dict[str, Any] = Field(description="Estructura serializable completa lista para exportación")
    validation_status: str = Field(description="APPROVED, APPROVED_WITH_WARNINGS, o FAILED")


# ---------------------------------------------------------------------------
# 5. Salida del Pipeline RAG Convencional
# ---------------------------------------------------------------------------
class ConventionalRagOutput(BaseModel):
    """Resultado directo producido por el baseline RAG convencional sin multiagente."""
    raw_response: str
    user_story: str
    gherkin_scenarios: str
    retrieved_documents: List[DomainDocument]
    execution_time_seconds: float
    total_tokens_estimated: int


# ---------------------------------------------------------------------------
# 6. Banco de Evaluación Experimental y Métricas Comparativas
# ---------------------------------------------------------------------------
class BenchmarkItemResult(BaseModel):
    """Métricas y resultados para un caso de prueba individual comparado."""
    requirement_id: str
    requirement_text: str
    
    # RAG Convencional
    rag_invest_score: float
    rag_faithfulness_score: float
    rag_gherkin_valid: bool
    rag_gherkin_scenarios_count: int
    rag_execution_time_sec: float
    rag_iterations: int = 1
    rag_tokens_estimated: int
    rag_hallucinations_count: int
    rag_user_story: str
    rag_scenarios_text: str
    retrieved_sources: List[str] = Field(default_factory=list, description="Fuentes y chunks específicos recuperados de la base de conocimiento para el RAG")

    # Sistema Multiagente LangGraph
    multiagent_invest_score: float
    multiagent_faithfulness_score: float
    multiagent_gherkin_valid: bool
    multiagent_gherkin_scenarios_count: int
    multiagent_execution_time_sec: float
    multiagent_iterations: int
    multiagent_tokens_estimated: int
    multiagent_hallucinations_count: int
    multiagent_user_story: str
    multiagent_scenarios_text: str
    multiagent_validation_status: str


class BenchmarkReport(BaseModel):
    """Reporte agregado del banco de evaluación experimental."""
    total_cases_evaluated: int
    average_rag_invest: float
    average_multiagent_invest: float
    average_rag_faithfulness: float
    average_multiagent_faithfulness: float
    rag_syntax_validity_percentage: float
    multiagent_syntax_validity_percentage: float
    average_rag_latency_sec: float
    average_multiagent_latency_sec: float
    average_multiagent_iterations: float
    individual_results: List[BenchmarkItemResult]
