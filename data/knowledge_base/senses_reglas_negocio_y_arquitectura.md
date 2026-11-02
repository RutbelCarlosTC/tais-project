# Centro Psicológico Senses: Reglas de Negocio, Políticas y Arquitectura Técnica

## 1. Reglas de Negocio de Agenda y Citas (RN-SENSES-CLI)

### RN-CLI-001: Calendario Interactivo, Prevención de Cruces y Agendamiento en Bloque (HU-0001 / FUE-0001)
- **Matriz Interactiva Visual**: La disponibilidad horaria de los profesionales debe renderizarse en una matriz semanal y mensual interactiva, reemplazando las hojas externas de Google Sheets.
- **Validación de Jornada Laboral**: Toda asignación de cita (individual, recurrente, arrastre o pegado) debe verificar previamente la jornada laboral activa del profesional (`WorkSchedule`) y la disponibilidad del consultorio físico seleccionado.
- **Prevención Estricta de Cruces**: Está terminantemente prohibido registrar, mover o duplicar una cita sobre un bloque previamente ocupado o bloqueado. El sistema debe impedir la acción en tiempo real y emitir un mensaje de indisponibilidad.
- **Programación en Bloque Recurrente**: Al programar series continuas de sesiones (por rango de fechas y días específicos), el sistema debe validar la jornada, omitir automáticamente bloques ocupados o no laborables y generar las citas válidas dentro del periodo.
- **Reprogramación por Arrastre (Drag and Drop)**: Arrastrar una cita hacia un bloque libre actualiza instantáneamente la fecha, hora y consultorio conservando el paciente y motivo, sin necesidad de cancelar ni recrear el registro.
- **Duplicación por Copiar y Pegar**: Permite copiar una cita existente y pegarla en un horario libre generando una nueva cita con los mismos datos del paciente y motivo de consulta.
- **Tipos de Atención**: Soporte explícito para modalidades Particular, Social y Por Convenio.

---

## 2. Reglas de Negocio Financieras y Facturación Interna (RN-SENSES-FIN)

### RN-FIN-001: Registro de Cobros y Comprobante de Control Interno (HU-0002 / FUE-0002)
- **Distribución Multicitas**: El usuario de Caja o Admisión puede registrar un pago y distribuir el monto total entre una o varias citas pendientes del mismo paciente. La suma de las partes distribuidas debe coincidir exactamente con el monto total cobrado; si no coincide, el sistema bloquea el guardado.
- **Métodos de Pago**: Admite efectivo, Yape, Plin, transferencias bancarias y tarjetas de débito/crédito.
- **Cálculo Automático de Impuestos**: El sistema computa de forma automática e inmediata el Subtotal y el Impuesto General a las Ventas (IGV 18%) a partir del monto total pactado:
  $$\text{Subtotal} = \frac{\text{Total}}{1.18}, \quad \text{IGV} = \text{Total} - \text{Subtotal}$$
- **Serie y Numeración Correlativa**: Asigna una serie consecutiva (ej. `B001`) y un número correlativo secuencial irrepetible (ej. `000036`) asegurando que el cobro quede indexado a un periodo contable abierto.
- **Generación de Comprobante PDF Interno**: Todo cobro guardado permite emitir un PDF con membrete de Senses Psicólogos S.A.C., RUC `20609694671`, datos del pagador (cliente), paciente, terapeuta, desglose de importes y la leyenda legal obligatoria:
  > *"ESTE RECIBO NO ES UNA BOLETA DE VENTA, ES PROVISIONAL. SU BOLETA DE VENTA O FACTURA SE HARÁ LLEGAR AL CORREO ELECTRÓNICO / CELULAR EN FORMATO PDF."* (Comprobante de control interno sin validez ante SUNAT).
- **Integración Inmediata en Registro Diario**: El cobro impacta en tiempo real el libro de ingresos, permitiendo filtros inmediatos por fecha, paciente, profesional, método de pago y estado.

---

## 3. Reglas de Negocio de Activos e Inventario Físico (RN-SENSES-PAT)

### RN-PAT-001: Control y Administración del Inventario de Activos (HU-0003 / FUE-0003)
- **Registro Pormenorizado y Valorización en Tiempo Real**: Todo bien mueble o equipo incorporado al inventario debe registrar: denominación, categoría, cantidad, costo unitario, importe total calculado automáticamente en tiempo real ($\text{Total} = \text{Cantidad} \times \text{Precio Unitario}$), marca, modelo, tipo, color, serie, dimensiones, comprobante de compra y fotografía física obligatoria.
- **Historial de Auditoría y Trazabilidad**: Cualquier modificación sobre las características o sobre la situación operativa de un activo genera un registro inmutable en la bitácora con: fecha/hora, usuario responsable, campo modificado, valor anterior y valor nuevo.
- **Estados Operativos y Segregación de Inactivos**: Los activos transicionan entre `Operativo`, `En Mantenimiento` y `Dado de Baja`. Al dar de baja un bien, este se retira de la lista operativa y pasa a la vista de activos inactivos conservando su ficha e historial íntegros, permitiendo su reactivación si el bien retorna a servicio.
- **Filtros y Exportación**: El inventario puede consultarse y filtrarse por categoría, estado operativo o término de búsqueda, permitiendo exportar el catálogo completo o filtrado a formatos Excel y PDF.

---

## 4. Reglas de Negocio de Datos Comerciales y Privacidad (RN-SENSES-MKT)

### RN-MKT-001: Prospección Comercial, Indicadores Socioeconómicos y Segregación Clínica (HU-0004 / FUE-0004)
- **Prospección y Captación Comercial**: En la ficha del paciente se capturan datos estratégicos: canal de captación (redes sociales, buscador, recomendación), nombre de quien refirió, comparación previa con otros centros psicológicos, motivos de elección de la clínica y consentimiento para promociones.
- **Información Socioeconómica Opcional**: Registro de situación laboral, sector o rubro de trabajo, modalidad de trabajo (presencial, remota o mixta) y rango de ingresos económicos familiares.
- **Aislamiento Estricto de Privacidad Clínica**: Los profesionales con rol de Psicólogo o Interno tienen **terminantemente restringido** el acceso a la sección de datos comerciales y socioeconómicos. Esta información está completamente oculta en las vistas clínicas y reservada exclusivamente para Admisión y Gerencia General.
- **Consolidado Exportable para Inteligencia de Negocio**: La Gerencia General tiene acceso a la descarga de reportes generales en Excel que cruzan los datos sociodemográficos del paciente con su canal de atracción y nivel socioeconómico para la toma de decisiones comerciales.

---

## 5. Reglas de Negocio de Recursos Humanos y Clima Laboral (RN-SENSES-RRHH)

### RN-RRHH-001: Buzón de Sugerencias, Anonimato y Planes de Mejora (HU-0005 / FUE-0005 / MAN-RRHH-BUZ-001)
- **Envío Institucional Multirrol**: Colaboradores (Psicólogos, Internos, Admisión, Caja) pueden registrar sugerencias, observaciones, reconocimientos o aspectos por mejorar asociados a áreas institucionales (Atención psicológica, Admisión, RR.HH., Infraestructura, Organización).
- **Régimen de Anonimato Estricto vs Contacto Voluntario**: Si el colaborador opta por el anonimato, el sistema no vincula su cuenta de usuario ni almacena IP ni datos de contacto. Si autoriza ser contactado, su nombre y teléfono quedan estrictamente bajo reserva y únicamente visibles para Recursos Humanos.
- **Aviso Legal Permanente de No Emergencia**: La pantalla del buzón debe mostrar permanentemente y en lugar visible:
  > *"IMPORTANTE: Si existe riesgo, violencia, emergencia, vulneración de confidencialidad o una situación que requiera atención inmediata, comunícala directamente al personal de SENSES."*
- **Transcripción de Fichas Físicas**: Recursos Humanos transcribe periódicamente las fichas físicas retiradas del buzón físico de la clínica mediante un formulario específico que clasifica el canal como `Ficha Física` asignando el correlativo anual unificado (`SUG-2026-XXXX`).
- **Ciclo de Gestión y Medición de Efectividad**:
  - Priorización obligatoria: `Baja`, `Media`, `Alta`, `Crítica`.
  - Estados: `Nuevo` $\rightarrow$ `En Análisis` $\rightarrow$ `Con Plan de Acción` $\rightarrow$ `En Seguimiento` $\rightarrow$ `Cerrado`.
  - Asignación de plan de acción con responsable, fecha límite y evidencia esperada.
  - Al cerrar el caso, RRHH califica obligatoriamente la efectividad de la mejora: `No Mejoró`, `Mejoró Parcialmente` o `Mejoró Significativamente`.
  - Se admite la reapertura si la problemática reincide.
- **Reportes Analíticos Mensuales**: RRHH genera consolidados mensuales de volumen por área, prioridad y efectividad de planes exportables a Excel/PDF sin exponer identidades de remitentes anónimos.
- **Exclusividad de Acceso a la Bandeja**: Ni Gerencia, ni Admisión, ni el equipo clínico tienen acceso a la bandeja de gestión de casos ni a sus expedientes; la bandeja es de administración confidencial y exclusiva de Recursos Humanos.

---

## 6. Arquitectura Técnica y Modelado de Datos (Prisma ORM)

### Modelos Principales de Base de Datos
1. **Modelo `Appointment` (HU-0001)**:
   - `id`: UUID (PK)
   - `patientId`: UUID (FK)
   - `therapistId`: UUID (FK)
   - `roomId`: String (ej. "C-2")
   - `startTime`: DateTime
   - `endTime`: DateTime
   - `careType`: Enum (`PARTICULAR`, `SOCIAL`, `CONVENIO`)
   - `reason`: String
   - `status`: Enum (`SCHEDULED`, `CONFIRMED`, `COMPLETED`, `CANCELLED`)
   - `isRecurring`: Boolean, `seriesId`: UUID?

2. **Modelo `PaymentReceipt` y `PaymentAllocation` (HU-0002)**:
   - `id`: UUID (PK)
   - `series`: String (`B001`)
   - `number`: Int (Autonumérico consecutivo)
   - `clientId`: UUID (Pagador)
   - `paymentMethod`: Enum (`YAPE`, `PLIN`, `CASH`, `TRANSFER`, `CARD`)
   - `subtotal`: Decimal(10, 2)
   - `igv`: Decimal(10, 2) (18%)
   - `total`: Decimal(10, 2)
   - `isInternalReceipt`: Boolean (Default: true)
   - `allocations`: Relación 1 a N con `Appointment` especificando monto distribuido.

3. **Modelo `Asset` y `AssetHistory` (HU-0003)**:
   - `id`: UUID (PK)
   - `denomination`: String
   - `category`: String
   - `quantity`: Int
   - `unitPrice`: Decimal(10, 2)
   - `totalPrice`: Decimal(10, 2) (Calculado en tiempo real)
   - `brand`: String?, `model`: String?, `seriesNumber`: String?, `color`: String?
   - `photoUrl`: String (URL de imagen obligatoria)
   - `operationalStatus`: Enum (`OPERATIONAL`, `MAINTENANCE`, `DECOMMISSIONED`)
   - `history`: Bitácora inmutable con `changedByUserId`, `changeDate`, `previousValue`, `newValue`.

4. **Modelo `PatientMarketingData` y `PatientSocioeconomicData` (HU-0004)**:
   - `id`: UUID (PK), `patientId`: UUID (FK Unique)
   - `acquisitionChannel`: Enum (`SOCIAL_MEDIA`, `SEARCH_ENGINE`, `RECOMMENDATION`, `OTHER`)
   - `referredByName`: String?
   - `previousCenterComparison`: Boolean
   - `promotionsConsent`: Boolean
   - `employmentStatus`: String?, `industrySector`: String?, `workModality`: String?
   - `monthlyIncomeRange`: String?
   - *Políticas de API*: Endpoints con Middleware `requireRole(["ADMIN", "ADMISSION"])` que bloquean peticiones desde tokens de rol `PSYCHOLOGIST` o `INTERN`.

5. **Modelo `SuggestionCase` y `ImprovementActionPlan` (HU-0005)**:
   - `id`: UUID (PK)
   - `code`: String (Unique, ej. `SUG-2026-001`)
   - `originChannel`: Enum (`WEB_INTERNAL`, `PHYSICAL_SHEET`)
   - `reporterRole`: String
   - `isAnonymous`: Boolean
   - `contactName`: String?, `contactPhone`: String? (Opcionales, cifrados)
   - `caseType`: Enum (`SUGGESTION`, `OBSERVATION`, `RECOGNITION`, `IMPROVEMENT_AREA`)
   - `targetArea`: String
   - `priority`: Enum (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`)
   - `status`: Enum (`NEW`, `ANALYZING`, `ACTION_PLAN`, `MONITORING`, `CLOSED`)
   - `effectivenessScore`: Enum (`NOT_IMPROVED`, `PARTIALLY_IMPROVED`, `SIGNIFICANTLY_IMPROVED`)?
   - `actionPlans`: Relación con planes de acción (responsable, fecha límite, evidencia esperada).
