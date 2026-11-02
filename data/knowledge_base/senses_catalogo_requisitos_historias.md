# Centro Psicológico Senses: Catálogo Oficial de Requisitos e Historias de Usuario

## Catálogo de Historias de Usuario (HU-0001 a HU-0005)

---

### HISTORIA 01: HU-0001

| Campo | Detalle |
| :--- | :--- |
| **Título** | Calendario interactivo para agendamiento individual, en bloque y reprogramación de citas |
| **Versión** | 02.00 |
| **Estimado** | 8 Puntos de Historia |
| **Fuente** | FUE-0001 (Matriz de Citas / Horario de Atención en Hojas Compartidas) |
| **Descripción** | Como personal de Admisión,<br>quiero consultar la disponibilidad horaria de los profesionales en una matriz interactiva y agendar citas individuales o en bloque recurrente, así como moverlas o duplicarlas,<br>para coordinar ágilmente las sesiones de los pacientes (particulares, sociales o por convenio) evitando cruces de horario y sustituyendo el uso de hojas compartidas externas. |
| **Criterios de Aceptación** | **1. Agendamiento individual en matriz:**<br>• Dado que el usuario consulta el calendario semanal o mensual de un profesional.<br>• Cuando hace clic en un horario libre y completa los datos del paciente, tipo de atención (particular, social o convenio) y motivo de consulta.<br>• Entonces el sistema guarda la cita y actualiza el bloque horario como ocupado en la matriz visual.<br><br>**2. Programación de citas recurrentes en bloque:**<br>• Dado que el usuario necesita programar una serie continua de sesiones para un paciente.<br>• Cuando activa la opción de agendamiento en bloque, define el rango de fechas, los días de la semana y los horarios deseados.<br>• Entonces el sistema verifica la jornada laboral del profesional, omite los horarios previamente ocupados y genera automáticamente las citas válidas dentro del periodo indicado.<br><br>**3. Reprogramación por arrastre:**<br>• Dado que existe una cita programada en el calendario.<br>• Cuando el usuario arrastra la cita hacia un nuevo horario disponible.<br>• Entonces el sistema actualiza la fecha, hora y consultorio de la cita sin necesidad de cancelarla ni volver a ingresar la información del paciente.<br><br>**4. Duplicación de citas (copiar y pegar):**<br>• Dado que el usuario desea replicar una cita existente en otro día u hora.<br>• Cuando copia la cita deseada y selecciona un horario libre para pegarla.<br>• Entonces el sistema crea una nueva cita conservando los datos del paciente y el motivo de consulta en el horario seleccionado.<br><br>**5. Control de disponibilidad y prevención de cruces:**<br>• Dado que un horario se encuentra ocupado o fuera de la jornada de atención del profesional.<br>• Cuando se intenta registrar, pegar o mover una cita hacia dicho bloque.<br>• Entonces el sistema impide la acción y muestra un aviso informando que el horario no está disponible. |

#### Especificación Gherkin / BDD (HU-0001):
```gherkin
Feature: Calendario interactivo y gestión dinámica de citas
  Como personal de Admisión
  Quiero agendar, mover y duplicar citas en una matriz interactiva
  Para coordinar eficazmente las consultas evitando cruces y sustituyendo hojas compartidas

  Scenario: Agendamiento individual en matriz interactiva
    Given que el personal de admisión consulta el calendario del profesional
    When hace clic en un horario libre e ingresa los datos del paciente, tipo de atención (particular, social o convenio) y motivo
    Then el sistema registra la cita y actualiza el bloque horario como ocupado en la matriz visual

  Scenario: Programación de citas recurrentes en bloque
    Given que se requiere programar una serie continua de sesiones
    When el usuario activa el agendamiento en bloque con rango de fechas, días semanales y horarios
    Then el sistema verifica la jornada laboral del profesional, omite los bloques ocupados y genera automáticamente las citas válidas

  Scenario: Reprogramación ágil por arrastre (Drag and Drop)
    Given que existe una cita previamente agendada en la matriz
    When el usuario arrastra la cita hacia un bloque libre disponible
    Then el sistema actualiza la fecha, hora y consultorio sin requerir cancelación ni reingreso de datos

  Scenario: Duplicación de citas por copiar y pegar
    Given que el usuario necesita duplicar una cita existente
    When copia la cita seleccionada y la pega sobre un bloque libre
    Then el sistema genera una nueva cita conservando los datos del paciente y motivo en el nuevo horario

  Scenario: Prevención estricta de cruces y horarios fuera de jornada
    Given que un bloque horario se encuentra ocupado o fuera de la jornada del profesional
    When el usuario intenta registrar, mover o pegar una cita en dicho horario
    Then el sistema bloquea la operación y notifica que el horario no está disponible
```

---

### HISTORIA 02: HU-0002

| Campo | Detalle |
| :--- | :--- |
| **Título** | Registro de ingresos y emisión de comprobante de pago interno |
| **Versión** | 02.00 |
| **Estimado** | 8 Puntos de Historia |
| **Fuente** | FUE-0002 (Recibo de Pago de Control Interno Senses Psicólogos S.A.C.) |
| **Descripción** | Como personal de Caja o Admisión,<br>quiero registrar los pagos de los pacientes por una o varias citas y emitir el comprobante de pago en formato digital,<br>para mantener el control del flujo diario de ingresos y entregar un comprobante con el desglose del servicio. |
| **Criterios de Aceptación** | **1. Registro de pago y distribución por citas:**<br>• Dado que el usuario inicia el registro de un cobro para un paciente.<br>• Cuando ingresa los datos del cliente (nombre, documento y teléfono), selecciona la forma de pago (efectivo, Yape, Plin, transferencia o tarjeta) y distribuye el monto total entre una o más citas pendientes del paciente.<br>• Entonces el sistema valida que la suma asignada coincida exactamente con el total pagado y actualiza el estado de pago de cada cita vinculada.<br><br>**2. Cálculo automático y numeración correlativa:**<br>• Dado que se completan los datos del ingreso.<br>• Cuando el usuario confirma el registro.<br>• Entonces el sistema calcula automáticamente el subtotal y el IGV (18%), asigna una serie y número correlativo consecutivo para evitar duplicidades, y vincula el cobro a un periodo contable abierto.<br><br>**3. Emisión de comprobante interno en PDF:**<br>• Dado que el cobro ha sido guardado con éxito.<br>• Cuando el usuario solicita emitir el comprobante.<br>• Entonces el sistema genera un documento PDF con los datos institucionales de la clínica, su RUC, número correlativo, datos del cliente y paciente, profesional asignado, detalle de servicios, importes desglosados y el aviso explícito de que se trata de un comprobante de control interno sin validez ante la SUNAT.<br><br>**4. Integración inmediata en el registro financiero:**<br>• Dado que se emitió el comprobante de ingreso.<br>• Cuando el personal autorizado consulta el registro financiero o balance.<br>• Entonces el pago figura inmediatamente en el listado de ingresos, permitiendo filtrar por fechas, paciente, profesional, método de pago y estado. |

#### Especificación Gherkin / BDD (HU-0002):
```gherkin
Feature: Registro de ingresos y comprobante de control interno
  Como personal de Caja o Admisión
  Quiero registrar cobros por citas y generar comprobantes internos digitales
  Para asegurar el control del flujo de ingresos con desglose de importes e IGV

  Scenario: Registro de cobro y distribución multicitas
    Given que un paciente mantiene una o varias citas pendientes de pago
    When el usuario ingresa los datos del cliente, selecciona el método de pago (Yape, Plin, efectivo, transferencia o tarjeta) y asigna el monto entre las citas
    Then el sistema valida que la distribución sume exactamente el importe total y actualiza el estado de las citas a pagado

  Scenario: Cálculo contable automático y serie correlativa
    Given que el registro de cobro contiene los importes distribuidos
    When se confirma el guardado de la transacción
    Then el sistema calcula de forma automática el subtotal y el 18% de IGV, asignando serie correlativa única (ej. B001-000036) vinculada al periodo contable

  Scenario: Emisión de comprobante PDF de control interno sin validez SUNAT
    Given que el cobro fue persistido exitosamente en el sistema
    When el usuario solicita la emisión del comprobante digital
    Then se genera un documento PDF con RUC 20609694671, datos de cliente y paciente, profesional, desglose de servicios y la advertencia explícita de comprobante interno provisional sin validez SUNAT

  Scenario: Reflejo en tiempo real en el registro financiero
    Given que se emitió el comprobante de pago
    When el usuario autorizado accede al libro o balance diario de ingresos
    Then el registro figura inmediatamente con opciones de filtrado por fecha, paciente, terapeuta, método de pago y estado
```

---

### HISTORIA 03: HU-0003

| Campo | Detalle |
| :--- | :--- |
| **Título** | Control y administración del inventario de activos de la clínica |
| **Versión** | 02.00 |
| **Estimado** | 8 Puntos de Historia |
| **Fuente** | FUE-0003 (Comisión de Inventario Bienes Muebles Senses Psicólogos S.A.C.) |
| **Descripción** | Como personal de Caja y Registro o Administración,<br>quiero registrar, actualizar y dar seguimiento a los bienes y equipos de la clínica con su información detallada, estado y fotografía,<br>para mantener un inventario físico valorizado, auditable y actualizado de los recursos institucionales. |
| **Criterios de Aceptación** | **1. Registro detallado del bien:**<br>• Dado que el usuario accede al formulario de inventario.<br>• Cuando ingresa denominación, categoría, cantidad, precio unitario, datos descriptivos (marca, modelo, serie, color, dimensiones, comprobante o factura de compra) y adjunta una fotografía del bien.<br>• Entonces el sistema calcula automáticamente el importe total en tiempo real y guarda el activo en el inventario institucional.<br><br>**2. Historial de modificaciones y trazabilidad:**<br>• Dado que el usuario modifica cualquier dato o la situación operativa de un activo (Operativo, En Mantenimiento o Dado de Baja).<br>• Cuando guarda los cambios.<br>• Entonces el sistema actualiza la ficha del activo y registra automáticamente una entrada en el historial con la fecha, el usuario responsable, el dato modificado y sus valores anterior y nuevo.<br><br>**3. Retiro y reactivación de bienes:**<br>• Dado que un bien se deteriora, queda en desuso o es dado de baja.<br>• Cuando el usuario ejecuta la acción de dar de baja.<br>• Entonces el sistema retira el activo de la lista operativa y lo traslada a la vista de activos inactivos conservando toda su información e historial, permitiendo reactivarlo si vuelve a estar en servicio.<br><br>**4. Filtros y exportación de inventario:**<br>• Dado que el usuario consulta el inventario de bienes (activos o inactivos).<br>• Cuando aplica filtros por categoría, situación operativa o texto de búsqueda y solicita la exportación.<br>• Entonces el sistema genera un archivo en formato Excel o PDF que contiene exactamente los registros y columnas que cumplen con los filtros aplicados. |

#### Especificación Gherkin / BDD (HU-0003):
```gherkin
Feature: Control y administración de activos institucionales
  Como personal de Caja y Registro o Administración
  Quiero registrar y auditar bienes muebles y equipos con fotos y estados
  Para disponer de un inventario valorizado, trazable y actualizado

  Scenario: Alta completa de activo con fotografía y cálculo en tiempo real
    Given que el usuario accede al módulo de registro de inventario
    When ingresa denominación, categoría, cantidad, costo unitario, especificaciones (marca, modelo, color, dimensiones) y adjunta la fotografía
    Then el sistema computa el importe total en tiempo real y persiste el activo en la base patrimonial

  Scenario: Trazabilidad y bitácora histórica de modificaciones
    Given que un activo ya se encuentra registrado en el sistema
    When el usuario modifica sus datos o su estado operativo (Operativo, En Mantenimiento o Dado de Baja)
    Then el sistema registra una entrada de auditoría inmutable con fecha, responsable, campo afectado y valor previo y posterior

  Scenario: Baja y reactivación de bienes institucionales
    Given que un bien queda obsoleto o fuera de servicio
    When el administrador ejecuta la acción de baja
    Then el bien se traslada a la vista de activos inactivos manteniendo su ficha completa y permitiendo su reactivación si retorna a servicio

  Scenario: Filtrado avanzado y exportación a Excel y PDF
    Given que se consulta la lista consolidada de bienes muebles
    When se aplican filtros por categoría, condición operativa o búsqueda textual y se solicita exportación
    Then el sistema genera un archivo Excel o PDF estructurado reflejando exactamente los registros filtrados
```

---

### HISTORIA 04: HU-0004

| Campo | Detalle |
| :--- | :--- |
| **Título** | Consulta gerencial y exportación de datos comerciales y socioeconómicos de pacientes |
| **Versión** | 02.00 |
| **Estimado** | 5 Puntos de Historia |
| **Fuente** | FUE-0004 (Ficha de Registro y Encuesta Estratégica de Pacientes para Estudio de Mercado) |
| **Descripción** | Como Gerencia,<br>quiero consultar los datos de prospección comercial, canales de captación y situación socioeconómica de los pacientes, así como exportar el consolidado institucional,<br>para evaluar el rendimiento de las estrategias de captación y tomar decisiones comerciales sin exponer esta información al personal de atención clínica. |
| **Criterios de Aceptación** | **1. Acceso a datos de prospección y marketing:**<br>• Dado que un usuario con rol de Gerencia o Admisión consulta la ficha de un paciente.<br>• Cuando accede al apartado de información comercial y marketing.<br>• Entonces el sistema le permite visualizar y gestionar las respuestas sobre cómo conoció la clínica (redes sociales, buscador, recomendación), persona que lo refirió, comparación previa con otros centros, motivos de atracción y aceptación de promociones.<br><br>**2. Acceso a información socioeconómica:**<br>• Dado que un usuario autorizado consulta la información complementaria del paciente.<br>• Cuando abre la sección socioeconómica.<br>• Entonces el sistema muestra la situación laboral, sector o rubro de trabajo, modalidad laboral (presencial, remota o mixta) y el rango de ingresos económicos familiares.<br><br>**3. Privacidad y restricción para el personal clínico:**<br>• Dado que un profesional con rol de Psicólogo o Interno accede a la ficha del paciente.<br>• Cuando revisa la información registrada.<br>• Entonces el sistema mantiene completamente ocultas las secciones de marketing comercial y situación socioeconómica, reservando su acceso exclusivamente a Admisión y Gerencia.<br><br>**4. Exportación consolidada para toma de decisiones:**<br>• Dado que Gerencia necesita analizar la cartera global de pacientes.<br>• Cuando solicita la descarga del reporte general de pacientes.<br>• Entonces el sistema genera y descarga un archivo en formato Excel con el consolidado completo de pacientes, integrando sus datos sociodemográficos con las respuestas de captación comercial y socioeconómica para su evaluación estratégica. |

#### Especificación Gherkin / BDD (HU-0004):
```gherkin
Feature: Explotación gerencial de datos comerciales y socioeconómicos
  Como Gerencia
  Quiero analizar métricas de prospección y nivel socioeconómico de pacientes
  Para formular estrategias de crecimiento comercial resguardando la privacidad clínica

  Scenario: Visualización de prospección comercial y canales de captación
    Given que un usuario con rol Gerencia o Admisión abre el expediente de un paciente
    When consulta el bloque de información comercial y marketing
    Then visualiza canal de captación, recomendador, comparativa con otros centros, motivos de elección y consentimiento de promociones

  Scenario: Acceso a indicadores socioeconómicos del paciente
    Given que el personal autorizado consulta la sección socioeconómica
    When visualiza los datos complementarios
    Then el sistema expone la situación laboral, rubro de actividad, modalidad de trabajo y rango de ingresos familiares

  Scenario: Segregación estricta de privacidad frente al equipo clínico
    Given que un profesional con rol de Psicólogo o Interno accede a la ficha de un paciente
    When navega por la interfaz de atención clínica
    Then las secciones de prospección comercial, marketing e ingresos socioeconómicos permanecen totalmente ocultas e inaccesibles

  Scenario: Exportación consolidada de datos comerciales a formato Excel
    Given que Gerencia requiere evaluar el retorno de campañas de captación
    When ejecuta la exportación del consolidado general de pacientes
    Then el sistema genera un archivo Excel con cruce de datos sociodemográficos, canales de captación y niveles de ingresos
```

---

### HISTORIA 05: HU-0005

| Campo | Detalle |
| :--- | :--- |
| **Título** | Buzón interno de sugerencias, reconocimientos y gestión de planes de mejora |
| **Versión** | 02.00 |
| **Estimado** | 5 Puntos de Historia |
| **Fuente** | FUE-0005 (Ficha de Sugerencias y Observaciones - Mejora Continua Senses) |
| **Descripción** | Como colaborador de la clínica (Psicólogo, Interno, Admisión o Caja),<br>quiero enviar sugerencias, observaciones o reconocimientos de forma anónima o identificada, y como Recursos Humanos quiero clasificar los casos, gestionar acciones de mejora y emitir reportes mensuales,<br>para impulsar la mejora continua del clima y los servicios institucionales con estricta confidencialidad. |
| **Criterios de Aceptación** | **1. Envío institucional de mensajes:**<br>• Dado que un colaborador ingresa al apartado del buzón en la plataforma.<br>• Cuando selecciona su rol, el tipo de registro (sugerencia, observación, reconocimiento o aspecto por mejorar), el área vinculada, la importancia percibida, el mensaje y una propuesta opcional de mejora.<br>• Entonces el sistema registra el caso con estado «Nuevo», le asigna un código correlativo único y muestra la confirmación de envío al colaborador.<br><br>**2. Gestión de anonimato o contacto voluntario:**<br>• Dado que el colaborador completa el formulario.<br>• Cuando elige mantener el anonimato, el sistema no vincula su cuenta de usuario ni almacena datos de contacto; y si autoriza ser contactado, le permite ingresar voluntariamente su nombre y celular.<br>• Entonces los datos de contacto únicamente quedan a la vista del área de Recursos Humanos.<br><br>**3. Aviso permanente de no emergencia:**<br>• Dado que un colaborador abre el formulario de registro del buzón.<br>• Cuando visualiza la pantalla antes de redactar su mensaje.<br>• Entonces el sistema muestra de forma permanente y visible una advertencia indicando que este buzón no sustituye canales de emergencia, crisis o situaciones de riesgo inmediato.<br><br>**4. Transcripción de fichas físicas por Recursos Humanos:**<br>• Dado que Recursos Humanos retira fichas físicas del buzón instalado en la clínica.<br>• Cuando las transcribe en el sistema mediante la opción de registro físico.<br>• Entonces el sistema almacena el caso bajo el canal de ficha física, asignándole su correlativo y los mismos campos de clasificación para su seguimiento unificado.<br><br>**5. Priorización y planes de acción por Recursos Humanos:**<br>• Dado que Recursos Humanos revisa un caso en su bandeja de gestión.<br>• Cuando asigna una prioridad (Baja, Media, Alta o Crítica), designa a un responsable y programa acciones de mejora con fecha límite y evidencia esperada.<br>• Entonces el sistema actualiza el estado del caso (En análisis, Con plan de acción o En seguimiento) y registra cada cambio en el historial de trazabilidad.<br><br>**6. Medición de efectividad y cierre formal:**<br>• Dado que se completaron las acciones planificadas para un caso.<br>• Cuando Recursos Humanos califica el resultado obtenido (no mejoró, mejoró parcialmente o mejoró significativamente) y selecciona el motivo de cierre (resuelta, parcialmente resuelta, no resuelta o justificación administrativa).<br>• Entonces el sistema cambia el estado a «Cerrado», guarda la fecha de cierre y permite reabrir el caso si la situación requiere nueva intervención.<br><br>**7. Reporte analítico mensual y exportación:**<br>• Dado que Recursos Humanos requiere reportar el balance institucional a Gerencia.<br>• Cuando selecciona un mes o periodo en la sección de reportes.<br>• Entonces el sistema genera indicadores de volumen por área, prioridad, porcentaje de resolución y efectividad de las mejoras, permitiendo exportar el reporte a formato Excel o PDF sin mostrar los nombres ni celulares de los remitentes.<br><br>**8. Privacidad estricta y restricción de bandeja:**<br>• Dado que un usuario con rol distinto a Recursos Humanos (Gerencia, Admisión, Psicólogo, Interno o Caja) navega por el sistema.<br>• Cuando accede a las opciones del buzón.<br>• Entonces el sistema le permite únicamente redactar y enviar nuevos mensajes, impidiéndole consultar la bandeja de gestión, el detalle de casos o los reportes. |

#### Especificación Gherkin / BDD (HU-0005):
```gherkin
Feature: Buzón interno de sugerencias y planes de mejora continua
  Como colaborador de Senses
  Quiero enviar sugerencias y reconocimientos anónimos o identificados
  Para promover la mejora continua con administración confidencial de Recursos Humanos

  Scenario: Envío institucional de reporte con asignación correlativa
    Given que un colaborador accede al formulario de buzón interno
    When selecciona rol, tipo de registro, área vinculada, nivel de importancia, mensaje y propuesta
    Then el sistema genera código correlativo único (ej. SUG-2026-001) con estado Nuevo y confirmación de recepción

  Scenario: Despliegue permanente de advertencia legal de no emergencia
    Given que el usuario abre la pantalla del buzón
    When visualiza el formulario antes de la redacción
    Then el sistema expone permanentemente el aviso de que el buzón no sustituye canales de emergencia, crisis o riesgo inmediato

  Scenario: Gestión de anonimato vs contacto voluntario confidencial
    Given que el colaborador finaliza el registro
    When marca mantener el anonimato
    Then el sistema bloquea el almacenamiento de IP, cuenta o teléfono; y si proporciona contacto voluntario, solo es accesible por RRHH

  Scenario: Transcripción de fichas físicas por Recursos Humanos
    Given que el área de Recursos Humanos retira fichas físicas del buzón de la sede
    When utiliza la interfaz de transcripción manual
    Then el caso queda registrado bajo canal de ficha física compartiendo la misma estructura y correlativo anual

  Scenario: Planificación, seguimiento y medición de efectividad
    Given que RRHH prioriza un caso (Baja, Media, Alta o Crítica) y asigna un plan de acción
    When culminan las acciones y se califica la efectividad (no mejoró, mejoró parcialmente o mejoró significativamente)
    Then el caso transiciona a Cerrado con motivo documentado y opción de reapertura si surgen reincidencias

  Scenario: Restricción estricta de la bandeja de gestión ante otros roles
    Given que un usuario con rol Gerencia, Admisión o Terapeuta ingresa al módulo de buzón
    When intenta acceder a la bandeja de casos o reportes de seguimiento
    Then el sistema deniega el acceso y restringe la administración exclusivamente al rol Recursos Humanos
```
