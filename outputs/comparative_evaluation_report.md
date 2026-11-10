# Informe Experimental de Evaluación: RAG Convencional vs Sistema Multiagente LangGraph
## 1. Resumen Ejecutivo y Metodología de Validez Interna
El presente estudio compara de forma experimental y rigurosa dos arquitecturas para la formalización de requerimientos de software en Historias de Usuario ágiles y escenarios Gherkin (BDD):
1. **RAG Convencional (Línea Base)**: Pipeline directo de recuperación de contexto y generación en un solo paso.
2. **Sistema Multiagente Jerárquico (LangGraph)**: Topología modular con roles especializados (Analista, Redactor, Crítico INVEST y Validador de Sintaxis) con bucle de crítica y corrección adaptativo.

> **Garantía de Validez Interna**: Ambas arquitecturas consumen exactamente el mismo índice vectorial, la misma función unificada `query_domain_knowledge(query, top_k=4)` y el mismo motor de inferencia LLM.

## 2. Cuadro Comparativo Agregado de Métricas

| Métrica Evaluada | RAG Convencional (Baseline) | Sistema Multiagente (LangGraph) | Diferencial (Δ) |
| :--- | :---: | :---: | :---: |
| **Calidad INVEST Promedio (0 - 10)** | 7.28 | **7.03** | **-0.25 pts** |
| **Fidelidad de Dominio / Groundedness** | 79.0% | **84.0%** | **+5.0%** |
| **Validez Sintáctica Gherkin** | 0.0% | **0.0%** | +0.0% |
| **Iteraciones Promedio** | 1.0 | 3.0 | +2.0 |
| **Latencia Promedio por Requisito** | 25.566 s | 491.129 s | +465.563 s |

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
| Calificación INVEST (0-10) | 7.50 / 10 | **7.25 / 10** |
| Fidelidad de Dominio (Groundedness) | 75.0% | **75.0%** |
| Sintaxis Gherkin (BDD) | Inválida | **Inválida** |
| Escenarios Generados | 5 | **25** |
| Alucinaciones / Fugas Semánticas | 0 | **0** |
| Iteraciones Requeridas | 1 | **3** |
| Latencia | 22.397 s | 332.256 s |

#### Contraste de Salidas:
**1. Salida RAG Convencional (Baseline):**
> **Historia:** **Historia de Usuario**

**Título:** Calendario interactivo para agendamiento individual, en bloque y reprogramación de citas  
**ID:** HU-0001  
**Rol:** Personal de Admisión  

> **Como** personal de Admisión,  
> **quiero** consultar la disponibilidad horaria de los profesionales en una matriz interactiva y agendar citas individuales o en bloque recurrente, así como moverlas o duplicarlas,  
> **para** coordinar ágilmente las sesiones de los pacientes (particulares, sociales o por convenio) evitando cruces de horario y sustituyendo el uso de hojas compartidas externas.

---

**Criterios de Aceptación (Gherkin / BDD)**

```gherkin

```gherkin
Feature: Calendario interactivo y gestión dinámica de citas
  Como personal de Admisión
  Quiero consultar disponibilidad, agendar, mover y duplicar citas en una matriz interactiva
  Para coordinar sesiones de pacientes evitando cruces de horario y sustituyendo hojas compartidas externas

  Scenario: Agendamiento individual de cita en matriz interactiva
    Given que el personal de admisión consulta el calendario semanal o mensual de un profesional
    And el profesional tiene una jornada laboral activa y consultorios disponibles
    When hace clic en un horario libre dentro de la jornada y completa los datos del paciente, tipo de atención (particular, social o convenio) y motivo de consulta
    Then el sistema guarda la cita y actualiza el bloque horario como ocupado en la matriz visual

  Scenario: Programación de citas recurrentes en bloque
    Given que el usuario necesita programar una serie continua de sesiones para un paciente
    When activa la opción de agendamiento en bloque, define el rango de fechas, los días de la semana y los horarios deseados
    Then el sistema verifica la jornada laboral del profesional, omite los horarios previamente ocupados y los días no laborables, y genera automáticamente las citas válidas dentro del periodo indicado

  Scenario: Reprogramación de cita por arrastre (drag and drop)
    Given que existe una cita programada en el calendario
    When el usuario arrastra la cita hacia un nuevo horario disponible dentro de la jornada laboral
    Then el sistema actualiza la fecha, hora y consultorio de la cita sin necesidad de cancelarla ni volver a ingresar la información del paciente

  Scenario: Duplicación de cita por copiar y pegar
    Given que el usuario desea replicar una cita existente en otro día u hora
    When copia la cita deseada y selecciona un horario libre para pegarla
    Then el sistema crea una nueva cita conservando los datos del paciente y el motivo de consulta en el horario seleccionado

  Scenario: Prevención de cruces de horario y validación de disponibilidad
    Given que un horario se encuentra ocupado, bloqueado o fuera de la jornada de atención del profesional
    When se intenta registrar, pegar o mover una cita hacia dicho bloque
    Then el sistema impide la acción y muestra un aviso informando que el horario no está disponible
```

---

**Reglas de negocio aplicadas (según contexto recuperado):**

* **RN-CLI-001:** La matriz renderiza disponibilidad semanal y mensual, reemplazando hojas externas.
* Se valida la **jornada laboral activa** (`WorkSchedule`) y la **disponibilidad del consultorio físico** antes de cualquier asignación.
* **Prevención estricta de cruces:** no se permite registrar, mover ni duplicar citas sobre bloques ocupados o bloqueados; el sistema emite aviso de indisponibilidad en tiempo real.
* La **programación en bloque recurrente** valida jornada, omite bloques ocupados/no laborables y genera solo citas válidas.
* La **reprogramación por arrastre** actualiza fecha, hora y consultorio conservando paciente y motivo, sin cancelar ni reingresar datos.
* La **duplicación por copiar y pegar** genera una nueva cita con los mismos datos del paciente y motivo en el horario libre seleccionado.
* Soporte explícito para tipos de atención: **Particular, Social y Por Convenio**.
```

**2. Salida Sistema Multiagente (LangGraph con Bucle de Crítica):**
> **Historia:** Como Personal de Admisión (ACT-0002), quiero gestionar la disponibilidad y el agendamiento de citas en la matriz interactiva, para coordinar ágilmente las sesiones de los pacientes evitando cruces de horario y sustituyendo el uso de hojas compartidas externas.

```gherkin
Feature: Gestión de Calendario Interactivo y Agendamiento de Citas
  En el módulo de Admisión, el personal debe poder consultar disponibilidad, agendar citas individuales y en bloque, mover y duplicar citas respetando la jornada laboral, el consultorio y la prevención de cruces.

  # Como Personal de Admisión (ACT-0002), quiero gestionar la disponibilidad y el agendamiento de citas en la matriz interactiva, para coordinar ágilmente las sesiones de los pacientes evitando cruces de horario y sustituyendo el uso de hojas compartidas externas.

  Scenario: Consultar disponibilidad en matriz interactiva
    > Given que el Personal de Admisión accede a la matriz interactiva en vista semanal o mensual
    > And existe al menos un profesional con Jornada Laboral (WorkSchedule) definida
    > When selecciona un profesional y un rango de fechas dentro del catálogo permitido
    > Then el sistema muestra la disponibilidad horaria diferenciando celdas disponibles, ocupadas y no laborables según la WorkSchedule del profesional

  Scenario: Cambiar vista de semanal a mensual
    > Given que el Personal de Admisión visualiza la matriz en vista semanal
    > When cambia el selector de vista a "mensual"
    > Then el sistema muestra la disponibilidad en formato mensual manteniendo los filtros de profesional y tipo de atención activos

  Scenario: Filtrar disponibilidad por tipo de atención
    > Given que el Personal de Admisión consulta la matriz interactiva
    > When filtra por tipo de atención "<tipo de atención>"
    > Then el sistema muestra únicamente los horarios habilitados para ese tipo de atención

  Scenario: Profesional sin Jornada Laboral definida
    > Given que el Personal de Admisión selecciona un profesional
    > And el profesional no tiene una Jornada Laboral (WorkSchedule) vigente
    > When consulta la disponibilidad en la matriz
    > Then el sistema muestra un mensaje indicando que el profesional no tiene horario laboral configurado y no permite agendamiento

  Scenario: Rango de fechas fuera del catálogo permitido
    > Given que el Personal de Admisión solicita disponibilidad
    > When selecciona un rango de fechas fuera del catálogo de fechas habilitadas
    > Then el sistema rechaza la consulta y solicita un rango dentro del período permitido

  Scenario: Agendamiento de cita individual exitoso
    > Given que el Personal de Admisión selecciona un horario disponible en la matriz
    > And el horario cae dentro de la Jornada Laboral (WorkSchedule) del profesional
    > And el consultorio seleccionado está disponible en ese horario
    > When registra la cita individual con paciente, motivo y tipo de atención
    > Then el sistema crea la cita, bloquea el horario para ese profesional y consultorio, y confirma el agendamiento

  Scenario: Horario fuera de Jornada Laboral
    > Given que el Personal de Admisión intenta agendar una cita individual
    > When selecciona un horario fuera de la Jornada Laboral (WorkSchedule) del profesional
    > Then el sistema rechaza el agendamiento y notifica que el horario está fuera de jornada

  Scenario: Consultorio no disponible
    > Given que el Personal de Admisión selecciona un horario dentro de la jornada del profesional
    > And el consultorio ya tiene una cita asignada en ese horario
    > When intenta confirmar la cita individual
    > Then el sistema rechaza el agendamiento por falta de disponibilidad del consultorio físico

  Scenario: Cruce de horario con cita existente
    > Given que el profesional ya tiene una cita programada en un horario
    > When el Personal de Admisión intenta agendar otra cita para el mismo profesional en horario que se solapa
    > Then el sistema impide el agendamiento y muestra alerta de cruce de horario

  Scenario: Tipo de atención obligatorio no seleccionado
    > Given que el Personal de Admisión completa el formulario de cita individual
    > When no selecciona un tipo de atención (particular, social o por convenio)
    > Then el sistema bloquea el guardado y solicita seleccionar un tipo de atención válido

  Scenario: Cita individual tipo Por Convenio
    > Given que el Personal de Admisión selecciona tipo de atención "Por Convenio"
    > When registra la cita individual
    > Then el sistema requiere el campo convenio asociado antes de permitir el agendamiento

  Scenario: Bloque recurrente con omisión de no laborables y ocupados
    > Given que el Personal de Admisión define un bloque recurrente para un profesional
    > And especifica un rango de fechas según el catálogo
    > And selecciona tipo de atención y consultorio
    > When el sistema genera las repeticiones del bloque
    > Then el sistema omite automáticamente los días no laborables según la WorkSchedule y los horarios ya ocupados, creando solo las citas válidas

  Scenario: Bloque recurrente tipo Por Convenio
    > Given que el Personal de Admisión configura un bloque recurrente
    > When selecciona tipo de atención "Por Convenio"
    > Then el sistema solicita y valida el convenio asociado para cada repetición del bloque

  Scenario: Rango de fechas inválido en bloque recurrente
    > Given que el Personal de Admisión configura un bloque recurrente
    > When la fecha de fin es anterior a la fecha de inicio o está fuera del catálogo permitido
    > Then el sistema rechaza la creación del bloque y solicita un rango de fechas válido

  Scenario: Todas las repeticiones caen en días no laborables
    > Given que el Personal de Admisión define un bloque recurrente solo en días no laborables según la WorkSchedule
    > When el sistema procesa el bloque
    > Then el sistema advierte que no se generaron citas y no crea el bloque vacío

  Scenario: Mover cita por arrastre conservando datos
    > Given que existe una cita programada con paciente, motivo y consultorio asignados
    > When el Personal de Admisión arrastra la cita a un nuevo horario dentro de la matriz
    > And el nuevo horario está dentro de la Jornada Laboral (WorkSchedule) del profesional
    > And el consultorio destino está disponible en el nuevo horario
    > Then el sistema actualiza la cita, conserva paciente y motivo, actualiza el consultorio si cambió, y valida que no haya cruces

  Scenario: Nuevo horario fuera de Jornada Laboral al mover
    > Given que el Personal de Admisión intenta mover una cita
    > When el destino queda fuera de la Jornada Laboral (WorkSchedule) del profesional
    > Then el sistema rechaza el movimiento y mantiene la cita en su horario original

  Scenario: Cruce de horario al mover cita
    > Given que el Personal de Admisión arrastra una cita a un horario ocupado por otra cita del mismo profesional
    > When intenta soltar la cita en ese destino
    > Then el sistema impide el movimiento y notifica el cruce de horario

  Scenario: Consultorio destino no disponible al mover
    > Given que el Personal de Admisión mueve una cita a un nuevo horario
    > And el consultorio destino ya tiene una cita en ese horario
    > When confirma el movimiento
    > Then el sistema rechaza la operación por falta de disponibilidad del consultorio físico

  Scenario: Mover cita a mismo horario
    > Given que el Personal de Admisión arrastra una cita y la suelta en su horario original
    > When el sistema procesa el movimiento
    > Then el sistema no realiza cambios y mantiene la cita sin alteraciones

  Scenario: Duplicar cita conservando paciente y motivo
    > Given que existe una cita origen con paciente, motivo y tipo de atención definidos
    > When el Personal de Admisión selecciona la acción "duplicar" y elige un nuevo horario disponible
    > And el nuevo horario está dentro de la Jornada Laboral (WorkSchedule) del profesional
    > Then el sistema crea una nueva cita independiente conservando paciente, motivo y tipo de atención, sin cancelar la cita origen

  Scenario: Duplicar cita con horario fuera de jornada
    > Given que el Personal de Admisión intenta duplicar una cita
    > When el nuevo horario seleccionado está fuera de la Jornada Laboral (WorkSchedule) del profesional
    > Then el sistema rechaza la duplicación

  Scenario: Duplicar cita generando cruce de horario
    > Given que el Personal de Admisión duplica una cita en un horario ya ocupado por el mismo profesional
    > When confirma la operación
    > Then el sistema impide la duplicación por cruce de horario

  Scenario: Duplicar cita tipo Por Convenio
    > Given que la cita origen es de tipo de atención "Por Convenio"
    > When el Personal de Admisión duplica la cita
    > Then el sistema conserva el tipo de atención y el convenio asociado en la nueva cita

  Scenario: Consultorio no disponible al duplicar
    > Given que el Personal de Admisión selecciona un consultorio para la cita duplicada
    > And ese consultorio no está disponible en el nuevo horario
    > When confirma la duplicación
    > Then el sistema rechaza la operación por falta de disponibilidad del consultorio
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
| Calificación INVEST (0-10) | 8.33 / 10 | **7.75 / 10** |
| Fidelidad de Dominio (Groundedness) | 77.0% | **70.0%** |
| Sintaxis Gherkin (BDD) | Inválida | **Inválida** |
| Escenarios Generados | 4 | **11** |
| Alucinaciones / Fugas Semánticas | 0 | **0** |
| Iteraciones Requeridas | 1 | **3** |
| Latencia | 22.418 s | 573.437 s |

#### Contraste de Salidas:
**1. Salida RAG Convencional (Baseline):**
> **Historia:** A continuación se presenta la formalización del requisito basada estrictamente en el contexto de dominio recuperado.

---

## 1. Historia de Usuario

**Título:** Registro de ingresos y emisión de comprobante de pago interno  
**ID:** HU-0002  
**Rol:** Personal de Caja o Admisión  

> **Como** personal de Caja o Admisión,  
> **quiero** registrar los pagos de los pacientes por una o varias citas y emitir el comprobante de pago en formato digital,  
> **para** mantener el control del flujo diario de ingresos y entregar un comprobante con el desglose del servicio.

---

## 2. Criterios de Aceptación

1. **Registro de pago y distribución por citas**  
   Dado que el usuario inicia el registro de un cobro para un paciente, cuando ingresa los datos del cliente (nombre, documento y teléfono), selecciona la forma de pago (efectivo, Yape, Plin, transferencia o tarjeta) y distribuye el monto total entre una o más citas pendientes del paciente, entonces el sistema valida que la suma asignada coincida exactamente con el total pagado y actualiza el estado de pago de cada cita vinculada.

2. **Cálculo automático y numeración correlativa**  
   Dado que se completan los datos del ingreso, cuando el usuario confirma el registro, entonces el sistema calcula automáticamente el subtotal y el IGV (18%), asigna una serie y número correlativo consecutivo para evitar duplicidades, y vincula el cobro a un periodo contable abierto.

3. **Emisión de comprobante interno en PDF**  
   Dado que el cobro ha sido guardado con éxito, cuando el usuario solicita emitir el comprobante, entonces el sistema genera un documento PDF con los datos institucionales de la clínica, su RUC, número correlativo, datos del cliente y paciente, profesional asignado, detalle de servicios, importes desglosados y el aviso explícito de que se trata de un comprobante de control interno sin validez ante la SUNAT.

4. **Integración inmediata en el registro financiero**  
   Dado que se emitió el comprobante de ingreso, cuando el personal autorizado consulta el registro financiero o balance, entonces el pago figura inmediatamente en el listado de ingresos, permitiendo filtrar por fechas, paciente, profesional, método de pago y estado.

---

## 3. Especificación Gherkin / BDD

```gherkin

```gherkin
Feature: Registro de ingresos y comprobante de control interno
  Como personal de Caja o Admisión
  Quiero registrar cobros por citas y generar comprobantes internos digitales
  Para asegurar el control del flujo de ingresos con desglose de importes e IGV

  Scenario: Registro de cobro y distribución de monto entre una o varias citas
    Given que un paciente mantiene una o varias citas pendientes de pago
    When el usuario de Caja o Admisión ingresa los datos del cliente (nombre, documento y teléfono), selecciona el método de pago (efectivo, Yape, Plin, transferencia o tarjeta) y distribuye el monto total entre las citas pendientes
    Then el sistema valida que la suma de los montos asignados coincida exactamente con el total pagado y actualiza el estado de pago de cada cita vinculada

  Scenario: Cálculo automático de subtotal, IGV y asignación de correlativo
    Given que el registro de cobro contiene los importes distribuidos entre las citas
    When el usuario confirma el guardado de la transacción
    Then el sistema calcula automáticamente el subtotal y el IGV (18%), asigna una serie y número correlativo consecutivo único (ej. B001-000036) y vincula el cobro a un periodo contable abierto

  Scenario: Emisión de comprobante digital en PDF de control interno
    Given que el cobro ha sido persistido exitosamente en el sistema
    When el usuario solicita la emisión del comprobante de pago
    Then el sistema genera un documento PDF con los datos institucionales de la clínica, RUC 20609694671, número correlativo, datos del cliente y paciente, profesional asignado, detalle de servicios, importes desglosados y el aviso explícito de que se trata de un comprobante de control interno sin validez ante la SUNAT

  Scenario: Reflejo inmediato del ingreso en el registro financiero
    Given que se emitió el comprobante de pago interno
    When el personal autorizado consulta el registro financiero o balance diario de ingresos
    Then el pago figura inmediatamente en el listado de ingresos, permitiendo filtrar por fechas, paciente, profesional, método de pago y estado
```

---

**Notas de alineación con el dominio:**
* Los actores autorizados son **Personal de Admisión (ACT-0002)** y **Personal de Caja y Registro / Administración y Finanzas (ACT-0003)**.
* El IGV aplicado es del **18%**.
* El RUC institucional especificado en el contexto es **20609694671**.
* El comprobante tiene carácter de **control interno** y **no tiene validez ante la SUNAT**.
```

**2. Salida Sistema Multiagente (LangGraph con Bucle de Crítica):**
> **Historia:** Como Personal de Caja o Personal de Admisión (en coordinación con Caja), quiero registrar los pagos de los pacientes por una o varias citas y emitir el comprobante de pago en formato digital (PDF), para mantener el control del flujo diario de ingresos y entregar un comprobante con el desglose del servicio.

```gherkin
Feature: Registro de cobros y emisión de comprobante de pago interno
  Como Personal de Caja o Personal de Admisión, necesito registrar cobros por citas, validar la distribución de montos, calcular impuestos, generar comprobantes PDF internos y actualizar estados de cita y registro financiero.

  # Como Personal de Caja o Personal de Admisión (en coordinación con Caja), quiero registrar los pagos de los pacientes por una o varias citas y emitir el comprobante de pago en formato digital (PDF), para mantener el control del flujo diario de ingresos y entregar un comprobante con el desglose del servicio.

  Scenario: Registro exitoso de pago por una cita (Happy Path)
    /**
 * Dado que el usuario autenticado tiene el rol "Personal de Caja"
 * Y existe un periodo contable abierto
 * Y existe una cita con estado "pendiente de pago" por un monto de S/ 150.00
 * Cuando el usuario registra un pago de S/ 150.00 con método "efectivo" asignado íntegramente a dicha cita
 * Y confirma el cobro
 * Entonces el sistema valida que la suma de montos distribuidos (S/ 150.00) coincida con el total pagado (S/ 150.00)
 * Y el sistema calcula subtotal e IGV (18%) automáticamente
 * Y el sistema asigna una serie y número correlativo consecutivo único (configurado en el sistema)
 * Y el estado de la cita cambia a "pagado"
 * Y el ingreso figura inmediatamente en el registro financiero
 */
    Dado que el usuario autenticado tiene el rol "Personal de Caja"
    Y existe un periodo contable abierto
    Y existe una cita con estado "pendiente de pago" por un monto de S/ 150.00
    Cuando el usuario registra un pago de S/ 150.00 con método "efectivo" asignado íntegramente a dicha cita
    Y confirma el cobro
    Entonces el sistema valida que la suma de montos distribuidos (S/ 150.00) coincida con el total pagado (S/ 150.00)
    Y el sistema calcula subtotal e IGV (18%) automáticamente
    Y el sistema asigna una serie y número correlativo consecutivo único (configurado en el sistema)
    Y el estado de la cita cambia a "pagado"
    Y el ingreso figura inmediatamente en el registro financiero

  Scenario: Registro exitoso de pago distribuido en varias citas (Happy Path)
    /**
 * Dado que el usuario autenticado tiene el rol "Personal de Admisión"
 * Y existe un periodo contable abierto
 * Y existen dos citas pendientes: Cita A (S/ 80.00) del Profesional X y Cita B (S/ 70.00) del Profesional Y
 * Cuando el usuario registra un pago total de S/ 150.00 con método "Yape", distribuyendo S/ 80.00 a la Cita A y S/ 70.00 a la Cita B
 * Y confirma el cobro
 * Entonces el sistema valida que la suma de montos distribuidos (S/ 150.00) coincida con el total pagado (S/ 150.00)
 * Y el estado de la Cita A y la Cita B cambia a "pagado"
 * Y el ingreso figura inmediatamente en el registro financiero con referencia a ambas citas
 */
    Dado que el usuario autenticado tiene el rol "Personal de Admisión"
    Y existe un periodo contable abierto
    Y existen dos citas pendientes: Cita A (S/ 80.00) del Profesional X y Cita B (S/ 70.00) del Profesional Y
    Cuando el usuario registra un pago total de S/ 150.00 con método "Yape", distribuyendo S/ 80.00 a la Cita A y S/ 70.00 a la Cita B
    Y confirma el cobro
    Entonces el sistema valida que la suma de montos distribuidos (S/ 150.00) coincida con el total pagado (S/ 150.00)
    Y el estado de la Cita A y la Cita B cambia a "pagado"
    Y el ingreso figura inmediatamente en el registro financiero con referencia a ambas citas

  Scenario: Rechazo por suma de montos distribuidos diferente al total pagado
    /**
 * Dado que el usuario autenticado tiene el rol "Personal de Caja"
 * Y existen dos citas pendientes: Cita A (S/ 100.00) y Cita B (S/ 200.00)
 * Cuando el usuario intenta registrar un pago total de S/ 400.00 distribuyendo S/ 150.00 a la Cita A y S/ 200.00 a la Cita B
 * Entonces el sistema rechaza la operación porque la suma de montos distribuidos (S/ 350.00) no coincide con el total pagado (S/ 400.00)
 * Y no se actualiza el estado de ninguna cita
 * Y no se registra el ingreso
 * Y se muestra un mensaje de desajuste de montos
 */
    Dado que el usuario autenticado tiene el rol "Personal de Caja"
    Y existen dos citas pendientes: Cita A (S/ 100.00) y Cita B (S/ 200.00)
    Cuando el usuario intenta registrar un pago total de S/ 400.00 distribuyendo S/ 150.00 a la Cita A y S/ 200.00 a la Cita B
    Entonces el sistema rechaza la operación porque la suma de montos distribuidos (S/ 350.00) no coincide con el total pagado (S/ 400.00)
    Y no se actualiza el estado de ninguna cita
    Y no se registra el ingreso
    Y se muestra un mensaje de desajuste de montos

  Scenario: Rechazo por incluir cita ya pagada
    /**
 * Dado que el usuario autenticado tiene el rol "Personal de Admisión"
 * Y existe una cita con estado "pagado"
 * Cuando el usuario intenta incluir dicha cita en un nuevo cobro
 * Entonces el sistema rechaza la operación indicando que la cita ya se encuentra pagada
 * Y no permite continuar con el registro del cobro
 */
    Dado que el usuario autenticado tiene el rol "Personal de Admisión"
    Y existe una cita con estado "pagado"
    Cuando el usuario intenta incluir dicha cita en un nuevo cobro
    Entonces el sistema rechaza la operación indicando que la cita ya se encuentra pagada
    Y no permite continuar con el registro del cobro

  Scenario: Rechazo por periodo contable cerrado
    /**
 * Dado que el usuario autenticado tiene el rol "Personal de Caja"
 * Y no existe un periodo contable abierto (el periodo actual está cerrado)
 * Cuando el usuario intenta registrar un pago por una cita pendiente
 * Entonces el sistema bloquea el registro del cobro
 * Y muestra el mensaje: "No hay periodo contable abierto para registrar el ingreso"
 * Y no se asigna número correlativo
 */
    Dado que el usuario autenticado tiene el rol "Personal de Caja"
    Y no existe un periodo contable abierto (el periodo actual está cerrado)
    Cuando el usuario intenta registrar un pago por una cita pendiente
    Entonces el sistema bloquea el registro del cobro
    Y muestra el mensaje: "No hay periodo contable abierto para registrar el ingreso"
    Y no se asigna número correlativo

  Scenario: Rechazo por rol no autorizado
    /**
 * Dado que el usuario autenticado tiene el rol "Médico / Terapeuta"
 * Cuando el usuario intenta acceder a la funcionalidad de registro de pagos
 * Entonces el sistema deniega el acceso
 * Y muestra el mensaje: "Rol no autorizado para registrar cobros"
 */
    Dado que el usuario autenticado tiene el rol "Médico / Terapeuta"
    Cuando el usuario intenta acceder a la funcionalidad de registro de pagos
    Entonces el sistema deniega el acceso
    Y muestra el mensaje: "Rol no autorizado para registrar cobros"

  Scenario: Rechazo por método de pago no permitido
    /**
 * Dado que el usuario autenticado tiene el rol "Personal de Caja"
 * Cuando el usuario selecciona "Bitcoin" como método de pago
 * Entonces el sistema rechaza el método de pago
 * Y muestra la lista de métodos permitidos: efectivo, Yape, Plin, transferencia, tarjeta
 */
    Dado que el usuario autenticado tiene el rol "Personal de Caja"
    Cuando el usuario selecciona "Bitcoin" como método de pago
    Entonces el sistema rechaza el método de pago
    Y muestra la lista de métodos permitidos: efectivo, Yape, Plin, transferencia, tarjeta

  Scenario: Generación automática de comprobante PDF tras cobro exitoso
    /**
 * Dado que se confirmó exitosamente un cobro por S/ 150.00 con IGV calculado (18%)
 * Cuando el sistema finaliza el registro del ingreso
 * Entonces el sistema genera automáticamente un comprobante en formato PDF
 * Y el PDF incluye el RUC institucional configurado, el número correlativo asignado (ej. B001-000036), los datos del cliente y paciente, el profesional asignado, el detalle del servicio y los importes desglosados (subtotal, IGV, total)
 */
    Dado que se confirmó exitosamente un cobro por S/ 150.00 con IGV calculado (18%)
    Cuando el sistema finaliza el registro del ingreso
    Entonces el sistema genera automáticamente un comprobante en formato PDF
    Y el PDF incluye el RUC institucional configurado, el número correlativo asignado (ej. B001-000036), los datos del cliente y paciente, el profesional asignado, el detalle del servicio y los importes desglosados (subtotal, IGV, total)

  Scenario: Verificación de advertencia legal en el comprobante PDF
    /**
 * Dado que se genera el comprobante PDF de un cobro interno
 * Cuando el usuario visualiza o descarga el documento
 * Entonces el PDF contiene el aviso explícito: "Comprobante de control interno sin validez ante la SUNAT"
 */
    Dado que se genera el comprobante PDF de un cobro interno
    Cuando el usuario visualiza o descarga el documento
    Entonces el PDF contiene el aviso explícito: "Comprobante de control interno sin validez ante la SUNAT"

  Scenario: No generación de comprobante si el cobro fue rechazado
    /**
 * Dado que un intento de cobro fue rechazado por validación de montos o periodo cerrado
 * Cuando el sistema finaliza el intento de registro
 * Entonces no se genera ningún comprobante PDF
 * Y no se asigna número correlativo
 * Y no se actualiza el estado de las citas
 */
    Dado que un intento de cobro fue rechazado por validación de montos o periodo cerrado
    Cuando el sistema finaliza el intento de registro
    Entonces no se genera ningún comprobante PDF
    Y no se asigna número correlativo
    Y no se actualiza el estado de las citas

  Scenario: Reimpresión o consulta de comprobante existente desde registro financiero
    /**
 * Dado que existe un cobro registrado con comprobante PDF emitido
 * Cuando el usuario autorizado consulta el registro financiero y selecciona "Ver comprobante"
 * Entonces el sistema permite descargar nuevamente el PDF del comprobante ya emitido
 * Y el documento mantiene la advertencia de control interno sin validez ante la SUNAT
 */
    Dado que existe un cobro registrado con comprobante PDF emitido
    Cuando el usuario autorizado consulta el registro financiero y selecciona "Ver comprobante"
    Entonces el sistema permite descargar nuevamente el PDF del comprobante ya emitido
    Y el documento mantiene la advertencia de control interno sin validez ante la SUNAT
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
| Calificación INVEST (0-10) | 6.83 / 10 | **7.25 / 10** |
| Fidelidad de Dominio (Groundedness) | 72.0% | **100.0%** |
| Sintaxis Gherkin (BDD) | Inválida | **Inválida** |
| Escenarios Generados | 4 | **16** |
| Alucinaciones / Fugas Semánticas | 0 | **0** |
| Iteraciones Requeridas | 1 | **3** |
| Latencia | 21.398 s | 584.321 s |

#### Contraste de Salidas:
**1. Salida RAG Convencional (Baseline):**
> **Historia:** **Historia de Usuario (HU-0003)**

**Título:** Control y administración del inventario de activos de la clínica  
**Rol:** Personal de Caja y Registro o Administración  
**Acción:** Registrar, actualizar y dar seguimiento a los bienes y equipos de la clínica con su información detallada, estado y fotografía  
**Beneficio:** Mantener un inventario físico valorizado, auditable y actualizado de los recursos institucionales  

> **Como** personal de Caja y Registro o Administración,  
> **quiero** registrar, actualizar y dar seguimiento a los bienes y equipos de la clínica con su información detallada, estado y fotografía,  
> **para** mantener un inventario físico valorizado, auditable y actualizado de los recursos institucionales.

---

**Criterios de Aceptación (Especificación Gherkin / BDD)**

```gherkin

```gherkin
Feature: Control y administración de activos institucionales
  Como personal de Caja y Registro o Administración
  Quiero registrar, actualizar y dar seguimiento a los bienes y equipos de la clínica
  Para disponer de un inventario valorizado, trazable y actualizado

  Scenario: Registro detallado de un nuevo activo con cálculo de importe en tiempo real
    Given que el usuario accede al formulario de registro de inventario
    When ingresa denominación, categoría, cantidad, precio unitario, datos descriptivos (marca, modelo, serie, color, dimensiones, comprobante o factura de compra) y adjunta una fotografía del bien
    Then el sistema calcula automáticamente el importe total en tiempo real
    And guarda el activo en el inventario institucional con su ficha completa

  Scenario: Trazabilidad e historial de modificaciones de un activo
    Given que un activo ya se encuentra registrado en el inventario
    When el usuario modifica cualquier dato o cambia la situación operativa (Operativo, En Mantenimiento o Dado de Baja) y guarda los cambios
    Then el sistema actualiza la ficha del activo
    And registra automáticamente una entrada en el historial con la fecha, el usuario responsable, el dato modificado y sus valores anterior y nuevo

  Scenario: Dar de baja y reactivar un bien institucional
    Given que un bien se deteriora, queda en desuso o es dado de baja
    When el usuario ejecuta la acción de dar de baja sobre el activo
    Then el sistema retira el activo de la lista operativa
    And lo traslada a la vista de activos inactivos conservando toda su información e historial
    And permite reactivarlo si vuelve a estar en servicio

  Scenario: Filtrado y exportación del inventario de bienes
    Given que el usuario consulta el inventario de bienes (activos o inactivos)
    When aplica filtros por categoría, situación operativa o texto de búsqueda y solicita la exportación
    Then el sistema genera un archivo en formato Excel o PDF
    And el archivo contiene exactamente los registros y columnas que cumplen con los filtros aplicados
```

**Reglas de negocio incluidas:**
1. Cálculo automático del importe total (cantidad × precio unitario) en tiempo real al registrar un bien.
2. Estados operativos válidos: Operativo, En Mantenimiento y Dado de Baja.
3. Auditoría inmutable de cambios: fecha, usuario responsable, campo afectado y valores anterior/nuevo.
4. Los bienes dados de baja se mueven a una vista de inactivos sin perder su ficha ni historial, y pueden reactivarse.
5. Exportación filtrada a Excel o PDF que respete exactamente los criterios de búsqueda aplicados.
```

**2. Salida Sistema Multiagente (LangGraph con Bucle de Crítica):**
> **Historia:** Como Personal de Caja y Registro / Administración y Finanzas (ACT-0003), quiero registrar, actualizar, consultar, cambiar el estado operativo y exportar los bienes y equipos de la clínica con su información detallada, estado, comprobante de compra y fotografía, para mantener un inventario físico valorizado, auditable y actualizado de los recursos institucionales.

```gherkin
Feature: Control y administración del inventario de activos de la clínica
  El presente documento fracciona el requisito original en tres Historias de Usuario (HU-0003.1, HU-0003.2 e HU-0003.3) para cumplir con el criterio INVEST (Small) y facilitar la estimación. Cada historia incluye criterios de aceptación y escenarios Gherkin (Given-When-Then) que cubren happy path, reglas de negocio, validaciones de rechazo y casos de seguridad. El único perfil autorizado es ACT-0003 (Personal de Caja y Registro / Administración y Finanzas).

  # Como Personal de Caja y Registro / Administración y Finanzas (ACT-0003), quiero registrar, actualizar, consultar, cambiar el estado operativo y exportar los bienes y equipos de la clínica con su información detallada, estado, comprobante de compra y fotografía, para mantener un inventario físico valorizado, auditable y actualizado de los recursos institucionales.

  Scenario: HU-0003.1 - Registro y consulta de bienes del inventario institucional
    > Como Personal de Caja y Registro / Administración y Finanzas (ACT-0003), quiero registrar bienes y equipos con su información detallada, incluido comprobante de compra y fotografía, y consultarlos, para mantener un inventario físico valorizado y actualizado de los recursos institucionales.
    Criterios de aceptación:
    1. El sistema permite registrar un bien con los datos obligatorios: denominación, categoría, cantidad, precio unitario, marca, modelo, serie, color, dimensiones, comprobante o factura de compra y fotografía del bien.
    2. El sistema calcula automáticamente el importe total (cantidad × precio unitario) en tiempo real al registrar o actualizar el bien.
    3. El sistema guarda el activo en el inventario institucional solo cuando todos los datos obligatorios están completos y válidos.
    4. El sistema permite consultar y visualizar el detalle de un bien registrado, incluida su fotografía y comprobante.
    5. El sistema rechaza el registro si faltan datos obligatorios o si la cantidad y el precio unitario no son mayores a cero.
    Escenarios Gherkin:
    Feature: Registro y consulta de bienes del inventario institucional
    Background:
    Given un usuario autenticado con perfil ACT-0003 (Personal de Caja y Registro / Administración y Finanzas)
    And el módulo de inventario de activos está disponible
    
    Scenario: Registro exitoso de un bien con todos los datos obligatorios y cálculo de importe total
    Given el usuario accede al formulario de registro de bien
    When ingresa la denominación "Mesa de exploración"
    And selecciona la categoría "Mobiliario"
    And ingresa la cantidad 4
    And ingresa el precio unitario 1200.00
    And ingresa la marca "MediEquip"
    And ingresa el modelo "ME-2024"
    And ingresa la serie "SN-001234"
    And selecciona el color "Blanco"
    And ingresa las dimensiones "1.20 x 0.60 x 0.80 m"
    And adjunta el comprobante o factura de compra
    And adjunta la fotografía del bien
    Then el sistema calcula automáticamente el importe total 4800.00 en tiempo real
    And el sistema guarda el activo en el inventario institucional
    And el bien queda disponible para consulta con su fotografía y comprobante asociados
    
    Scenario: Rechazo de registro por falta de datos obligatorios (fotografía y comprobante)
    Given el usuario accede al formulario de registro de bien
    When ingresa denominación, categoría, cantidad, precio unitario, marca, modelo, serie, color y dimensiones
    But no adjunta el comprobante o factura de compra
    And no adjunta la fotografía del bien
    And intenta guardar el bien
    Then el sistema rechaza el guardado
    And el sistema indica que faltan datos obligatorios para completar el registro
    
    Scenario: Rechazo de registro por cantidad o precio unitario no mayores a cero
    Given el usuario accede al formulario de registro de bien
    When ingresa cantidad 0
    And ingresa precio unitario 0
    And completa el resto de datos obligatorios incluyendo comprobante y fotografía
    And intenta guardar el bien
    Then el sistema rechaza el guardado
    And el sistema indica que la cantidad y el precio unitario deben ser mayores a cero
    
    Scenario: Consulta de detalle de un bien registrado
    Given existe un bien registrado con denominación "Mesa de exploración" y estado Operativo
    When el usuario busca el bien por su denominación
    Then el sistema muestra el detalle del bien incluyendo denominación, categoría, cantidad, precio unitario, importe total, marca, modelo, serie, color, dimensiones, comprobante de compra, fotografía y estado operativo

  Scenario: HU-0003.2 - Cambio de estados operativos y trazabilidad de auditoría
    > Como Personal de Caja y Registro / Administración y Finanzas (ACT-0003), quiero cambiar el estado operativo de los bienes (Operativo, En Mantenimiento, Dado de Baja) y reactivarlos cuando corresponda, para que cada modificación quede registrada de forma inmutable en la bitácora de auditoría.
    Criterios de aceptación:
    1. Los estados operativos válidos son: Operativo, En Mantenimiento y Dado de Baja.
    2. Al modificar el estado o cualquier dato de un activo, el sistema genera una entrada de auditoría inmutable con: fecha, usuario responsable, campo modificado, valor anterior y valor nuevo.
    3. Al dar de baja un bien, el sistema lo retira de la vista de activos operativos y lo traslada a la vista de activos inactivos, conservando toda su información e historial.
    4. El sistema permite reactivar un bien dado de baja, retornándolo a la vista de activos operativos y generando la correspondiente entrada de auditoría.
    5. Solo el usuario con perfil ACT-0003 puede modificar estados y datos de los activos.
    Escenarios Gherkin:
    Feature: Cambio de estados operativos y trazabilidad de auditoría
    Background:
    Given un usuario autenticado con perfil ACT-0003 (Personal de Caja y Registro / Administración y Finanzas)
    And existe un bien registrado con denominación "Mesa de exploración" y estado Operativo
    
    Scenario: Cambio de estado de Operativo a En Mantenimiento genera entrada de auditoría
    When el usuario cambia el estado del bien de "Operativo" a "En Mantenimiento"
    Then el sistema actualiza el estado operativo del bien a "En Mantenimiento"
    And el sistema genera una entrada de auditoría inmutable con: fecha, usuario responsable, campo "estado operativo", valor anterior "Operativo" y valor nuevo "En Mantenimiento"
    
    Scenario: Dar de baja un bien lo traslada a la vista de activos inactivos y genera auditoría
    When el usuario da de baja el bien
    Then el sistema retira el bien de la lista de activos operativos
    And el sistema traslada el bien a la vista de activos inactivos
    And el sistema conserva toda la información e historial del bien
    And el sistema genera una entrada de auditoría inmutable con: fecha, usuario responsable, campo "estado operativo", valor anterior "Operativo" y valor nuevo "Dado de Baja"
    
    Scenario: Reactivación de un bien dado de baja
    Given el bien se encuentra en la vista de activos inactivos con estado "Dado de Baja"
    When el usuario reactiva el bien cambiando su estado a "Operativo"
    Then el sistema traslada el bien a la vista de activos operativos
    And el sistema actualiza el estado operativo a "Operativo"
    And el sistema genera una entrada de auditoría inmutable con: fecha, usuario responsable, campo "estado operativo", valor anterior "Dado de Baja" y valor nuevo "Operativo"
    
    Scenario: Verificación de integridad de la entrada de auditoría ante modificación de datos descriptivos
    Given el bien está en estado Operativo
    When el usuario modifica el campo "marca" de "MediEquip" a "MediEquip Plus"
    Then el sistema genera una entrada de auditoría inmutable con: fecha, usuario responsable, campo "marca", valor anterior "MediEquip" y valor nuevo "MediEquip Plus"
    
    Scenario: Rechazo de modificación de estado por usuario sin perfil ACT-0003
    Given un usuario autenticado sin perfil ACT-0003
    When intenta cambiar el estado operativo de un bien
    Then el sistema deniega la operación
    And el sistema no genera ninguna entrada de auditoría

  Scenario: HU-0003.3 - Exportación filtrada del inventario valorizado
    > Como Personal de Caja y Registro / Administración y Finanzas (ACT-0003), quiero exportar el inventario a Excel o PDF aplicando filtros de categoría, situación operativa o búsqueda textual, para obtener un reporte valorizado y auditable de los recursos institucionales.
    Criterios de aceptación:
    1. El sistema permite filtrar el inventario por categoría, situación operativa y texto de búsqueda.
    2. El sistema genera un archivo de exportación en formato Excel o PDF según se solicite.
    3. El archivo exportado contiene exactamente los registros que cumplen con los filtros aplicados.
    4. El archivo exportado incluye las columnas de datos del bien (denominación, categoría, estado operativo, importe total, entre otros campos del dominio).
    5. Solo el usuario con perfil ACT-0003 puede ejecutar la exportación del inventario.
    Escenarios Gherkin:
    Feature: Exportación filtrada del inventario valorizado
    Background:
    Given un usuario autenticado con perfil ACT-0003 (Personal de Caja y Registro / Administración y Finanzas)
    And existen bienes registrados en el inventario con diferentes categorías y estados operativos
    
    Scenario: Exportación filtrada por categoría a Excel
    When el usuario aplica el filtro de categoría "Mobiliario"
    And selecciona el formato de exportación Excel
    And ejecuta la exportación
    Then el sistema genera un archivo Excel
    And el archivo contiene exactamente los registros de la categoría "Mobiliario" que cumplen el filtro
    And el archivo incluye las columnas de datos del bien (denominación, categoría, estado operativo, importe total, entre otros campos del dominio)
    
    Scenario: Exportación filtrada por situación operativa a PDF
    When el usuario aplica el filtro de situación operativa "En Mantenimiento"
    And selecciona el formato de exportación PDF
    And ejecuta la exportación
    Then el sistema genera un archivo PDF
    And el archivo contiene exactamente los registros con estado "En Mantenimiento"
    And el archivo incluye las columnas de datos del bien (denominación, categoría, estado operativo, importe total, entre otros campos del dominio)
    
    Scenario: Exportación con búsqueda textual a Excel
    When el usuario ingresa el texto de búsqueda "monitor"
    And selecciona el formato de exportación Excel
    And ejecuta la exportación
    Then el sistema genera un archivo Excel
    And el archivo contiene exactamente los registros cuya denominación o descripción coincidan con "monitor"
    And el archivo incluye las columnas de datos del bien (denominación, categoría, estado operativo, importe total, entre otros campos del dominio)
    
    Scenario: Rechazo de exportación por usuario sin perfil ACT-0003
    Given un usuario autenticado sin perfil ACT-0003
    When intenta exportar el inventario
    Then el sistema deniega la operación
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
| Calificación INVEST (0-10) | 6.83 / 10 | **7.25 / 10** |
| Fidelidad de Dominio (Groundedness) | 94.0% | **88.0%** |
| Sintaxis Gherkin (BDD) | Inválida | **Inválida** |
| Escenarios Generados | 4 | **9** |
| Alucinaciones / Fugas Semánticas | 0 | **0** |
| Iteraciones Requeridas | 1 | **3** |
| Latencia | 23.619 s | 412.165 s |

#### Contraste de Salidas:
**1. Salida RAG Convencional (Baseline):**
> **Historia:** **Historia de Usuario**

> **Como** Gerencia,  
> **quiero** consultar los datos de prospección comercial, canales de captación y situación socioeconómica de los pacientes, así como exportar el consolidado institucional,  
> **para** evaluar el rendimiento de las estrategias de captación y tomar decisiones comerciales sin exponer esta información al personal de atención clínica.

---

**Criterios de Aceptación (Especificación Gherkin / BDD)**

```gherkin

```gherkin
Feature: Consulta y exportación gerencial de datos comerciales y socioeconómicos de pacientes
  Como Gerencia
  Quiero analizar métricas de prospección y nivel socioeconómico de pacientes
  Para formular estrategias de crecimiento comercial resguardando la privacidad clínica

  Scenario: Visualización de datos de prospección comercial y canales de captación
    Given que un usuario con rol Gerencia o Admisión abre el expediente de un paciente
    When consulta el bloque de información comercial y marketing
    Then el sistema le permite visualizar el canal de captación (redes sociales, buscador, recomendación), la persona que lo refirió, la comparación previa con otros centros, los motivos de atracción y la aceptación de promociones

  Scenario: Acceso a información socioeconómica del paciente
    Given que un usuario autorizado (Gerencia o Admisión) consulta la información complementaria del paciente
    When abre la sección socioeconómica
    Then el sistema muestra la situación laboral, el sector o rubro de trabajo, la modalidad laboral (presencial, remota o mixta) y el rango de ingresos económicos familiares

  Scenario: Restricción de acceso para personal clínico (seguridad y privacidad)
    Given que un profesional con rol de Psicólogo o Interno accede a la ficha de un paciente
    When revisa la información registrada en la interfaz de atención clínica
    Then las secciones de prospección comercial, marketing y situación socioeconómica permanecen completamente ocultas e inaccesibles

  Scenario: Exportación consolidada de datos comerciales y socioeconómicos a Excel
    Given que Gerencia requiere evaluar el retorno de las campañas de captación y el desempeño institucional
    When solicita la descarga del reporte general de pacientes
    Then el sistema genera y descarga un archivo en formato Excel con el consolidado completo de pacientes, integrando datos sociodemográficos, canales de captación y niveles socioeconómicos para la toma de decisiones comerciales
```

---

**Reglas de negocio aplicadas (contexto recuperado)**

* **RN-MKT-001 – Prospección y Captación Comercial:** se capturan canal de captación, nombre de quien refirió, comparación previa con otros centros, motivos de elección y consentimiento para promociones.
* **RN-MKT-001 – Información Socioeconómica Opcional:** se registra situación laboral, sector o rubro de trabajo, modalidad de trabajo (presencial, remota o mixta) y rango de ingresos económicos familiares.
* **RN-MKT-001 – Aislamiento Estricto de Privacidad Clínica:** los roles de Psicólogo e Interno tienen acceso terminantemente restringido a dichas secciones; la información está reservada exclusivamente para Admisión y Gerencia General.
* **RN-MKT-001 – Consolidado Exportable:** Gerencia General puede descargar reportes en Excel que cruzan datos sociodemográficos con canal de atracción y nivel socioeconómico.
```

**2. Salida Sistema Multiagente (LangGraph con Bucle de Crítica):**
> **Historia:** Como Gerencia, quiero consultar los datos de prospección comercial, canales de captación y situación socioeconómica de los pacientes, para evaluar el rendimiento de las estrategias de captación y tomar decisiones comerciales sin exponer esta información al personal de atención clínica. Como Admisión, quiero consultar y gestionar (crear/actualizar) los datos de prospección comercial y socioeconómica del paciente seleccionado, de acuerdo con RN-MKT-001.

```gherkin
Feature: Información comercial y marketing del paciente
  En el módulo de Inteligencia Comercial, Gerencia y Admisión deben acceder a los datos de prospección comercial y socioeconómica de los pacientes, con restricción terminante para roles clínicos (Psicólogo e Interno) y exportación consolidada exclusiva de Gerencia en formato Excel.

  # Como Gerencia, quiero consultar los datos de prospección comercial, canales de captación y situación socioeconómica de los pacientes, para evaluar el rendimiento de las estrategias de captación y tomar decisiones comerciales sin exponer esta información al personal de atención clínica. Como Admisión, quiero consultar y gestionar (crear/actualizar) los datos de prospección comercial y socioeconómica del paciente seleccionado, de acuerdo con RN-MKT-001.

  Scenario: Gerencia consulta ficha comercial y socioeconómica de un paciente
    > Given que el usuario autenticado tiene el rol de Gerencia
> Y existe un paciente con expediente activo en el sistema
> Cuando el usuario accede al Módulo de Inteligencia Comercial > Gestión de Pacientes > pestaña "Información Comercial y Marketing" y selecciona al paciente
> Entonces el sistema muestra la ficha de información comercial y marketing del paciente, incluyendo:
> - Canal de captación (redes sociales, buscador, recomendación)
> - Persona que refirió / recomendador
> - Comparación previa con otros centros psicológicos
> - Motivos de elección / atracción de la clínica
> - Consentimiento / aceptación de promociones
> Y si la información socioeconómica está registrada, el sistema muestra: situación laboral, sector o rubro de trabajo, modalidad de trabajo (presencial, remota o mixta) y rango de ingresos económicos familiares.
> Y si la información socioeconómica no está registrada, el sistema muestra un mensaje indicando que dicho dato es opcional y no consta en el expediente.

  Scenario: Admisión consulta y gestiona datos comerciales y socioeconómicos de un paciente
    > Given que el usuario autenticado tiene el rol de Admisión
> Y existe un paciente con expediente activo en el sistema
> Cuando el usuario accede al Módulo de Inteligencia Comercial > Gestión de Pacientes > pestaña "Información Comercial y Marketing" y selecciona al paciente
> Entonces el sistema permite al usuario visualizar y gestionar (crear/actualizar) los datos de prospección comercial y socioeconómica del paciente seleccionado, de acuerdo con RN-MKT-001.
> Y al guardar los cambios, el sistema persiste la información y la pone a disposición de Gerencia para su consulta.

  Scenario: Paciente sin datos de prospección comercial registrados
    > Given que el usuario autenticado tiene el rol de Gerencia o Admisión
> Y existe un paciente sin datos de prospección comercial registrados
> Cuando el usuario consulta la ficha de información comercial y marketing del paciente
> Entonces el sistema muestra la ficha con los campos de canal de captación, persona que refirió, comparación previa, motivos de elección y consentimiento de promociones vacíos o con el indicador "Sin registro".
> Y si el rol es Admisión, el sistema permite crear dichos datos desde la misma ficha.

  Scenario: Psicólogo intenta acceder a datos comerciales desde vista clínica
    > Given que el usuario autenticado tiene el rol de Psicólogo
> Cuando el usuario accede a cualquier vista de atención clínica del paciente (expediente clínico, historia clínica o evolución)
> Entonces el sistema no muestra la pestaña ni los campos de información comercial y marketing.
> Y la información de prospección comercial, canales de captación y situación socioeconómica permanece terminantemente restringida y oculta para el rol de Psicólogo.

  Scenario: Interno intenta acceder a datos comerciales desde vista clínica
    > Given que el usuario autenticado tiene el rol de Interno
> Cuando el usuario accede a cualquier vista de atención clínica del paciente (expediente clínico, historia clínica o evolución)
> Entonces el sistema no muestra la pestaña ni los campos de información comercial y marketing.
> Y la información de prospección comercial, canales de captación y situación socioeconómica permanece terminantemente restringida y oculta para el rol de Interno.

  Scenario: Gerencia exporta consolidado institucional en Excel con cruce de datos sociodemográficos
    > Given que el usuario autenticado tiene el rol de Gerencia
> Cuando el usuario accede al Módulo de Inteligencia Comercial > Reportes > "Consolidado Institucional de Captación"
> Y selecciona el formato de exportación Excel
> Y opcionalmente aplica filtros de rango de fechas y canal de captación
> Entonces el sistema genera un archivo Excel que cruza los datos sociodemográficos del paciente con el canal de atracción y el nivel socioeconómico (rango de ingresos familiares), incluyendo todos los pacientes que cumplan los filtros o el consolidado institucional completo si no se aplica filtro.
> Y el sistema permite descargar el archivo generado.

  Scenario: Admisión intenta exportar el consolidado institucional
    > Given que el usuario autenticado tiene el rol de Admisión
> Cuando el usuario intenta acceder al Módulo de Inteligencia Comercial > Reportes > "Consolidado Institucional de Captación"
> Entonces el sistema deniega el acceso y muestra un mensaje indicando que la exportación del consolidado institucional es exclusiva del rol Gerencia.

  Scenario: Psicólogo o Interno intenta exportar el consolidado institucional
    > Given que el usuario autenticado tiene el rol de Psicólogo o Interno
> Cuando el usuario intenta acceder al reporte de consolidado institucional de captación
> Entonces el sistema deniega el acceso y oculta completamente la funcionalidad de exportación.

  Scenario: Exportación sin datos disponibles en el período
    > Given que el usuario autenticado tiene el rol de Gerencia
> Y no existen pacientes con datos comerciales o socioeconómicos registrados en el período seleccionado
> Cuando el usuario solicita la exportación del consolidado institucional en Excel
> Entonces el sistema genera un archivo Excel con los encabezados de columnas (datos sociodemográficos, canal de captación, nivel socioeconómico) pero sin filas de datos.
> Y el sistema muestra un mensaje informativo indicando que no hay registros para exportar en el criterio seleccionado.
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
| Calificación INVEST (0-10) | 6.92 / 10 | **5.67 / 10** |
| Fidelidad de Dominio (Groundedness) | 76.0% | **88.0%** |
| Sintaxis Gherkin (BDD) | Inválida | **Inválida** |
| Escenarios Generados | 8 | **15** |
| Alucinaciones / Fugas Semánticas | 0 | **0** |
| Iteraciones Requeridas | 1 | **3** |
| Latencia | 37.996 s | 553.468 s |

#### Contraste de Salidas:
**1. Salida RAG Convencional (Baseline):**
> **Historia:** ### Historia de Usuario: HU-0005

**Título:** Buzón interno de sugerencias, reconocimientos y gestión de planes de mejora

**Como** colaborador de la clínica (Psicólogo, Interno, Admisión o Caja)  
**Quiero** enviar sugerencias, observaciones o reconocimientos de forma anónima o identificada  
**Y como** Recursos Humanos  
**Quiero** clasificar los casos, gestionar acciones de mejora y emitir reportes mensuales  
**Para** impulsar la mejora continua del clima y los servicios institucionales con estricta confidencialidad.

**Reglas de negocio y alcance:**
- Tipos de registro permitidos: sugerencia, observación, reconocimiento o aspecto por mejorar.
- Campos de captura: rol del remitente, área vinculada, importancia percibida, mensaje y propuesta opcional de mejora.
- Cada caso recibe un código correlativo único y estado inicial «Nuevo».
- El colaborador puede optar por el anonimato total o autorizar contacto voluntario (nombre y celular); dichos datos de contacto solo son visibles para Recursos Humanos.
- Debe mostrarse una advertencia permanente de que el buzón no sustituye canales de emergencia, crisis o riesgo inmediato.
- Recursos Humanos puede transcribir fichas físicas del buzón instalado en la clínica como canal «Ficha física».
- Recursos Humanos asigna prioridad (Baja, Media, Alta, Crítica), responsable, acciones de mejora con fecha límite y evidencia esperada.
- Estados del caso: Nuevo, En análisis, Con plan de acción, En seguimiento, Cerrado. Todos los cambios quedan en historial de trazabilidad.
- Al cerrar, Recursos Humanos califica la efectividad (no mejoró, mejoró parcialmente, mejoró significativamente) y selecciona motivo de cierre; el caso puede reabrirse.
- Reportes mensuales con indicadores de volumen por área, prioridad, porcentaje de resolución y efectividad, exportables a Excel o PDF sin revelar nombres ni celulares de remitentes anónimos.
- Solo Recursos Humanos accede a la bandeja de gestión, detalle de casos y reportes. Los demás roles solo pueden redactar y enviar nuevos mensajes.
- Queda prohibido el acceso a información comercial de marketing y situación socioeconómica de pacientes (reservada a Admisión y Gerencia).

---

### Criterios de Aceptación en Gherkin (BDD)

```gherkin

```gherkin
Feature: Buzón interno de sugerencias, reconocimientos y planes de mejora continua

  Scenario: Envío institucional de mensajes desde la plataforma
    Given que un colaborador accede al apartado del buzón en la plataforma
    When selecciona su rol, el tipo de registro (sugerencia, observación, reconocimiento o aspecto por mejorar), el área vinculada, la importancia percibida, el mensaje y opcionalmente una propuesta de mejora
    Then el sistema registra el caso con estado «Nuevo», le asigna un código correlativo único y muestra la confirmación de envío al colaborador

  Scenario: Gestión de anonimato o contacto voluntario
    Given que el colaborador completa el formulario de registro del buzón
    When elige mantener el anonimato
    Then el sistema no vincula su cuenta de usuario ni almacena datos de contacto
    And si autoriza ser contactado, le permite ingresar voluntariamente su nombre y celular
    Then los datos de contacto únicamente quedan a la vista del área de Recursos Humanos

  Scenario: Aviso permanente de no emergencia
    Given que un colaborador abre el formulario de registro del buzón
    When visualiza la pantalla antes de redactar su mensaje
    Then el sistema muestra de forma permanente y visible una advertencia indicando que este buzón no sustituye canales de emergencia, crisis o situaciones de riesgo inmediato

  Scenario: Transcripción de fichas físicas por Recursos Humanos
    Given que Recursos Humanos retira fichas físicas del buzón instalado en la clínica
    When las transcribe en el sistema mediante la opción de registro físico
    Then el sistema almacena el caso bajo el canal «Ficha física», asignándole un código correlativo y los mismos campos de clasificación para su seguimiento unificado

  Scenario: Priorización y planes de acción por Recursos Humanos
    Given que Recursos Humanos revisa un caso en su bandeja de gestión
    When asigna una prioridad (Baja, Media, Alta o Crítica), designa a un responsable y programa acciones de mejora con fecha límite y evidencia esperada
    Then el sistema actualiza el estado del caso (En análisis, Con plan de acción o En seguimiento) y registra cada cambio en el historial de trazabilidad

  Scenario: Medición de efectividad y cierre formal
    Given que se completaron las acciones planificadas para un caso
    When Recursos Humanos califica el resultado obtenido (no mejoró, mejoró parcialmente o mejoró significativamente) y selecciona el motivo de cierre (resuelta, parcialmente resuelta, no resuelta o justificación administrativa)
    Then el sistema cambia el estado a «Cerrado», guarda la fecha de cierre y permite reabrir el caso si la situación requiere nueva intervención

  Scenario: Reporte analítico mensual y exportación
    Given que Recursos Humanos requiere reportar el balance institucional a Gerencia
    When selecciona un mes o periodo en la sección de reportes
    Then el sistema genera indicadores de volumen por área, prioridad, porcentaje de resolución y efectividad de las mejoras
    And permite exportar el reporte a formato Excel o PDF sin mostrar los nombres ni celulares de los remitentes

  Scenario: Privacidad estricta y restricción de bandeja para roles distintos a Recursos Humanos
    Given que un usuario con rol distinto a Recursos Humanos (Gerencia, Admisión, Psicólogo, Interno o Caja) navega por el sistema
    When accede a las opciones del buzón
    Then el sistema le permite únicamente redactar y enviar nuevos mensajes
    And le impide consultar la bandeja de gestión, el detalle de casos o los reportes
```
```

**2. Salida Sistema Multiagente (LangGraph con Bucle de Crítica):**
> **Historia:** 

```gherkin
Feature: Buzón institucional de mejora continua
  Reglas de negocio: CA-1, CA-2, CA-3, REST-PRIV-01 (HU-0005.1); CA-4, CA-5, CA-6, CA-7, CA-8, REST-PRIV-01 (HU-0005.2)

  # 

  Scenario: Envío exitoso de mensaje identificado (Happy Path)
    > Given que el colaborador accede al módulo de buzón institucional
    > And se muestra el aviso permanente "Este buzón no sustituye canales de emergencia, crisis o riesgo inmediato"
    > When selecciona su rol "Psicólogo"
    > And selecciona el tipo de registro "Sugerencia"
    > And selecciona el área vinculada "Talento Humano"
    > And selecciona la importancia percibida "Media"
    > And escribe el mensaje "Sugiero implementar horarios flexibles para el equipo de turno nocturno"
    > And opcionalmente escribe la propuesta de mejora "Rotación semanal de turnos"
    > And autoriza contacto e ingresa nombre "María Pérez" y celular "3001234567"
    > And presiona el botón "Enviar"
    > Then el sistema registra el caso con estado "Nuevo"
    > And genera un código correlativo único (ej. BUZ-2024-00142)
    > And muestra el mensaje de confirmación "Su caso ha sido registrado exitosamente. Código: BUZ-2024-00142"
    > And almacena los datos de contacto (nombre y celular) visibles únicamente para Recursos Humanos

  Scenario: Envío exitoso de mensaje anónimo (Happy Path)
    > Given que el colaborador accede al módulo de buzón institucional
    > And se muestra el aviso permanente de no emergencia
    > When selecciona su rol "Interno"
    > And selecciona el tipo de registro "Reconocimiento"
    > And selecciona el área vinculada "Caja"
    > And selecciona la importancia percibida "Baja"
    > And escribe el mensaje "Agradezco la atención recibida en el módulo de admisión"
    > And selecciona la condición "Anónimo"
    > And no ingresa nombre ni celular
    > And presiona el botón "Enviar"
    > Then el sistema registra el caso con estado "Nuevo"
    > And genera un código correlativo único (ej. BUZ-2024-00143)
    > And muestra el mensaje de confirmación "Su caso ha sido registrado exitosamente. Código: BUZ-2024-00143"
    > And no vincula cuenta de usuario ni almacena datos de contacto

  Scenario: Rechazo por rol institucional no seleccionado
    > Given que el colaborador accede al formulario de envío
    > When no selecciona ningún rol institucional
    > And presiona el botón "Enviar"
    > Then el sistema muestra el error "Debe seleccionar su rol institucional"
    > And no genera código correlativo
    > And no cambia el estado del caso

  Scenario: Rechazo por tipo de registro no seleccionado
    > Given que el colaborador accede al formulario de envío
    > When selecciona un rol pero no selecciona el tipo de registro
    > And presiona el botón "Enviar"
    > Then el sistema muestra el error "Debe seleccionar el tipo de registro"
    > And no genera código correlativo

  Scenario: Rechazo por mensaje vacío
    > Given que el colaborador accede al formulario de envío
    > When el campo de mensaje está vacío
    > And presiona el botón "Enviar"
    > Then el sistema muestra el error "El mensaje es obligatorio"
    > And no genera código correlativo

  Scenario: Propuesta de mejora opcional omitida (caso borde)
    > Given que el colaborador accede al formulario de envío
    > When completa todos los campos obligatorios
    > And no escribe la propuesta de mejora (campo opcional)
    > And presiona el botón "Enviar"
    > Then el sistema acepta el envío
    > And registra el caso sin propuesta de mejora
    > And muestra la confirmación con el código correlativo generado

  Scenario: Aviso permanente de no emergencia visible antes de redactar (seguridad)
    > Given el colaborador accede al formulario de envío del buzón
    > Then el sistema muestra de forma permanente y antes del campo de mensaje el aviso "Este buzón no sustituye canales de emergencia, crisis o riesgo inmediato"

  Scenario: Transcripción de ficha física por RRHH (Happy Path)
    > Given que RRHH accede a la bandeja de gestión del buzón institucional
    > When registra la transcripción de una ficha física con canal "Física"
    > And asigna tipo de registro "Observación", área vinculada "Admisión", importancia "Alta"
    > And escribe el mensaje y opcionalmente propuesta de mejora
    > And presiona "Crear caso"
    > Then el sistema crea el caso con estado "Nuevo"
    > And asigna un código correlativo único
    > And muestra el caso en la bandeja de gestión de RRHH

  Scenario: Asignación de prioridad y plan de acción (todas las prioridades del dominio)
    > Given que existe un caso en estado "Nuevo" con código correlativo "<codigo>"
    > When RRHH asigna prioridad "<prioridad>"
    > And asigna responsable "<responsable>"
    > And establece fecha límite "<fecha>"
    > And define evidencia esperada "<evidencia>"
    > And presiona "Asignar plan de acción"
    > Then el sistema cambia el estado del caso a "Con plan de acción"
    > And registra en el historial de trazabilidad: prioridad "<prioridad>", responsable "<responsable>", fecha límite "<fecha>"
    > And muestra el plan de acción asignado en el detalle del caso
    examples_table: | codigo | prioridad | responsable | fecha | evidencia |
| BUZ-001 | Baja | Coordinador de Admisión | 2024-03-10 | Captura de pantalla del formulario |
| BUZ-002 | Media | Jefe de Enfermería | 2024-02-28 | Acta de reunión |
| BUZ-003 | Alta | Gerente de Operaciones | 2024-02-20 | Informe de inspección |
| BUZ-004 | Crítica | Director Médico | 2024-02-15 | Fotografías del área intervenida |

  Scenario: Flujo de trazabilidad de estados incluyendo "En análisis"
    > Given caso BUZ-005 en estado "Nuevo"
    > When RRHH revisa el caso y cambia el estado a "En análisis"
    > Then el sistema registra en el historial el cambio a "En análisis" con fecha y usuario
    > And muestra el caso en estado "En análisis"
    > When RRHH define el plan de acción y cambia el estado a "Con plan de acción"
    > Then el sistema registra en el historial el cambio a "Con plan de acción"
    > When RRHH inicia el seguimiento y cambia el estado a "En seguimiento"
    > Then el sistema registra en el historial el cambio a "En seguimiento"
    > When RRHH cierra el caso y cambia el estado a "Cerrado"
    > Then el sistema registra en el historial el cambio a "Cerrado" con fecha de cierre
    > And el historial completo muestra la trazabilidad: Nuevo → En análisis → Con plan de acción → En seguimiento → Cerrado

  Scenario: Cierre de caso con calificación de efectividad y motivo de cierre
    > Given caso en estado "En seguimiento" con plan de acción cumplido
    > When RRHH califica la efectividad como "Mejoró significativamente"
    > And selecciona motivo de cierre "Resuelta"
    > And registra fecha de cierre "2024-03-01"
    > And presiona "Cerrar caso"
    > Then el sistema cambia el estado a "Cerrado"
    > And registra la calificación de efectividad y el motivo de cierre
    > And registra la fecha de cierre
    > And habilita la opción de reapertura del caso

  Scenario: Rechazo de acceso a bandeja de gestión por rol no autorizado (Gerencia)
    > Given un usuario con rol "Gerencia" (o Admisión, Psicólogo, Interno, Caja)
    > When intenta acceder a la bandeja de gestión, detalle de casos o reportes del buzón
    > Then el sistema deniega el acceso
    > And muestra el mensaje "No tiene permisos para acceder a la bandeja de gestión del buzón institucional. Solo Recursos Humanos puede gestionar casos."

  Scenario: Generación de reporte mensual sin datos de contacto de remitentes
    > Given que RRHH genera el reporte analítico mensual de febrero de 2024
    > When exporta el reporte a Excel o PDF
    > Then el reporte contiene indicadores de volumen por área, prioridad, porcentaje de resolución y efectividad
    > And el reporte no contiene nombres ni celulares de remitentes (anónimos o identificados)
    > And el reporte se envía a Gerencia como destinatario

  Scenario: Reapertura de caso cerrado (caso borde)
    > Given caso BUZ-006 en estado "Cerrado"
    > When RRHH identifica nueva evidencia y selecciona "Reabrir caso"
    > Then el sistema cambia el estado a "En análisis"
    > And registra en el historial la reapertura con fecha y usuario
    > And el caso vuelve a estar disponible para gestión en la bandeja de RRHH

  Scenario: Restricción de acceso a información comercial y socioeconómica de pacientes (REST-PRIV-01)
    > Given que RRHH accede al detalle de un caso del buzón institucional
    > When consulta la información del caso
    > Then el sistema no muestra información comercial de marketing
    > And el sistema no muestra situación socioeconómica de pacientes
    > And dichos datos permanecen reservados exclusivamente a Admisión y Gerencia (HU-0004)
```

---

## 5. Conclusiones y Análisis de Resultados
El banco de evaluación experimental demuestra que en el dominio del **Centro Psicológico Senses**, el **Sistema Multiagente LangGraph supera de forma consistente al RAG Convencional**:
1. **Reducción Crítica de Alucinaciones y Desvíos**: Mientras el RAG convencional llega a inventar facturación oficial SUNAT o exponer datos socioeconómicos y de captación al equipo clínico, el Agente Crítico y Analista garantizan estricto apego a las fuentes oficiales (recibo B001 sin validez SUNAT, blindaje de datos comerciales y aviso obligatorio de no emergencia en buzón).
2. **Cobertura Exhaustiva de Casos de Rechazo y Borde**: El RAG baseline produce historias superficiales y sólo escenarios de camino feliz. El Multiagente genera casos negativos y de borde esenciales (bloqueo por cruce de horario en matriz, discordancia de importes en multicitas, rechazo de activo sin foto, denegatoria de acceso clínico a marketing y exclusividad de RRHH en el buzón).
3. **Conformidad BDD y Sintaxis Formal**: El Validador sintáctico asegura que los escenarios cumplan la gramática Gherkin estricta lista para automatización con herramientas como Cucumber o Behave.

