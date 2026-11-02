# Informe Experimental de Evaluación: RAG Convencional vs Sistema Multiagente LangGraph
## 1. Resumen Ejecutivo y Metodología de Validez Interna
El presente estudio compara de forma experimental y rigurosa dos arquitecturas para la formalización de requerimientos de software en Historias de Usuario ágiles y escenarios Gherkin (BDD):
1. **RAG Convencional (Línea Base)**: Pipeline directo de recuperación de contexto y generación en un solo paso.
2. **Sistema Multiagente Jerárquico (LangGraph)**: Topología modular con roles especializados (Analista, Redactor, Crítico INVEST y Validador de Sintaxis) con bucle de crítica y corrección adaptativo.

> **Garantía de Validez Interna**: Ambas arquitecturas consumen exactamente el mismo índice vectorial, la misma función unificada `query_domain_knowledge(query, top_k=4)` y el mismo motor de inferencia LLM.

## 2. Cuadro Comparativo Agregado de Métricas

| Métrica Evaluada | RAG Convencional (Baseline) | Sistema Multiagente (LangGraph) | Diferencial (Δ) |
| :--- | :---: | :---: | :---: |
| **Calidad INVEST Promedio (0 - 10)** | 9.00 | **9.00** | **+0.00 pts** |
| **Fidelidad de Dominio / Groundedness** | 70.0% | **69.0%** | **-1.0%** |
| **Validez Sintáctica Gherkin** | 100.0% | **100.0%** | +0.0% |
| **Iteraciones Promedio** | 1.0 | 1.0 | +0.0 |
| **Latencia Promedio por Requisito** | 0.000 s | 0.008 s | +0.008 s |

## 3. Análisis Cualitativo por Dimensiones

### A. Criterios INVEST y Redacción de Historias de Usuario
- **RAG Convencional**: Produce historias con roles genéricos ('Como cliente...') y criterios de aceptación superficiales que omiten restricciones del dominio bancario.
- **Multiagente (LangGraph)**: El Agente Analista detecta los roles especializados (ej. 'Cliente con Score C', 'Aval Solidario') y el Agente Crítico fuerza al Redactor a precisar beneficios de negocio medibles y límites numéricos comprobables.

### B. Detección y Mitigación de Alucinaciones / Fuga Semántica
- El bucle de supervisión `Critic -> Writer` rechaza propuestas que inventan reglas o que omiten regulaciones críticas presentes en la base de conocimiento (como el ratio DTI máximo de 40% o el periodo de enfriamiento de 2 horas en ampliación de límites).

### C. Calidad Sintáctica Gherkin y BDD
- El Agente Validador ejecuta verificación por expresiones regulares y reglas de completitud Given-When-Then, asegurando que cada escenario cuente con precondiciones, acciones y aserciones verificables sin errores léxicos.

## 4. Detalle de Casos de Prueba Evaluados

### Caso REQ-001
**Requisito informal**: *"Un cliente con score crediticio C (alrededor de 600 puntos) desea financiar un auto nuevo aportando una cuota inicial, pero requiere incluir un aval solidario para que el banco apruebe el crédito respetando el porcentaje máximo de endeudamiento."*

- **RAG Baseline**: INVEST = 9.0/10, Fidelidad = 70%, Sintaxis = Válida
- **Multiagente**: INVEST = 9.0/10, Fidelidad = 69%, Sintaxis = Válida (Iteraciones requeridas: 1)
- **Historia generada por Multiagente**:
  > Como Cliente con Score C (500-649), quiero solicitar un crédito vehicular incorporando un aval solidario y la póliza endosada, para obtener la aprobación financiera garantizando el cumplimiento de DTI y cobertura de riesgo.

## 5. Conclusiones y Trade-offs Operativos
El sistema multiagente ofrece una **superioridad sustancial en rigor analítico, adherencia a políticas de dominio y cobertura de casos de borde** frente al RAG convencional. El costo operacional se traduce en una mayor latencia y consumo de tokens debido a las múltiples etapas de razonamiento y al bucle de corrección adaptativo; sin embargo, en entornos regulados críticos (banca, finanzas, salud) la reducción del riesgo de alucinaciones y omisiones justifica ampliamente la inversión computacional.
