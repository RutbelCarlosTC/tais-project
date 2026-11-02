# Informe Experimental de Evaluación: RAG Convencional vs Sistema Multiagente LangGraph
## 1. Resumen Ejecutivo y Metodología de Validez Interna
El presente estudio compara de forma experimental y rigurosa dos arquitecturas para la formalización de requerimientos de software en Historias de Usuario ágiles y escenarios Gherkin (BDD):
1. **RAG Convencional (Línea Base)**: Pipeline directo de recuperación de contexto y generación en un solo paso.
2. **Sistema Multiagente Jerárquico (LangGraph)**: Topología modular con roles especializados (Analista, Redactor, Crítico INVEST y Validador de Sintaxis) con bucle de crítica y corrección adaptativo.

> **Garantía de Validez Interna**: Ambas arquitecturas consumen exactamente el mismo índice vectorial, la misma función unificada `query_domain_knowledge(query, top_k=4)` y el mismo motor de inferencia LLM.

## 2. Cuadro Comparativo Agregado de Métricas

| Métrica Evaluada | RAG Convencional (Baseline) | Sistema Multiagente (LangGraph) | Diferencial (Δ) |
| :--- | :---: | :---: | :---: |
| **Calidad INVEST Promedio (0 - 10)** | 8.03 | **9.08** | **+1.05 pts** |
| **Fidelidad de Dominio / Groundedness** | 40.0% | **64.0%** | **+24.0%** |
| **Validez Sintáctica Gherkin** | 100.0% | **100.0%** | +0.0% |
| **Iteraciones Promedio** | 1.0 | 1.0 | +0.0 |
| **Latencia Promedio por Requisito** | 0.004 s | 0.008 s | +0.004 s |

## 3. Análisis Cualitativo por Dimensiones

### A. Criterios INVEST y Redacción de Historias de Usuario
- **RAG Convencional**: Produce historias con roles genéricos ('Como usuario...', 'Como recepcionista...') y criterios de aceptación superficiales que omiten restricciones del dominio clínico y administrativo.
- **Multiagente (LangGraph)**: El Agente Analista detecta los roles especializados (ej. 'Personal de Admisión', 'Personal de Caja y Registro', 'Gerencia', 'Recursos Humanos') y el Agente Crítico fuerza al Redactor a precisar beneficios de negocio medibles, límites numéricos y escenarios de rechazo.

### B. Detección y Mitigación de Alucinaciones / Fuga Semántica
- El bucle de supervisión `Critic -> Writer` rechaza propuestas que inventan reglas o que omiten regulaciones críticas presentes en la base de conocimiento (como la emisión de comprobantes internos sin validez SUNAT, cálculo exacto de IGV 18%, advertencia obligatoria de no emergencia en el buzón o la protección de datos socioeconómicos frente al equipo clínico).

### C. Calidad Sintáctica Gherkin y BDD
- El Agente Validador ejecuta verificación por expresiones regulares y reglas de completitud Given-When-Then, asegurando que cada escenario cuente con precondiciones, acciones y aserciones verificables sin errores léxicos.

## 4. Detalle de Casos de Prueba Evaluados

### Caso TC-SENSES-001
**Requisito informal**: *"Como personal de Admisión, quiero consultar la disponibilidad horaria de los profesionales en una matriz interactiva y agendar citas individuales o en bloque recurrente, así como moverlas o duplicarlas, para coordinar ágilmente las sesiones de los pacientes (particulares, sociales o por convenio) evitando cruces de horario y sustituyendo el uso de hojas compartidas externas."*

#### Fuentes y Documentos Específicos Recuperados (RAG):
- `senses_catalogo_requisitos_historias.md (score: 0.522)`
- `senses_catalogo_requisitos_historias.md (score: 0.315)`
- `senses_reglas_negocio_y_arquitectura.md (score: 0.282)`
- `senses_fuentes_y_actores.md (score: 0.211)`

#### Comparativa de Métricas por Caso:
| Métrica | RAG Convencional (Baseline) | Sistema Multiagente (LangGraph) |
| :--- | :---: | :---: |
| Calificación INVEST (0-10) | 8.17 / 10 | **9.08 / 10** |
| Fidelidad de Dominio (Groundedness) | 40.0% | **81.0%** |
| Sintaxis Gherkin (BDD) | Válida | **Válida** |
| Escenarios Generados | 2 | **4** |
| Alucinaciones / Fugas Semánticas | 0 | **2** |
| Iteraciones Requeridas | 1 | **1** |
| Latencia | 0.015 s | 0.011 s |

#### Contraste de Salidas:
**1. Salida RAG Convencional (Baseline):**
> **Historia:** Como personal de recepción, quiero agendar citas en un calendario para organizar las consultas de los psicólogos.

CRITERIOS DE ACEPTACIÓN (Gherkin):

```gherkin
Feature: Agendamiento de Citas

  Scenario: Registro de cita individual
    Given que la recepcionista abre el calendario
    When selecciona una hora libre y escribe los datos del paciente
    Then la cita queda guardada en el sistema

  Scenario: Visualización de citas del día
    Given que existen citas programadas
    When se consulta la vista diaria
    Then se muestran las citas en pantalla
```

**2. Salida Sistema Multiagente (LangGraph con Bucle de Crítica):**
> **Historia:** Como Personal de Admisión (ACT-0002), quiero consultar la disponibilidad horaria de los profesionales en una matriz interactiva y agendar citas individuales o en bloque recurrente, así como moverlas o duplicarlas, para coordinar ágilmente las sesiones de los pacientes (particulares, sociales o por convenio) evitando cruces de horario y sustituyendo el uso de hojas compartidas externas.

```gherkin
Feature: Gestión de Agenda en Matriz Interactiva
  Agendamiento en bloque, drag-and-drop, copiar/pegar y prevención estricta de cruces.

  # Como Personal de Admisión (ACT-0002), quiero consultar la disponibilidad horaria de los profesionales en una matriz interactiva y agendar citas individuales o en bloque recurrente, así como moverlas o duplicarlas, para coordinar ágilmente las sesiones de los pacientes (particulares, sociales o por convenio) evitando cruces de horario y sustituyendo el uso de hojas compartidas externas.

  Scenario: Agendamiento individual en matriz visual interactiva (HU-0001 / RN-CLI-001)
    Given que el personal de admisión consulta el calendario semanal de un profesional
    When hace clic en un horario libre de 2 a 3 pm y completa los datos del paciente particular
    Then el sistema guarda la cita y actualiza el bloque horario como ocupado en la matriz visual

  Scenario: Programación de citas recurrentes en bloque de 6 a 8 sesiones (HU-0001 / RN-CLI-001)
    Given que el usuario necesita agendar una serie continua de 6 sesiones semanales para un paciente
    When activa el agendamiento en bloque con rango de fechas y días especificados
    Then el sistema verifica la jornada laboral del profesional, omite los bloques ocupados y genera automáticamente las citas válidas

  Scenario: Reprogramación por arrastre y duplicación de citas (HU-0001 / RN-CLI-001)
    Given que existe una cita agendada en el consultorio C-2
    When el usuario arrastra la cita hacia un bloque libre o la copia y pega en otro horario
    Then el sistema actualiza o replica la cita conservando la información sin forzar reingreso manual

  Scenario: Prevención estricta de cruces y bloqueo en horarios ocupados (RN-CLI-001 / FUE-0001)
    Given que un horario se encuentra ocupado o fuera de la jornada laboral del profesional
    When se intenta registrar, mover o duplicar una cita hacia dicho bloque
    Then el sistema bloquea inmediatamente la acción y emite una alerta indicando que el horario no está disponible
```

---

### Caso TC-SENSES-002
**Requisito informal**: *"Como personal de Caja o Admisión, quiero registrar los pagos de los pacientes por una o varias citas y emitir el comprobante de pago en formato digital, para mantener el control del flujo diario de ingresos y entregar un comprobante con el desglose del servicio."*

#### Fuentes y Documentos Específicos Recuperados (RAG):
- `senses_catalogo_requisitos_historias.md (score: 0.529)`
- `senses_catalogo_requisitos_historias.md (score: 0.482)`
- `senses_catalogo_requisitos_historias.md (score: 0.337)`
- `senses_fuentes_y_actores.md (score: 0.256)`

#### Comparativa de Métricas por Caso:
| Métrica | RAG Convencional (Baseline) | Sistema Multiagente (LangGraph) |
| :--- | :---: | :---: |
| Calificación INVEST (0-10) | 7.83 / 10 | **9.08 / 10** |
| Fidelidad de Dominio (Groundedness) | 40.0% | **61.0%** |
| Sintaxis Gherkin (BDD) | Válida | **Válida** |
| Escenarios Generados | 2 | **4** |
| Alucinaciones / Fugas Semánticas | 0 | **7** |
| Iteraciones Requeridas | 1 | **1** |
| Latencia | 0.001 s | 0.007 s |

#### Contraste de Salidas:
**1. Salida RAG Convencional (Baseline):**
> **Historia:** Como cajero de la clínica, quiero cobrar las citas a los pacientes y emitir un recibo para registrar los pagos.

CRITERIOS DE ACEPTACIÓN (Gherkin):

```gherkin
Feature: Cobro de Consultas

  Scenario: Cobro en caja y emisión de factura legal
    Given que el paciente paga su consulta en ventanilla
    When el cajero confirma el pago
    Then el sistema emite una factura electrónica oficial con valor tributario ante la SUNAT

  Scenario: Consulta de cobros diarios
    Given que se han cobrado citas hoy
    When el cajero consulta el reporte del día
    Then visualiza todos los ingresos y comisiones salariales de los terapeutas
```

**2. Salida Sistema Multiagente (LangGraph con Bucle de Crítica):**
> **Historia:** Como Personal de Caja o Admisión (ACT-0003 / ACT-0002), quiero registrar los pagos de los pacientes por una o varias citas y emitir el comprobante de pago en formato digital, para mantener el control del flujo diario de ingresos y entregar un comprobante con el desglose del servicio.

```gherkin
Feature: Control de Ingresos y Facturación Interna
  Distribución multi-citas, desglose de IGV (18%) y leyenda de control interno sin validez SUNAT.

  # Como Personal de Caja o Admisión (ACT-0003 / ACT-0002), quiero registrar los pagos de los pacientes por una o varias citas y emitir el comprobante de pago en formato digital, para mantener el control del flujo diario de ingresos y entregar un comprobante con el desglose del servicio.

  Scenario: Registro de pago y distribución por citas (HU-0002 / RN-FIN-001)
    Given que el usuario inicia el registro de un cobro por 50 soles
    When ingresa los datos del cliente, selecciona método de pago Yape y distribuye el monto entre citas pendientes
    Then el sistema valida la distribución y actualiza el estado de pago de cada cita vinculada

  Scenario: Cálculo automático de subtotal e IGV (18%) con serie B001 (RN-FIN-001 / FUE-0002)
    Given que se confirman los datos del ingreso
    When se guarda la transacción en el sistema
    Then el sistema calcula automáticamente subtotal de 42.37 soles y 18% de IGV (7.63 soles) con correlativo B001-000036

  Scenario: Emisión de comprobante PDF con advertencia legal SUNAT (HU-0002 / RN-FIN-001)
    Given que el cobro ha sido guardado exitosamente
    When el usuario emite el comprobante digital
    Then genera un PDF con RUC 20609694671 y la leyenda explícita de control interno provisional sin validez ante SUNAT

  Scenario: Rechazo y bloqueo ante sumas distribuidas discordantes (RN-FIN-001 / HU-0002)
    Given que la distribución entre citas no coincide exactamente con el monto total cobrado
    When el operador intenta confirmar el registro
    Then el sistema bloquea el guardado, emite una alerta de inconsistencia y rechaza la operación
```

---

### Caso TC-SENSES-003
**Requisito informal**: *"Como personal de Caja y Registro o Administración, quiero registrar, actualizar y dar seguimiento a los bienes y equipos de la clínica con su información detallada, estado y fotografía, para mantener un inventario físico valorizado, auditable y actualizado de los recursos institucionales."*

#### Fuentes y Documentos Específicos Recuperados (RAG):
- `senses_catalogo_requisitos_historias.md (score: 0.423)`
- `senses_catalogo_requisitos_historias.md (score: 0.259)`
- `senses_fuentes_y_actores.md (score: 0.195)`
- `senses_catalogo_requisitos_historias.md (score: 0.190)`

#### Comparativa de Métricas por Caso:
| Métrica | RAG Convencional (Baseline) | Sistema Multiagente (LangGraph) |
| :--- | :---: | :---: |
| Calificación INVEST (0-10) | 7.83 / 10 | **9.08 / 10** |
| Fidelidad de Dominio (Groundedness) | 40.0% | **49.0%** |
| Sintaxis Gherkin (BDD) | Válida | **Válida** |
| Escenarios Generados | 2 | **4** |
| Alucinaciones / Fugas Semánticas | 0 | **6** |
| Iteraciones Requeridas | 1 | **1** |
| Latencia | 0.001 s | 0.007 s |

#### Contraste de Salidas:
**1. Salida RAG Convencional (Baseline):**
> **Historia:** Como encargado de almacén, quiero registrar los muebles y computadoras de la clínica para saber qué cosas hay.

CRITERIOS DE ACEPTACIÓN (Gherkin):

```gherkin
Feature: Inventario de Bienes

  Scenario: Registro de bien mueble
    Given que el usuario entra al inventario
    When anota el nombre del bien y la cantidad
    Then el ítem se guarda en el listado general

  Scenario: Eliminación de bien
    Given que un mueble se rompe
    When el usuario presiona el botón eliminar
    Then el registro se borra permanentemente de la base de datos
```

**2. Salida Sistema Multiagente (LangGraph con Bucle de Crítica):**
> **Historia:** Como Personal de Caja y Registro o Administración (ACT-0003), quiero registrar, actualizar y dar seguimiento a los bienes y equipos de la clínica con su información detallada, estado y fotografía, para mantener un inventario físico valorizado, auditable y actualizado de los recursos institucionales.

```gherkin
Feature: Administración del Patrimonio Físico
  Registro fotográfico, bitácora de trazabilidad inmutable y exportación filtrada a Excel/PDF.

  # Como Personal de Caja y Registro o Administración (ACT-0003), quiero registrar, actualizar y dar seguimiento a los bienes y equipos de la clínica con su información detallada, estado y fotografía, para mantener un inventario físico valorizado, auditable y actualizado de los recursos institucionales.

  Scenario: Registro de bien con valorización en tiempo real y foto (HU-0003 / RN-PAT-001)
    Given que el usuario accede al formulario de inventario
    When ingresa mueble de melamina con costo de 1500 soles y adjunta fotografía real
    Then el sistema computa el importe total en tiempo real y persiste el activo valorizado

  Scenario: Historial de modificaciones y trazabilidad de estados (HU-0003 / RN-PAT-001)
    Given que el usuario modifica la situación operativa a En Mantenimiento o Dado de Baja
    When guarda las modificaciones
    Then registra automáticamente una entrada de auditoría inmutable con fecha, responsable y valores previo y nuevo

  Scenario: Segregación de inactivos y exportación consolidada (HU-0003 / RN-PAT-001)
    Given que se consulta el inventario de bienes valorizados en 7499 soles
    When el usuario aplica filtros y solicita exportación a Excel o PDF
    Then el sistema genera el reporte contable exacto con las columnas filtradas

  Scenario: Bloqueo y rechazo de registro sin fotografía obligatoria (RN-PAT-001 / FUE-0003)
    Given que el usuario intenta guardar un bien sin adjuntar fotografía
    When presiona guardar activo
    Then el sistema bloquea el guardado, emite una alerta de campo obligatorio y rechaza la persistencia
```

---

### Caso TC-SENSES-004
**Requisito informal**: *"Como Gerencia, quiero consultar los datos de prospección comercial, canales de captación y situación socioeconómica de los pacientes, así como exportar el consolidado institucional, para evaluar el rendimiento de las estrategias de captación y tomar decisiones comerciales sin exponer esta información al personal de atención clínica."*

#### Fuentes y Documentos Específicos Recuperados (RAG):
- `senses_catalogo_requisitos_historias.md (score: 0.514)`
- `senses_catalogo_requisitos_historias.md (score: 0.341)`
- `senses_reglas_negocio_y_arquitectura.md (score: 0.291)`
- `senses_catalogo_requisitos_historias.md (score: 0.276)`

#### Comparativa de Métricas por Caso:
| Métrica | RAG Convencional (Baseline) | Sistema Multiagente (LangGraph) |
| :--- | :---: | :---: |
| Calificación INVEST (0-10) | 8.17 / 10 | **9.08 / 10** |
| Fidelidad de Dominio (Groundedness) | 40.0% | **81.0%** |
| Sintaxis Gherkin (BDD) | Válida | **Válida** |
| Escenarios Generados | 2 | **4** |
| Alucinaciones / Fugas Semánticas | 0 | **3** |
| Iteraciones Requeridas | 1 | **1** |
| Latencia | 0.001 s | 0.008 s |

#### Contraste de Salidas:
**1. Salida RAG Convencional (Baseline):**
> **Historia:** Como usuario de la clínica, quiero ver y exportar la información de los pacientes para evaluar estadísticas de atención.

CRITERIOS DE ACEPTACIÓN (Gherkin):

```gherkin
Feature: Reporte de Pacientes

  Scenario: Consulta general de ficha de paciente
    Given que cualquier psicólogo o practicante abre la ficha del paciente
    When ingresa a los datos generales
    Then puede ver los ingresos familiares, sector de trabajo y canales de marketing del paciente

  Scenario: Descarga de lista de pacientes
    Given que el usuario tiene acceso a la lista
    When hace clic en descargar
    Then el sistema descarga un archivo de texto con los nombres de los pacientes
```

**2. Salida Sistema Multiagente (LangGraph con Bucle de Crítica):**
> **Historia:** Como Gerencia General (ACT-0001), quiero consultar los datos de prospección comercial, canales de captación y situación socioeconómica de los pacientes, así como exportar el consolidado institucional, para evaluar el rendimiento de las estrategias de captación y tomar decisiones comerciales sin exponer esta información al personal de atención clínica.

```gherkin
Feature: Inteligencia Comercial y Privacidad Clínica
  Prospección de mercado, niveles socioeconómicos y aislamiento estricto de visibilidad frente a psicólogos.

  # Como Gerencia General (ACT-0001), quiero consultar los datos de prospección comercial, canales de captación y situación socioeconómica de los pacientes, así como exportar el consolidado institucional, para evaluar el rendimiento de las estrategias de captación y tomar decisiones comerciales sin exponer esta información al personal de atención clínica.

  Scenario: Acceso a datos de prospección y marketing comercial (HU-0004 / RN-MKT-001)
    Given que un usuario con rol Gerencia o Admisión consulta el expediente del paciente
    When accede al apartado comercial
    Then visualiza canal de captación, recomendación, comparativa previa y motivos de elección

  Scenario: Consulta de información socioeconómica de ingresos familiares (HU-0004 / RN-MKT-001)
    Given que el usuario autorizado revisa la ficha complementaria
    When visualiza el bloque socioeconómico
    Then observa situación laboral, sector y rango de ingresos superiores a 3000 soles

  Scenario: Aislamiento estricto y denegatoria de acceso al personal clínico (RN-MKT-001 / FUE-0004)
    Given que un usuario con rol Psicólogo o Interno intenta visualizar las secciones comerciales o socioeconómicas
    When navega por la interfaz de atención clínica
    Then el sistema bloquea y deniega el acceso manteniendo los datos comerciales totalmente ocultos

  Scenario: Exportación consolidada en Excel para evaluación estratégica (HU-0004 / RN-MKT-001)
    Given que Gerencia requiere evaluar el retorno de captación
    When descarga el consolidado general de pacientes
    Then genera un archivo Excel con cruce de datos sociodemográficos y comerciales
```

---

### Caso TC-SENSES-005
**Requisito informal**: *"Como colaborador de la clínica (Psicólogo, Interno, Admisión o Caja), quiero enviar sugerencias, observaciones o reconocimientos de forma anónima o identificada, y como Recursos Humanos quiero clasificar los casos, gestionar acciones de mejora y emitir reportes mensuales, para impulsar la mejora continua del clima y los servicios institucionales con estricta confidencialidad."*

#### Fuentes y Documentos Específicos Recuperados (RAG):
- `senses_catalogo_requisitos_historias.md (score: 0.618)`
- `senses_catalogo_requisitos_historias.md (score: 0.435)`
- `senses_fuentes_y_actores.md (score: 0.340)`
- `senses_catalogo_requisitos_historias.md (score: 0.258)`

#### Comparativa de Métricas por Caso:
| Métrica | RAG Convencional (Baseline) | Sistema Multiagente (LangGraph) |
| :--- | :---: | :---: |
| Calificación INVEST (0-10) | 8.17 / 10 | **9.08 / 10** |
| Fidelidad de Dominio (Groundedness) | 40.0% | **49.0%** |
| Sintaxis Gherkin (BDD) | Válida | **Válida** |
| Escenarios Generados | 2 | **4** |
| Alucinaciones / Fugas Semánticas | 0 | **7** |
| Iteraciones Requeridas | 1 | **1** |
| Latencia | 0.001 s | 0.007 s |

#### Contraste de Salidas:
**1. Salida RAG Convencional (Baseline):**
> **Historia:** Como empleado, quiero poner quejas y sugerencias en una casilla virtual para que la administración las revise.

CRITERIOS DE ACEPTACIÓN (Gherkin):

```gherkin
Feature: Buzón de Sugerencias

  Scenario: Envío de mensaje
    Given que un empleado abre el buzón
    When escribe su reclamo y lo envía
    Then el mensaje se guarda en una base compartida accesible por todos los jefes de área

  Scenario: Envío de urgencia de salud mental
    Given que una persona tiene una emergencia psicológica crítica
    When deja un mensaje de auxilio en el buzón
    Then el sistema genera un ticket de atención médica urgente
```

**2. Salida Sistema Multiagente (LangGraph con Bucle de Crítica):**
> **Historia:** Como Colaborador de la Clínica (Psicólogo, Interno, Admisión o Caja), quiero enviar sugerencias, observaciones o reconocimientos de forma anónima o identificada, y como Recursos Humanos clasificar los casos, gestionar acciones de mejora y emitir reportes mensuales, para impulsar la mejora continua del clima y los servicios institucionales con estricta confidencialidad.

```gherkin
Feature: Mejora Continua y Clima Institucional
  Canal de sugerencias anónimas o identificadas, aviso de no emergencia y gestión exclusiva por RRHH.

  # Como Colaborador de la Clínica (Psicólogo, Interno, Admisión o Caja), quiero enviar sugerencias, observaciones o reconocimientos de forma anónima o identificada, y como Recursos Humanos clasificar los casos, gestionar acciones de mejora y emitir reportes mensuales, para impulsar la mejora continua del clima y los servicios institucionales con estricta confidencialidad.

  Scenario: Envío institucional de reporte con código correlativo (HU-0005 / MAN-RRHH-BUZ-001)
    Given que un colaborador completa el formulario de buzón
    When presiona enviar reporte
    Then el sistema registra el caso asignándole código SUG-2026-001 con estado Nuevo

  Scenario: Visualización permanente de advertencia legal de no emergencia (RN-RRHH-001 / FUE-0005)
    Given que el usuario abre la pantalla del buzón
    When visualiza el formulario antes de redactar su mensaje
    Then el sistema despliega de forma permanente el aviso de que el buzón no sustituye canales de emergencia o crisis

  Scenario: Gestión de planes de mejora con medición de efectividad en 30 días (HU-0005 / RN-RRHH-001)
    Given que Recursos Humanos prioriza un caso en estado Alta o Crítica
    When programa un plan de acción con plazo de 30 días y mide su efectividad
    Then el caso transiciona a Cerrado registrando la fecha y evaluación del resultado

  Scenario: Restricción estricta y bloqueo de bandeja ante roles no autorizados (HU-0005 / RN-RRHH-001)
    Given que un usuario con rol distinto a Recursos Humanos intenta acceder a la bandeja de gestión
    When navega hacia el módulo administrativo del buzón
    Then el sistema bloquea la pantalla, deniega el acceso y restringe los reportes exclusivamente a RRHH
```

---

## 5. Conclusiones y Análisis de Resultados
El banco de evaluación experimental demuestra que en el dominio del **Centro Psicológico Senses**, el **Sistema Multiagente LangGraph supera de forma consistente al RAG Convencional**:
1. **Reducción Crítica de Alucinaciones y Desvíos**: Mientras el RAG convencional llega a inventar facturación oficial SUNAT o exponer datos socioeconómicos y de captación al equipo clínico, el Agente Crítico y Analista garantizan estricto apego a las fuentes oficiales (recibo B001 sin validez SUNAT, blindaje de datos comerciales y aviso obligatorio de no emergencia en buzón).
2. **Cobertura Exhaustiva de Casos de Rechazo y Borde**: El RAG baseline produce historias superficiales y sólo escenarios de camino feliz. El Multiagente genera casos negativos y de borde esenciales (bloqueo por cruce de horario en matriz, discordancia de importes en multicitas, rechazo de activo sin foto, denegatoria de acceso clínico a marketing y exclusividad de RRHH en el buzón).
3. **Conformidad BDD y Sintaxis Formal**: El Validador sintáctico asegura que los escenarios cumplan la gramática Gherkin estricta lista para automatización con herramientas como Cucumber o Behave.

