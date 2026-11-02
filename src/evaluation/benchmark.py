"""
Banco de Evaluación Experimental (Benchmarking).
Ejecuta el protocolo de contraste riguroso entre el RAG Convencional y el Sistema Multiagente LangGraph
sobre un conjunto estructurado de casos de prueba representativos del dominio.
"""
from typing import List, Dict, Any
from src.models.schemas import BenchmarkItemResult, BenchmarkReport
from src.baseline_rag.pipeline import ConventionalRagPipeline
from src.multiagent.graph import MultiAgentStorySystem
from src.evaluation.metrics import (
    evaluate_invest_rubric,
    evaluate_domain_faithfulness,
    evaluate_gherkin_syntax
)


BENCHMARK_TEST_SUITE = [
    {
        "id": "TC-SENSES-001",
        "title": "Calendario interactivo para agendamiento individual, en bloque y reprogramación de citas",
        "requirement": (
            "Como personal de Admisión, quiero consultar la disponibilidad horaria de los profesionales "
            "en una matriz interactiva y agendar citas individuales o en bloque recurrente, así como moverlas o "
            "duplicarlas, para coordinar ágilmente las sesiones de los pacientes (particulares, sociales o por convenio) "
            "evitando cruces de horario y sustituyendo el uso de hojas compartidas externas."
        ),
        "expected_sources": [
            "senses_catalogo_requisitos_historias.md (HU-0001)",
            "senses_fuentes_y_actores.md (FUE-0001, ACT-0002)",
            "senses_reglas_negocio_y_arquitectura.md (RN-CLI-001, Appointment)"
        ]
    },
    {
        "id": "TC-SENSES-002",
        "title": "Registro de ingresos y emisión de comprobante de pago interno",
        "requirement": (
            "Como personal de Caja o Admisión, quiero registrar los pagos de los pacientes por una o varias citas "
            "y emitir el comprobante de pago en formato digital, para mantener el control del flujo diario de ingresos "
            "y entregar un comprobante con el desglose del servicio."
        ),
        "expected_sources": [
            "senses_catalogo_requisitos_historias.md (HU-0002)",
            "senses_fuentes_y_actores.md (FUE-0002, ACT-0002, ACT-0003)",
            "senses_reglas_negocio_y_arquitectura.md (RN-FIN-001, PaymentReceipt)"
        ]
    },
    {
        "id": "TC-SENSES-003",
        "title": "Control y administración del inventario de activos de la clínica",
        "requirement": (
            "Como personal de Caja y Registro o Administración, quiero registrar, actualizar y dar seguimiento "
            "a los bienes y equipos de la clínica con su información detallada, estado y fotografía, para mantener un "
            "inventario físico valorizado, auditable y actualizado de los recursos institucionales."
        ),
        "expected_sources": [
            "senses_catalogo_requisitos_historias.md (HU-0003)",
            "senses_fuentes_y_actores.md (FUE-0003, ACT-0003)",
            "senses_reglas_negocio_y_arquitectura.md (RN-PAT-001, Asset)"
        ]
    },
    {
        "id": "TC-SENSES-004",
        "title": "Consulta gerencial y exportación de datos comerciales y socioeconómicos de pacientes",
        "requirement": (
            "Como Gerencia, quiero consultar los datos de prospección comercial, canales de captación y "
            "situación socioeconómica de los pacientes, así como exportar el consolidado institucional, para evaluar el "
            "rendimiento de las estrategias de captación y tomar decisiones comerciales sin exponer esta información al "
            "personal de atención clínica."
        ),
        "expected_sources": [
            "senses_catalogo_requisitos_historias.md (HU-0004)",
            "senses_fuentes_y_actores.md (FUE-0004, ACT-0001, ACT-0004)",
            "senses_reglas_negocio_y_arquitectura.md (RN-MKT-001, PatientMarketingData)"
        ]
    },
    {
        "id": "TC-SENSES-005",
        "title": "Buzón interno de sugerencias, reconocimientos y gestión de planes de mejora",
        "requirement": (
            "Como colaborador de la clínica (Psicólogo, Interno, Admisión o Caja), quiero enviar sugerencias, "
            "observaciones o reconocimientos de forma anónima o identificada, y como Recursos Humanos quiero clasificar los "
            "casos, gestionar acciones de mejora y emitir reportes mensuales, para impulsar la mejora continua del clima y "
            "los servicios institucionales con estricta confidencialidad."
        ),
        "expected_sources": [
            "senses_catalogo_requisitos_historias.md (HU-0005)",
            "senses_fuentes_y_actores.md (FUE-0005, ACT-0006, MAN-RRHH-BUZ-001)",
            "senses_reglas_negocio_y_arquitectura.md (RN-RRHH-001, SuggestionCase)"
        ]
    }
]


class ExperimentalBenchmarkRunner:
    """
    Ejecutor del protocolo experimental de contraste.
    Asegura idénticas condiciones de contexto vectorial, embeddings y LLM.
    """
    def __init__(self, top_k: int = 4, max_agent_iterations: int = 3):
        self.top_k = top_k
        self.rag_pipeline = ConventionalRagPipeline()
        self.multiagent_system = MultiAgentStorySystem(max_iterations=max_agent_iterations)

    def run_benchmark(self, test_suite: List[Dict[str, str]] = None) -> BenchmarkReport:
        suite = test_suite or BENCHMARK_TEST_SUITE
        results: List[BenchmarkItemResult] = []

        print(f"\n================================================================================")
        print(f"  INICIANDO BANCO DE EVALUACIÓN EXPERIMENTAL: RAG BASELINE vs MULTIAGENTE")
        print(f"  Total de casos de prueba: {len(suite)}")
        print(f"================================================================================\n")

        for idx, item in enumerate(suite, start=1):
            req_id = item["id"]
            req_text = item["requirement"]
            print(f"[{idx}/{len(suite)}] Evaluando caso {req_id}: '{item['title']}'...")

            # -------------------------------------------------------------
            # 1. Ejecución del Módulo RAG Base Convencional
            # -------------------------------------------------------------
            rag_output = self.rag_pipeline.run(informal_requirement=req_text, top_k=self.top_k)
            
            rag_invest = evaluate_invest_rubric(rag_output.user_story, rag_output.gherkin_scenarios)
            rag_faith = evaluate_domain_faithfulness(rag_output.raw_response, rag_output.retrieved_documents)
            rag_gherkin = evaluate_gherkin_syntax(rag_output.gherkin_scenarios)

            # -------------------------------------------------------------
            # 2. Ejecución del Sistema Multiagente LangGraph
            # -------------------------------------------------------------
            agent_state = self.multiagent_system.run(informal_requirement=req_text, top_k=self.top_k)
            
            writer_out = agent_state.get("writer_output")
            validator_out = agent_state.get("validator_output")
            critic_out = agent_state.get("critic_output")
            retrieved_docs = agent_state.get("retrieved_docs", [])

            story_text = writer_out.user_story.full_text if writer_out else ""
            scenarios_text = validator_out.formatted_gherkin_feature if validator_out else (writer_out.raw_feature_text if writer_out else "")

            multi_invest = evaluate_invest_rubric(story_text, scenarios_text)
            multi_faith = evaluate_domain_faithfulness(story_text + " " + scenarios_text, retrieved_docs)
            multi_gherkin = evaluate_gherkin_syntax(scenarios_text)

            item_result = BenchmarkItemResult(
                requirement_id=req_id,
                requirement_text=req_text,
                
                # RAG
                rag_invest_score=rag_invest["overall_score"],
                rag_faithfulness_score=rag_faith["faithfulness_score"],
                rag_gherkin_valid=rag_gherkin["is_valid"],
                rag_gherkin_scenarios_count=rag_gherkin["scenario_count"],
                rag_execution_time_sec=rag_output.execution_time_seconds,
                rag_iterations=1,
                rag_tokens_estimated=rag_output.total_tokens_estimated,
                rag_hallucinations_count=rag_faith["hallucinations_count"],
                rag_user_story=rag_output.user_story,
                rag_scenarios_text=rag_output.gherkin_scenarios,
                retrieved_sources=[f"{d.source} (score: {d.score:.3f})" for d in rag_output.retrieved_documents],

                # Multiagente
                multiagent_invest_score=multi_invest["overall_score"],
                multiagent_faithfulness_score=multi_faith["faithfulness_score"],
                multiagent_gherkin_valid=multi_gherkin["is_valid"],
                multiagent_gherkin_scenarios_count=multi_gherkin["scenario_count"],
                multiagent_execution_time_sec=agent_state.get("execution_time_seconds", 0.0),
                multiagent_iterations=agent_state.get("iteration_count", 1),
                multiagent_tokens_estimated=agent_state.get("total_tokens_estimated", 0),
                multiagent_hallucinations_count=multi_faith["hallucinations_count"],
                multiagent_user_story=story_text,
                multiagent_scenarios_text=scenarios_text,
                multiagent_validation_status=validator_out.validation_status if validator_out else "N/A"
            )
            results.append(item_result)
            print(f"  -> RAG INVEST: {item_result.rag_invest_score:.1f}/10 | Multiagente INVEST: {item_result.multiagent_invest_score:.1f}/10 (Iteraciones: {item_result.multiagent_iterations})")

        # Calcular agregados
        total = len(results)
        avg_rag_invest = round(sum(r.rag_invest_score for r in results) / total, 2)
        avg_multi_invest = round(sum(r.multiagent_invest_score for r in results) / total, 2)
        avg_rag_faith = round(sum(r.rag_faithfulness_score for r in results) / total, 2)
        avg_multi_faith = round(sum(r.multiagent_faithfulness_score for r in results) / total, 2)
        
        rag_valid_pct = round((sum(1 for r in results if r.rag_gherkin_valid) / total) * 100, 1)
        multi_valid_pct = round((sum(1 for r in results if r.multiagent_gherkin_valid) / total) * 100, 1)
        
        avg_rag_latency = round(sum(r.rag_execution_time_sec for r in results) / total, 3)
        avg_multi_latency = round(sum(r.multiagent_execution_time_sec for r in results) / total, 3)
        avg_multi_iters = round(sum(r.multiagent_iterations for r in results) / total, 1)

        report = BenchmarkReport(
            total_cases_evaluated=total,
            average_rag_invest=avg_rag_invest,
            average_multiagent_invest=avg_multi_invest,
            average_rag_faithfulness=avg_rag_faith,
            average_multiagent_faithfulness=avg_multi_faith,
            rag_syntax_validity_percentage=rag_valid_pct,
            multiagent_syntax_validity_percentage=multi_valid_pct,
            average_rag_latency_sec=avg_rag_latency,
            average_multiagent_latency_sec=avg_multi_latency,
            average_multiagent_iterations=avg_multi_iters,
            individual_results=results
        )
        return report
