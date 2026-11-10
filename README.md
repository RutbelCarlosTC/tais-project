# Sistema Multiagente con LangGraph vs RAG Convencional
### Marco Experimental para Contraste Riguroso en Generación de Requisitos Formales e Historias de Usuario

Este proyecto implementa y contrasta experimentalmente dos paradigmas de Inteligencia Artificial para la ingeniería de requisitos de software:
1. **Pipeline RAG Convencional (Baseline)**: Invocación directa en un solo paso contextualizada con búsqueda vectorial.
2. **Sistema Multiagente Jerárquico con Bucle de Crítica (LangGraph)**: Orquestación modular de agentes especializados con supervisión de calidad INVEST, mitigación de alucinaciones y validación de sintaxis BDD (Gherkin).

---

## 1. Arquitectura Desacoplada y Validez Interna

Para garantizar la **validez interna estricta del experimento**, ambas arquitecturas están completamente desacopladas pero consumen **la misma capa de datos, el mismo contexto vectorial y el mismo LLM**:

```
                              ┌──────────────────────────────────────────────┐
                              │  Base de Conocimiento de Dominio (Markdown)  │
                              │  - Catálogo de Requisitos e Historias (HU)   │
                              │  - Fuentes de Información y Actores (FUE/ACT)│
                              │  - Reglas de Negocio y Arquitectura (RN/DAT) │
                              └──────────────────────┬───────────────────────┘
                                                     │ Chunking (500-800 tokens, 10-15% overlap)
                                                     ▼
                                      ┌──────────────────────────────┐
                                      │ Almacén Vectorial (ChromaDB) │
                                      └──────────────┬───────────────┘
                                                     │
                                                     ▼
                                 ┌────────────────────────────────────────┐
                                 │       Herramienta Canónica Única:      │
                                 │ query_domain_knowledge(query, top_k=4) │
                                 └───────────┬────────────────┬───────────┘
                                             │                │
                      ┌──────────────────────┘                └──────────────────────┐
                      ▼                                                              ▼
       ┌─────────────────────────────┐                                ┌─────────────────────────────┐
       │   Módulo RAG Convencional   │                                │  Sistema Multiagente        │
       │   (Baseline en 1 paso)      │                                │  (LangGraph StateGraph)     │
       └──────────────┬──────────────┘                                └──────────────┬──────────────┘
                      │                                                              │
                      └──────────────────────────────┬───────────────────────────────┘
                                                     │
                                                     ▼
                                      ┌──────────────────────────────┐
                                      │ Banco de Evaluación          │
                                      │ Experimental y Benchmarking  │
                                      │ - Rúbrica INVEST (0-10)      │
                                      │ - Fidelidad / Alucinaciones  │
                                      │ - Linter Sintáctico Gherkin  │
                                      │ - Latencia y Consumo Tokens  │
                                      └──────────────────────────────┘
```

---

## 2. Topología del Sistema Multiagente (LangGraph)

El sistema multiagente implementa una topología jerárquica con bucle de crítica y corrección adaptativo:

```
[Requisito Informal en Lenguaje Natural]
                  │
                  ▼
       ┌──────────────────────┐
       │   Agente Analista    │ ◄─── Consulta query_domain_knowledge(query, top_k=4)
       └──────────┬───────────┘
                  │ (Actores, Reglas RN/SEC detectadas, Entidades, Omisiones)
                  ▼
       ┌──────────────────────┐
       │   Agente Redactor    │ ◄─── (Feedback en iteraciones 2 y 3)
       └──────────┬───────────┘
                  │ (Genera HU 'Como/Quiero/Para' + Escenarios Gherkin iniciales)
                  ▼
       ┌──────────────────────┐
       │    Agente Crítico    │ ◄─── Evalúa INVEST, fidelidad normativa y alucinaciones
       └──────────┬───────────┘
                  │
             ¿Pasa INVEST?
             ├── No (Iteración < 3) ──► Retorna al Agente Redactor con feedback accionable
             └── Sí (o Max Iter)
                  │
                  ▼
       ┌──────────────────────┐
       │   Agente Validador   │ ───► Verifica sintaxis BDD (regex) y emite .feature + JSON
       └──────────────────────┘
```

### Roles y Responsabilidades

| Agente | Entrada | Herramientas / Fuentes | Salida |
| :--- | :--- | :--- | :--- |
| **1. Analista de Dominio** | Requisito informal | `query_domain_knowledge` | Requisito desglosado: actores identificados, reglas de negocio detectadas y ambigüedades marcadas. |
| **2. Redactor de Historias (PO)** | Análisis del paso 1 + feedback del Crítico | Razonamiento analítico | Historia de Usuario estándar (`Como [rol] quiero [acción] para [beneficio]`) + escenarios en Gherkin (`Given-When-Then`). |
| **3. Crítico INVEST (QA)** | HU generada + Requisito original + Docs recuperados | Razonamiento y rúbrica | Calificación de criterios INVEST, detección de información sin respaldo (*hallucinations*), omisiones y feedback de corrección. |
| **4. Validador de Sintaxis** | Versión final de la HU y Gherkin | Linter sintáctico Gherkin / regex | Especificación ejecutable final (`.feature` formateado y JSON de entrega). |

---

## 3. Estructura del Proyecto

```
multiagente/
├── .gitignore                         # Reglas de exclusión Git (venv, bytecode, envs, caches)
├── .env.example                       # Plantilla de variables de entorno (OpenAI, Gemini, Ollama o Mock)
├── requirements.txt                   # Dependencias principales
├── data/
│   └── knowledge_base/                # Base de conocimiento (Centro Psicológico Senses)
│       ├── senses_catalogo_requisitos_historias.md     # HU-0001 a HU-0005 con BDD Gherkin
│       ├── senses_fuentes_y_actores.md                 # FUE-0001 a FUE-0005 y ACT-0001 a ACT-0006
│       └── senses_reglas_negocio_y_arquitectura.md     # RN-CLI, RN-FIN, RN-PAT, modelos Prisma
├── src/
│   ├── config.py                      # Configuración central (chunks, top_k, umbrales)
│   ├── data_layer/                    # Capa de datos y recuperación común
│   │   ├── document_loader.py         # Chunks de 500-800 tokens con 10-15% solapamiento
│   │   ├── vector_store.py            # Almacén vectorial con índice semántico BM25/Coseno y ChromaDB
│   │   └── retriever_tool.py          # Función canónica query_domain_knowledge
│   ├── models/
│   │   ├── schemas.py                 # Esquemas Pydantic tipados (Analyst, Writer, Critic, Validator)
│   │   └── llm_factory.py             # Fábrica LLM (OpenAI, Gemini, Ollama y Simulador Determinista)
│   ├── baseline_rag/
│   │   └── pipeline.py                # Pipeline RAG convencional
│   ├── multiagent/
│   │   ├── state.py                   # MultiAgentState para LangGraph
│   │   ├── agents/                    # Nodos de cada rol
│   │   │   ├── analyst.py
│   │   │   ├── writer.py
│   │   │   ├── critic.py
│   │   │   └── validator.py
│   │   └── graph.py                   # Grafo de estados StateGraph con bucle de crítica
│   └── evaluation/                    # Banco experimental
│       ├── metrics.py                 # Rúbrica INVEST, fidelidad y linter sintáctico
│       ├── benchmark.py               # Runner comparativo sistemático
│       └── reporter.py                # Generador de reportes en consola, JSON y Markdown
├── tests/                             # Suite de pruebas unitarias y de integración
│   ├── test_retriever.py
│   ├── test_baseline_rag.py
│   ├── test_multiagent_graph.py
│   └── test_benchmark.py
├── outputs/                           # Artefactos generados (reportes JSON y Markdown)
└── main.py                            # Interfaz CLI unificada
```

---

## 4. Instalación y Uso Rápido

### Requisitos
- Python 3.11 o 3.12
- `pip install -r requirements.txt`

### Comandos de la CLI (`main.py`)

1. **Indexar la base de conocimiento:**
   ```bash
   python main.py ingest
   ```

2. **Ejecutar el Pipeline RAG Convencional (Baseline):**
   ```bash
   python main.py rag "Personal de admisión necesita agendar citas individuales y recurrentes en bloque"
   ```

3. **Ejecutar el Sistema Multiagente LangGraph:**
   ```bash
   python main.py multiagent "Personal de admisión necesita agendar citas individuales y recurrentes en bloque"
   ```

4. **Ejecutar el Banco de Evaluación Experimental Completo:**
   ```bash
   python main.py benchmark
   ```

5. **Ejecutar Demostración Comparativa en Vivo:**
   ```bash
   python main.py demo
   ```

6. **Ejecutar Batería de Pruebas Automatizadas:**
   ```bash
   pytest tests/ -v
   ```

---

## 5. Configuración de Modelos (LLM)

El sistema funciona de inmediato de modo autónomo y reproducible gracias al motor determinista de dominio incorporado (`LLM_PROVIDER=mock`). Para conectar modelos comerciales o locales, configura el archivo `.env`:

```env
# Modo OpenAI
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini

# Modo Google Gemini
LLM_PROVIDER=gemini
GEMINI_API_KEY=AIzaSy...
GEMINI_MODEL=gemini-2.5-flash

# Modo Ollama Local
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3:8b
```

---

## 6. Resultados Experimentales (Benchmark Senses)

Evaluación comparativa ejecutada sobre los 5 requerimientos nucleares del **Centro Psicológico Senses** (`HU-0001` a `HU-0005`) utilizando el modelo **`nvidia/nemotron-3.5-super-vl-120b-a12b`** a través de **NVIDIA NIM** (temperatura = 0.0).

| Métrica Evaluada | RAG Convencional (Baseline) | Sistema Multiagente (LangGraph) | Diferencial (Δ) |
| :--- | :---: | :---: | :---: |
| **Calidad INVEST Promedio (0 - 10)** | 7.61 | **7.65** | **+0.04 pts** |
| **Fidelidad de Dominio (Groundedness)** | **79.0%** | 72.0% | **–7.0%** |
| **Validez Sintáctica Gherkin (BDD)** | 20.0% | **40.0%** | **+20.0%** |
| **Escenarios BDD Promedio por Caso** | 5.0 | **7.2** | **+2.2 escenarios** |
| **Iteraciones Promedio (Crítico)** | 1.0 | **2.6** | **+1.6 iter** |
| **Latencia Promedio por Requisito** | **32.890 s** | 551.249 s | +518.359 s |

> **Conclusión Clave**: El sistema multiagente mejora ligeramente la calidad INVEST (+0.04 pts) y duplica la validez sintáctica Gherkin (de 20.0% a 40.0%), pero reduce la fidelidad al dominio (–7.0%) y incrementa significativamente la latencia y el consumo de tokens debido al bucle de crítica iterativo. Los resultados reflejan valores medidos con el modelo Nemotron real, no datos simulados. Los reportes detallados se guardan automáticamente en `outputs/comparative_evaluation_report.md` y `outputs/benchmark_results.json`.

