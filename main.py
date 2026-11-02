"""
Punto de entrada principal (CLI) del sistema experimental Multiagente vs RAG Convencional.

Uso:
  python main.py ingest
  python main.py rag "requisito informal"
  python main.py multiagent "requisito informal"
  python main.py benchmark
  python main.py demo
"""
import sys
import argparse
from pathlib import Path

from src.data_layer.document_loader import load_knowledge_base
from src.data_layer.vector_store import VectorStoreManager
from src.data_layer.retriever_tool import query_domain_knowledge
from src.baseline_rag.pipeline import ConventionalRagPipeline
from src.multiagent.graph import MultiAgentStorySystem
from src.evaluation.benchmark import ExperimentalBenchmarkRunner
from src.evaluation.reporter import print_cli_summary, export_benchmark_json, generate_markdown_report


def run_ingest():
    """Indexa la base de conocimiento en la capa de datos compartida."""
    print(">>> Iniciando indexación de la base de conocimiento...")
    docs = load_knowledge_base()
    print(f"Cargados y particionados {len(docs)} chunks normativos (500-800 tokens con 10-15% solapamiento).")
    vm = VectorStoreManager.get_instance()
    vm.reload()
    print("Vector Store indexado exitosamente.")


def run_rag(query: str):
    """Ejecuta el pipeline RAG convencional."""
    print(f"\n--- EJECUCIÓN RAG CONVENCIONAL (BASELINE) ---")
    print(f"Requisito: {query}\n")
    pipeline = ConventionalRagPipeline()
    result = pipeline.run(informal_requirement=query)

    print("DOCUMENTOS RECUPERADOS:")
    for d in result.retrieved_documents:
        print(f" - [{d.source}] (Score: {d.score}): {d.content[:90]}...")

    print("\nHISTORIA DE USUARIO:")
    print(result.user_story)

    print("\nESCENARIOS GHERKIN:")
    print(result.gherkin_scenarios)

    print(f"\nTiempo de ejecución: {result.execution_time_seconds} s | Tokens est.: {result.total_tokens_estimated}")


def run_multiagent(query: str):
    """Ejecuta la orquestación Multiagente LangGraph."""
    print(f"\n--- EJECUCIÓN SISTEMA MULTIAGENTE (LANGGRAPH) ---")
    print(f"Requisito: {query}\n")
    system = MultiAgentStorySystem()
    state = system.run(informal_requirement=query)

    analyst = state.get("analyst_output")
    writer = state.get("writer_output")
    critic = state.get("critic_output")
    validator = state.get("validator_output")

    print("\n1. AGENTE ANALISTA DE DOMINIO:")
    if analyst:
        print(f" - Actores identificados: {', '.join(analyst.identified_actors)}")
        print(f" - Reglas detectadas: {len(analyst.business_rules)}")
        for r in analyst.business_rules:
            print(f"    * {r.code}: {r.description}")
        print(f" - Ambigüedades detectadas: {len(analyst.ambiguities_marked)}")
        for a in analyst.ambiguities_marked:
            print(f"    * {a}")

    print("\n2. AGENTE CRÍTICO INVEST (QA):")
    if critic:
        print(f" - Aprobado: {critic.passed}")
        print(f" - Calificación global INVEST: {critic.overall_invest_score}/10")
        for inv in critic.invest_breakdown:
            print(f"    * {inv.criterion}: {inv.score}/10 - {inv.justification}")
        print(f" - Alucinaciones detectadas: {len(critic.hallucinations_detected)}")

    print(f"\n3. HISTORIAL DE BUCLE DE CORRECCIÓN (Iteraciones: {state.get('iteration_count', 1)}):")
    for idx, f in enumerate(state.get("critic_feedback_history", []), start=1):
        print(f" - Iteración {idx}: {f}")

    print("\n4. AGENTE VALIDADOR (ENTREGA FINAL):")
    if validator:
        print(f" - Estado de validación: {validator.validation_status}")
        print(f" - Escenarios verificados: {validator.total_scenarios_count}")
        print("\nESPECIFICACIÓN GHERKIN FINAL FORMATADA (.feature):")
        print("--------------------------------------------------------------------------------")
        print(validator.formatted_gherkin_feature)
        print("--------------------------------------------------------------------------------")

    print(f"\nTiempo de ejecución: {state.get('execution_time_seconds')} s | Tokens est.: {state.get('total_tokens_estimated')}")


def run_benchmark():
    """Ejecuta el banco de evaluación experimental completo."""
    runner = ExperimentalBenchmarkRunner()
    report = runner.run_benchmark()
    print_cli_summary(report)
    export_benchmark_json(report)
    generate_markdown_report(report)


def run_demo():
    """Ejecuta una demostración comparativa directa sobre un caso representativo."""
    sample_req = (
        "Un cliente con score medio C (alrededor de 600 puntos) desea financiar un auto nuevo "
        "aportando una cuota inicial, pero requiere incluir un aval solidario para que el banco apruebe "
        "el crédito respetando el porcentaje máximo de endeudamiento."
    )
    print("\n" + "=" * 80)
    print("                    DEMOSTRACIÓN COMPARATIVA EN VIVO")
    print("=" * 80)
    print(f"REQUISITO INFORMAL EVALUADO:\n\"{sample_req}\"\n")

    print(">>> 1. Evaluando con Pipeline RAG Convencional...")
    run_rag(sample_req)

    print("\n>>> 2. Evaluando con Sistema Multiagente LangGraph...")
    run_multiagent(sample_req)

    print("\n>>> 3. Ejecutando Banco de Evaluación Experimental sobre el Caso...")
    from src.evaluation.benchmark import BENCHMARK_TEST_SUITE
    runner = ExperimentalBenchmarkRunner()
    report = runner.run_benchmark([BENCHMARK_TEST_SUITE[0]])
    print_cli_summary(report)
    export_benchmark_json(report)
    generate_markdown_report(report)


def main():
    parser = argparse.ArgumentParser(description="Sistema Multiagente LangGraph vs RAG Convencional")
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponibles")

    # Ingest
    subparsers.add_parser("ingest", help="Indexar base de conocimiento compartida")

    # RAG
    rag_parser = subparsers.add_parser("rag", help="Ejecutar RAG convencional")
    rag_parser.add_argument("query", type=str, help="Requisito informal a procesar")

    # Multiagent
    multi_parser = subparsers.add_parser("multiagent", help="Ejecutar Sistema Multiagente LangGraph")
    multi_parser.add_argument("query", type=str, help="Requisito informal a procesar")

    # Benchmark
    subparsers.add_parser("benchmark", help="Ejecutar banco experimental completo")

    # Demo
    subparsers.add_parser("demo", help="Demostración comparativa completa")

    args = parser.parse_args()

    if args.command == "ingest":
        run_ingest()
    elif args.command == "rag":
        run_rag(args.query)
    elif args.command == "multiagent":
        run_multiagent(args.query)
    elif args.command == "benchmark":
        run_benchmark()
    elif args.command == "demo" or args.command is None:
        run_demo()


if __name__ == "__main__":
    main()
