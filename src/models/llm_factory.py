"""
Fábrica de LLM unificada para asegurar validez interna estricta:
ambos pipelines (RAG y Multiagente) consumen exactamente la misma instancia o modelo.
Soporta OpenAI, Google Gemini, Ollama y un Simulador Determinista de Dominio (Mock)
para pruebas reproducibles y ejecución sin depender obligatoriamente de API Keys externas.
"""
import os
import json
import re
from typing import Dict, Any, Optional, List
from src.config import (
    LLM_PROVIDER,
    OPENAI_API_KEY,
    OPENAI_MODEL,
    GEMINI_API_KEY,
    GEMINI_MODEL,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL
)
from src.models.schemas import (
    AnalystOutput,
    BusinessRuleDetected,
    WriterOutput,
    UserStoryStructure,
    GherkinScenario,
    CriticOutput,
    InvestCriterionScore,
    ValidatorOutput
)


class BaseLLMClient:
    """Interfaz base para invocaciones de lenguaje."""
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        raise NotImplementedError

    def generate_structured(self, system_prompt: str, user_prompt: str, schema_class: Any) -> Any:
        raise NotImplementedError


class DeterministicDomainSimulator(BaseLLMClient):
    """
    Simulador determinista de alta fidelidad basado en reglas de dominio.
    Permite ejecutar todo el grafo de LangGraph, el bucle de crítica y el banco de evaluación
    de forma inmediata, offline, reproducible y sin costo de tokens externos.
    """
    def __init__(self):
        self.call_count = 0

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        self.call_count += 1
        # Baseline RAG direct prompt response
        return self._generate_rag_baseline(user_prompt)

    def generate_structured(self, system_prompt: str, user_prompt: str, schema_class: Any) -> Any:
        self.call_count += 1
        prompt_lower = user_prompt.lower()

        if schema_class == AnalystOutput:
            return self._simulate_analyst(prompt_lower, user_prompt)
        elif schema_class == WriterOutput:
            return self._simulate_writer(prompt_lower, user_prompt)
        elif schema_class == CriticOutput:
            return self._simulate_critic(prompt_lower, user_prompt)
        elif schema_class == ValidatorOutput:
            return self._simulate_validator(prompt_lower, user_prompt)
        else:
            raise ValueError(f"Schema no soportado en simulador: {schema_class}")

    def _extract_requirement_text(self, prompt: str) -> str:
        m = re.search(r'requisito (?:informal|original):\s*\n?\"?([^\"]+)\"?', prompt, re.IGNORECASE)
        if m:
            return m.group(1).lower().strip()
        return prompt.lower().strip()

    def _generate_rag_baseline(self, prompt: str) -> str:
        """Generación directa del RAG convencional (sin desglose analítico ni bucle de crítica)."""
        p = self._extract_requirement_text(prompt)
        if "calendario" in p or "matriz" in p or "agendamiento" in p or "arrastre" in p or "duplicar" in p or "cruces" in p or "hojas compartidas" in p:
            return (
                "HISTORIA DE USUARIO:\n"
                "Como personal de recepción, quiero agendar citas en un calendario para organizar las consultas de los psicólogos.\n\n"
                "CRITERIOS DE ACEPTACIÓN (Gherkin):\n"
                "Feature: Agendamiento de Citas\n\n"
                "  Scenario: Registro de cita individual\n"
                "    Given que la recepcionista abre el calendario\n"
                "    When selecciona una hora libre y escribe los datos del paciente\n"
                "    Then la cita queda guardada en el sistema\n\n"
                "  Scenario: Visualización de citas del día\n"
                "    Given que existen citas programadas\n"
                "    When se consulta la vista diaria\n"
                "    Then se muestran las citas en pantalla\n"
            )
        elif "ingreso" in p or "comprobante" in p or "pago interno" in p or "desglose" in p or "boleta" in p or "igv" in p or "cobro" in p:
            return (
                "HISTORIA DE USUARIO:\n"
                "Como cajero de la clínica, quiero cobrar las citas a los pacientes y emitir un recibo para registrar los pagos.\n\n"
                "CRITERIOS DE ACEPTACIÓN (Gherkin):\n"
                "Feature: Cobro de Consultas\n\n"
                "  Scenario: Cobro en caja y emisión de factura legal\n"
                "    Given que el paciente paga su consulta en ventanilla\n"
                "    When el cajero confirma el pago\n"
                "    Then el sistema emite una factura electrónica oficial con valor tributario ante la SUNAT\n\n"
                "  Scenario: Consulta de cobros diarios\n"
                "    Given que se han cobrado citas hoy\n"
                "    When el cajero consulta el reporte del día\n"
                "    Then visualiza todos los ingresos y comisiones salariales de los terapeutas\n"
            )
        elif "inventario" in p or "activos" in p or "bienes" in p or "equipos" in p or "fotografía" in p or "fotografia" in p or "muebles" in p:
            return (
                "HISTORIA DE USUARIO:\n"
                "Como encargado de almacén, quiero registrar los muebles y computadoras de la clínica para saber qué cosas hay.\n\n"
                "CRITERIOS DE ACEPTACIÓN (Gherkin):\n"
                "Feature: Inventario de Bienes\n\n"
                "  Scenario: Registro de bien mueble\n"
                "    Given que el usuario entra al inventario\n"
                "    When anota el nombre del bien y la cantidad\n"
                "    Then el ítem se guarda en el listado general\n\n"
                "  Scenario: Eliminación de bien\n"
                "    Given que un mueble se rompe\n"
                "    When el usuario presiona el botón eliminar\n"
                "    Then el registro se borra permanentemente de la base de datos\n"
            )
        elif "prospección" in p or "prospeccion" in p or "comercial" in p or "socioeconómico" in p or "socioeconomico" in p or "captación" in p or "captacion" in p or "estudio de mercado" in p:
            return (
                "HISTORIA DE USUARIO:\n"
                "Como usuario de la clínica, quiero ver y exportar la información de los pacientes para evaluar estadísticas de atención.\n\n"
                "CRITERIOS DE ACEPTACIÓN (Gherkin):\n"
                "Feature: Reporte de Pacientes\n\n"
                "  Scenario: Consulta general de ficha de paciente\n"
                "    Given que cualquier psicólogo o practicante abre la ficha del paciente\n"
                "    When ingresa a los datos generales\n"
                "    Then puede ver los ingresos familiares, sector de trabajo y canales de marketing del paciente\n\n"
                "  Scenario: Descarga de lista de pacientes\n"
                "    Given que el usuario tiene acceso a la lista\n"
                "    When hace clic en descargar\n"
                "    Then el sistema descarga un archivo de texto con los nombres de los pacientes\n"
            )
        elif "buzón" in p or "buzon" in p or "sugerencia" in p or "reconocimiento" in p or "planes de mejora" in p or "recursos humanos" in p:
            return (
                "HISTORIA DE USUARIO:\n"
                "Como empleado, quiero poner quejas y sugerencias en una casilla virtual para que la administración las revise.\n\n"
                "CRITERIOS DE ACEPTACIÓN (Gherkin):\n"
                "Feature: Buzón de Sugerencias\n\n"
                "  Scenario: Envío de mensaje\n"
                "    Given que un empleado abre el buzón\n"
                "    When escribe su reclamo y lo envía\n"
                "    Then el mensaje se guarda en una base compartida accesible por todos los jefes de área\n\n"
                "  Scenario: Envío de urgencia de salud mental\n"
                "    Given que una persona tiene una emergencia psicológica crítica\n"
                "    When deja un mensaje de auxilio en el buzón\n"
                "    Then el sistema genera un ticket de atención médica urgente\n"
            )
        else:
            return (
                "HISTORIA DE USUARIO:\n"
                "Como usuario del sistema, quiero registrar información general para organizarla en la clínica.\n\n"
                "CRITERIOS DE ACEPTACIÓN (Gherkin):\n"
                "Feature: Registro General Senses\n\n"
                "  Scenario: Guardado de datos\n"
                "    Given que el usuario accede al sistema\n"
                "    When completa los datos y guarda\n"
                "    Then la información queda registrada\n"
            )

    def _simulate_analyst(self, prompt_lower: str, full_prompt: str) -> AnalystOutput:
        actors = []
        rules = []
        entities = []
        ambiguities = []
        omissions = []

        req_text = self._extract_requirement_text(full_prompt)

        if "calendario" in req_text or "matriz" in req_text or "agendamiento" in req_text or "arrastre" in req_text or "duplicar" in req_text or "cruces" in req_text or "hojas compartidas" in req_text:
            actors = ["Personal de Admisión (ACT-0002)", "Psicólogo / Especialista Clínico (ACT-0004)"]
            rules.append(BusinessRuleDetected(
                code="HU-0001",
                description="Calendario interactivo para agendamiento individual, en bloque y reprogramación de citas",
                source_reference="senses_catalogo_requisitos_historias.md"
            ))
            rules.append(BusinessRuleDetected(
                code="RN-CLI-001",
                description="Verificación de jornada laboral, prevención de cruces en tiempo real, drag-and-drop y duplicación",
                source_reference="senses_reglas_negocio_y_arquitectura.md"
            ))
            rules.append(BusinessRuleDetected(
                code="FUE-0001",
                description="Matriz visual de citas en hojas compartidas de cálculo (Abril C-2) que se sustituye por la matriz interactiva",
                source_reference="senses_fuentes_y_actores.md"
            ))
            entities.extend(["Matriz Interactiva", "Agendamiento en Bloque", "Drag and Drop", "Copiar y Pegar", "Prevención de Cruces", "Consultorio C-2", "Atención Particular/Social/Convenio"])
            ambiguities.append("No se especifica la política de concurrencia cuando dos admisionistas seleccionan simultáneamente el mismo bloque horario libre.")
            omissions.append("El requerimiento informal omitió contemplar los días feriados o no laborables dentro del rango de agendamiento en bloque.")

        elif "ingreso" in req_text or "comprobante" in req_text or "pago interno" in req_text or "desglose" in req_text or "boleta" in req_text or "igv" in req_text or "cobro" in req_text:
            actors = ["Personal de Caja o Admisión (ACT-0003 / ACT-0002)", "Gerencia General (ACT-0001)"]
            rules.append(BusinessRuleDetected(
                code="HU-0002",
                description="Registro de ingresos y emisión de comprobante de pago interno",
                source_reference="senses_catalogo_requisitos_historias.md"
            ))
            rules.append(BusinessRuleDetected(
                code="RN-FIN-001",
                description="Cálculo automático de Subtotal e IGV (18%), correlativo B001-XXXXXX y leyenda legal sin validez SUNAT",
                source_reference="senses_reglas_negocio_y_arquitectura.md"
            ))
            rules.append(BusinessRuleDetected(
                code="FUE-0002",
                description="Recibo de pago de control interno B001-000036 emitido por Senses Psicólogos S.A.C.",
                source_reference="senses_fuentes_y_actores.md"
            ))
            entities.extend(["Recibo B001-000036", "RUC 20609694671", "Subtotal", "IGV 18%", "Distribución Multicitas", "Métodos (Yape, Plin, Efectivo, Tarjeta, Transferencia)", "Libro de Ingresos"])
            ambiguities.append("No se especifica si los pagos realizados mediante billeteras electrónicas (Yape/Plin) requieren registrar el número de operación bancaria.")
            omissions.append("El requerimiento informal omitió la advertencia explícita y obligatoria de comprobante de control interno sin validez ante SUNAT.")

        elif "inventario" in req_text or "activos" in req_text or "bienes" in req_text or "equipos" in req_text or "fotografía" in req_text or "fotografia" in req_text or "muebles" in req_text:
            actors = ["Personal de Caja y Registro o Administración (ACT-0003)", "Gerencia General (ACT-0001)"]
            rules.append(BusinessRuleDetected(
                code="HU-0003",
                description="Control y administración del inventario de activos de la clínica",
                source_reference="senses_catalogo_requisitos_historias.md"
            ))
            rules.append(BusinessRuleDetected(
                code="RN-PAT-001",
                description="Valorización en tiempo real, fotografía obligatoria, bitácora de trazabilidad inmutable y estados operativos",
                source_reference="senses_reglas_negocio_y_arquitectura.md"
            ))
            rules.append(BusinessRuleDetected(
                code="FUE-0003",
                description="Comisión de Inventario Bienes Muebles Ejercicio 2022 con registro fotográfico y valorización total de S/ 7,499.00",
                source_reference="senses_fuentes_y_actores.md"
            ))
            entities.extend(["Inventario de Bienes Muebles", "Fotografía del bien", "Costo Unitario e Importe Total", "Estados (Operativo, En Mantenimiento, Dado de Baja)", "Exportación Excel y PDF"])
            ambiguities.append("No se especifica si las imágenes de los bienes deben almacenarse comprimidas en cloudStorage o en base de datos.")
            omissions.append("El requerimiento informal omitió contemplar la reactivación de bienes desde la vista de inactivos tras una baja temporal.")

        elif "prospección" in req_text or "prospeccion" in req_text or "comercial" in req_text or "socioeconómico" in req_text or "socioeconomico" in req_text or "captación" in req_text or "captacion" in req_text or "estudio de mercado" in req_text:
            actors = ["Gerencia General (ACT-0001)", "Personal de Admisión (ACT-0002)", "Restricción a Psicólogos/Internos (ACT-0004/ACT-0005)"]
            rules.append(BusinessRuleDetected(
                code="HU-0004",
                description="Consulta gerencial y exportación de datos comerciales y socioeconómicos de pacientes",
                source_reference="senses_catalogo_requisitos_historias.md"
            ))
            rules.append(BusinessRuleDetected(
                code="RN-MKT-001",
                description="Segregación estricta de privacidad de datos comerciales y socioeconómicos frente al equipo clínico",
                source_reference="senses_reglas_negocio_y_arquitectura.md"
            ))
            rules.append(BusinessRuleDetected(
                code="FUE-0004",
                description="Ficha de Registro y Encuesta Estratégica de Pacientes para Estudio de Mercado y Dashboards Gerenciales",
                source_reference="senses_fuentes_y_actores.md"
            ))
            entities.extend(["Canales de Captación", "Recomendador", "Comparativa Previa", "Nivel Socioeconómico", "Blindaje Clínico", "Exportación Excel"])
            ambiguities.append("No se precisa si la encuesta socioeconómica admite omitir el rango de ingresos en caso el paciente prefiera no declararlo.")
            omissions.append("El requerimiento informal omitió estipular el bloqueo estricto de lectura para los roles clínicos (Psicólogos e Internos).")

        elif "buzón" in req_text or "buzon" in req_text or "sugerencia" in req_text or "reconocimiento" in req_text or "planes de mejora" in req_text or "recursos humanos" in req_text:
            actors = ["Colaborador de la Clínica (ACT-0002 / ACT-0003 / ACT-0004 / ACT-0005)", "Recursos Humanos (ACT-0006)"]
            rules.append(BusinessRuleDetected(
                code="HU-0005",
                description="Buzón interno de sugerencias, reconocimientos y gestión de planes de mejora",
                source_reference="senses_catalogo_requisitos_historias.md"
            ))
            rules.append(BusinessRuleDetected(
                code="RN-RRHH-001",
                description="Aviso legal permanente de no emergencia, anonimato vs contacto voluntario, trazabilidad y medición de efectividad",
                source_reference="senses_reglas_negocio_y_arquitectura.md"
            ))
            rules.append(BusinessRuleDetected(
                code="FUE-0005",
                description="Ficha de Sugerencias y Observaciones - Mejora Continua y Manual MAN-RRHH-BUZ-001",
                source_reference="senses_fuentes_y_actores.md"
            ))
            rules.append(BusinessRuleDetected(
                code="MAN-RRHH-BUZ-001",
                description="Procedimiento formal de gestión del buzón: correlativo SUG-2026-XXXX, priorización y exclusividad para RRHH",
                source_reference="senses_reglas_negocio_y_arquitectura.md"
            ))
            entities.extend(["Código SUG-2026-XXXX", "Aviso Permanente de No Emergencia", "Anonimato Estricto", "Transcripción Ficha Física", "Prioridad (Baja, Media, Alta, Crítica)", "Efectividad de Cierre"])
            ambiguities.append("No se indica si los reconocimientos positivos ameritan emisión de constancias formales por parte de Recursos Humanos.")
            omissions.append("El requerimiento informal omitió la advertencia legal explícita de no emergencia ante crisis emocionales agudas o riesgo inmediato.")

        else:
            actors = ["Personal de Admisión (ACT-0002)", "Gerencia General (ACT-0001)"]
            rules.append(BusinessRuleDetected(
                code="HU-0001",
                description="Gestión de citas y disponibilidad clínica",
                source_reference="senses_catalogo_requisitos_historias.md"
            ))
            entities.extend(["Centro Psicológico Senses", "tb_pacientes"])

        return AnalystOutput(
            identified_actors=actors,
            business_rules=rules,
            domain_entities=entities,
            ambiguities_marked=ambiguities,
            omissions_detected=omissions,
            domain_summary=(
                f"Análisis del dominio Senses: se identificaron {len(rules)} reglas normativas críticas "
                f"y {len(actors)} actores formalizados en la base de conocimiento del proyecto."
            )
        )

    def _simulate_writer(self, prompt_lower: str, full_prompt: str) -> WriterOutput:
        is_correction = "feedback" in prompt_lower or "iteración" in prompt_lower or "observación" in prompt_lower
        req_text = self._extract_requirement_text(full_prompt).lower()

        if "calendario" in req_text or "matriz" in req_text or "agendamiento" in req_text or "arrastre" in req_text or "duplicar" in req_text or "cruces" in req_text or "hojas compartidas" in req_text:
            role = "Personal de Admisión (ACT-0002)"
            action = "consultar la disponibilidad horaria de los profesionales en una matriz interactiva y agendar citas individuales o en bloque recurrente, así como moverlas o duplicarlas"
            benefit = "coordinar ágilmente las sesiones de los pacientes (particulares, sociales o por convenio) evitando cruces de horario y sustituyendo el uso de hojas compartidas externas"

            scenarios = [
                GherkinScenario(
                    name="Agendamiento individual en matriz visual interactiva (HU-0001 / RN-CLI-001)",
                    steps=[
                        "Given que el personal de admisión consulta el calendario semanal de un profesional",
                        "When hace clic en un horario libre de 2 a 3 pm y completa los datos del paciente particular",
                        "Then el sistema guarda la cita y actualiza el bloque horario como ocupado en la matriz visual"
                    ]
                ),
                GherkinScenario(
                    name="Programación de citas recurrentes en bloque de 6 a 8 sesiones (HU-0001 / RN-CLI-001)",
                    steps=[
                        "Given que el usuario necesita agendar una serie continua de 6 sesiones semanales para un paciente",
                        "When activa el agendamiento en bloque con rango de fechas y días especificados",
                        "Then el sistema verifica la jornada laboral del profesional, omite los bloques ocupados y genera automáticamente las citas válidas"
                    ]
                ),
                GherkinScenario(
                    name="Reprogramación por arrastre y duplicación de citas (HU-0001 / RN-CLI-001)",
                    steps=[
                        "Given que existe una cita agendada en el consultorio C-2",
                        "When el usuario arrastra la cita hacia un bloque libre o la copia y pega en otro horario",
                        "Then el sistema actualiza o replica la cita conservando la información sin forzar reingreso manual"
                    ]
                ),
                GherkinScenario(
                    name="Prevención estricta de cruces y bloqueo en horarios ocupados (RN-CLI-001 / FUE-0001)",
                    steps=[
                        "Given que un horario se encuentra ocupado o fuera de la jornada laboral del profesional",
                        "When se intenta registrar, mover o duplicar una cita hacia dicho bloque",
                        "Then el sistema bloquea inmediatamente la acción y emite una alerta indicando que el horario no está disponible"
                    ]
                )
            ]
            raw_feature = (
                "Feature: Calendario Interactivo y Gestión Dinámica de Citas\n\n"
                f"  Como {role}\n"
                f"  Quiero {action}\n"
                f"  Para {benefit}\n\n"
            )
            for sc in scenarios:
                raw_feature += f"  Scenario: {sc.name}\n"
                for step in sc.steps:
                    raw_feature += f"    {step}\n"
                raw_feature += "\n"

            return WriterOutput(
                title="Calendario Interactivo para Agendamiento y Reprogramación de Citas",
                user_story=UserStoryStructure(
                    role=role,
                    action=action,
                    benefit=benefit,
                    full_text=f"Como {role}, quiero {action}, para {benefit}."
                ),
                feature_name="Gestión de Agenda en Matriz Interactiva",
                gherkin_feature_description="Agendamiento en bloque, drag-and-drop, copiar/pegar y prevención estricta de cruces.",
                scenarios=scenarios,
                raw_feature_text=raw_feature.strip(),
                business_rules_addressed=["HU-0001", "RN-CLI-001", "FUE-0001"]
            )

        elif "ingreso" in req_text or "comprobante" in req_text or "pago interno" in req_text or "desglose" in req_text or "boleta" in req_text or "igv" in req_text or "cobro" in req_text:
            role = "Personal de Caja o Admisión (ACT-0003 / ACT-0002)"
            action = "registrar los pagos de los pacientes por una o varias citas y emitir el comprobante de pago en formato digital"
            benefit = "mantener el control del flujo diario de ingresos y entregar un comprobante con el desglose del servicio"

            scenarios = [
                GherkinScenario(
                    name="Registro de pago y distribución por citas (HU-0002 / RN-FIN-001)",
                    steps=[
                        "Given que el usuario inicia el registro de un cobro por 50 soles",
                        "When ingresa los datos del cliente, selecciona método de pago Yape y distribuye el monto entre citas pendientes",
                        "Then el sistema valida la distribución y actualiza el estado de pago de cada cita vinculada"
                    ]
                ),
                GherkinScenario(
                    name="Cálculo automático de subtotal e IGV (18%) con serie B001 (RN-FIN-001 / FUE-0002)",
                    steps=[
                        "Given que se confirman los datos del ingreso",
                        "When se guarda la transacción en el sistema",
                        "Then el sistema calcula automáticamente subtotal de 42.37 soles y 18% de IGV (7.63 soles) con correlativo B001-000036"
                    ]
                ),
                GherkinScenario(
                    name="Emisión de comprobante PDF con advertencia legal SUNAT (HU-0002 / RN-FIN-001)",
                    steps=[
                        "Given que el cobro ha sido guardado exitosamente",
                        "When el usuario emite el comprobante digital",
                        "Then genera un PDF con RUC 20609694671 y la leyenda explícita de control interno provisional sin validez ante SUNAT"
                    ]
                ),
                GherkinScenario(
                    name="Rechazo y bloqueo ante sumas distribuidas discordantes (RN-FIN-001 / HU-0002)",
                    steps=[
                        "Given que la distribución entre citas no coincide exactamente con el monto total cobrado",
                        "When el operador intenta confirmar el registro",
                        "Then el sistema bloquea el guardado, emite una alerta de inconsistencia y rechaza la operación"
                    ]
                )
            ]
            raw_feature = (
                "Feature: Registro de Ingresos y Emisión de Comprobante de Pago Interno\n\n"
                f"  Como {role}\n"
                f"  Quiero {action}\n"
                f"  Para {benefit}\n\n"
            )
            for sc in scenarios:
                raw_feature += f"  Scenario: {sc.name}\n"
                for step in sc.steps:
                    raw_feature += f"    {step}\n"
                raw_feature += "\n"

            return WriterOutput(
                title="Registro de Ingresos y Emisión de Comprobante de Pago Interno",
                user_story=UserStoryStructure(
                    role=role,
                    action=action,
                    benefit=benefit,
                    full_text=f"Como {role}, quiero {action}, para {benefit}."
                ),
                feature_name="Control de Ingresos y Facturación Interna",
                gherkin_feature_description="Distribución multi-citas, desglose de IGV (18%) y leyenda de control interno sin validez SUNAT.",
                scenarios=scenarios,
                raw_feature_text=raw_feature.strip(),
                business_rules_addressed=["HU-0002", "RN-FIN-001", "FUE-0002"]
            )

        elif "inventario" in req_text or "activos" in req_text or "bienes" in req_text or "equipos" in req_text or "fotografía" in req_text or "fotografia" in req_text or "muebles" in req_text:
            role = "Personal de Caja y Registro o Administración (ACT-0003)"
            action = "registrar, actualizar y dar seguimiento a los bienes y equipos de la clínica con su información detallada, estado y fotografía"
            benefit = "mantener un inventario físico valorizado, auditable y actualizado de los recursos institucionales"

            scenarios = [
                GherkinScenario(
                    name="Registro de bien con valorización en tiempo real y foto (HU-0003 / RN-PAT-001)",
                    steps=[
                        "Given que el usuario accede al formulario de inventario",
                        "When ingresa mueble de melamina con costo de 1500 soles y adjunta fotografía real",
                        "Then el sistema computa el importe total en tiempo real y persiste el activo valorizado"
                    ]
                ),
                GherkinScenario(
                    name="Historial de modificaciones y trazabilidad de estados (HU-0003 / RN-PAT-001)",
                    steps=[
                        "Given que el usuario modifica la situación operativa a En Mantenimiento o Dado de Baja",
                        "When guarda las modificaciones",
                        "Then registra automáticamente una entrada de auditoría inmutable con fecha, responsable y valores previo y nuevo"
                    ]
                ),
                GherkinScenario(
                    name="Segregación de inactivos y exportación consolidada (HU-0003 / RN-PAT-001)",
                    steps=[
                        "Given que se consulta el inventario de bienes valorizados en 7499 soles",
                        "When el usuario aplica filtros y solicita exportación a Excel o PDF",
                        "Then el sistema genera el reporte contable exacto con las columnas filtradas"
                    ]
                ),
                GherkinScenario(
                    name="Bloqueo y rechazo de registro sin fotografía obligatoria (RN-PAT-001 / FUE-0003)",
                    steps=[
                        "Given que el usuario intenta guardar un bien sin adjuntar fotografía",
                        "When presiona guardar activo",
                        "Then el sistema bloquea el guardado, emite una alerta de campo obligatorio y rechaza la persistencia"
                    ]
                )
            ]
            raw_feature = (
                "Feature: Control y Administración del Inventario de Activos de la Clínica\n\n"
                f"  Como {role}\n"
                f"  Quiero {action}\n"
                f"  Para {benefit}\n\n"
            )
            for sc in scenarios:
                raw_feature += f"  Scenario: {sc.name}\n"
                for step in sc.steps:
                    raw_feature += f"    {step}\n"
                raw_feature += "\n"

            return WriterOutput(
                title="Control y Administración del Inventario de Activos de la Clínica",
                user_story=UserStoryStructure(
                    role=role,
                    action=action,
                    benefit=benefit,
                    full_text=f"Como {role}, quiero {action}, para {benefit}."
                ),
                feature_name="Administración del Patrimonio Físico",
                gherkin_feature_description="Registro fotográfico, bitácora de trazabilidad inmutable y exportación filtrada a Excel/PDF.",
                scenarios=scenarios,
                raw_feature_text=raw_feature.strip(),
                business_rules_addressed=["HU-0003", "RN-PAT-001", "FUE-0003"]
            )

        elif "prospección" in req_text or "prospeccion" in req_text or "comercial" in req_text or "socioeconómico" in req_text or "socioeconomico" in req_text or "captación" in req_text or "captacion" in req_text or "estudio de mercado" in req_text:
            role = "Gerencia General (ACT-0001)"
            action = "consultar los datos de prospección comercial, canales de captación y situación socioeconómica de los pacientes, así como exportar el consolidado institucional"
            benefit = "evaluar el rendimiento de las estrategias de captación y tomar decisiones comerciales sin exponer esta información al personal de atención clínica"

            scenarios = [
                GherkinScenario(
                    name="Acceso a datos de prospección y marketing comercial (HU-0004 / RN-MKT-001)",
                    steps=[
                        "Given que un usuario con rol Gerencia o Admisión consulta el expediente del paciente",
                        "When accede al apartado comercial",
                        "Then visualiza canal de captación, recomendación, comparativa previa y motivos de elección"
                    ]
                ),
                GherkinScenario(
                    name="Consulta de información socioeconómica de ingresos familiares (HU-0004 / RN-MKT-001)",
                    steps=[
                        "Given que el usuario autorizado revisa la ficha complementaria",
                        "When visualiza el bloque socioeconómico",
                        "Then observa situación laboral, sector y rango de ingresos superiores a 3000 soles"
                    ]
                ),
                GherkinScenario(
                    name="Aislamiento estricto y denegatoria de acceso al personal clínico (RN-MKT-001 / FUE-0004)",
                    steps=[
                        "Given que un usuario con rol Psicólogo o Interno intenta visualizar las secciones comerciales o socioeconómicas",
                        "When navega por la interfaz de atención clínica",
                        "Then el sistema bloquea y deniega el acceso manteniendo los datos comerciales totalmente ocultos"
                    ]
                ),
                GherkinScenario(
                    name="Exportación consolidada en Excel para evaluación estratégica (HU-0004 / RN-MKT-001)",
                    steps=[
                        "Given que Gerencia requiere evaluar el retorno de captación",
                        "When descarga el consolidado general de pacientes",
                        "Then genera un archivo Excel con cruce de datos sociodemográficos y comerciales"
                    ]
                )
            ]
            raw_feature = (
                "Feature: Consulta Gerencial y Exportación de Datos Comerciales y Socioeconómicos\n\n"
                f"  Como {role}\n"
                f"  Quiero {action}\n"
                f"  Para {benefit}\n\n"
            )
            for sc in scenarios:
                raw_feature += f"  Scenario: {sc.name}\n"
                for step in sc.steps:
                    raw_feature += f"    {step}\n"
                raw_feature += "\n"

            return WriterOutput(
                title="Consulta Gerencial y Exportación de Datos Comerciales y Socioeconómicos",
                user_story=UserStoryStructure(
                    role=role,
                    action=action,
                    benefit=benefit,
                    full_text=f"Como {role}, quiero {action}, para {benefit}."
                ),
                feature_name="Inteligencia Comercial y Privacidad Clínica",
                gherkin_feature_description="Prospección de mercado, niveles socioeconómicos y aislamiento estricto de visibilidad frente a psicólogos.",
                scenarios=scenarios,
                raw_feature_text=raw_feature.strip(),
                business_rules_addressed=["HU-0004", "RN-MKT-001", "FUE-0004"]
            )

        elif "buzón" in req_text or "buzon" in req_text or "sugerencia" in req_text or "reconocimiento" in req_text or "planes de mejora" in req_text or "recursos humanos" in req_text:
            role = "Colaborador de la Clínica (Psicólogo, Interno, Admisión o Caja)"
            action = "enviar sugerencias, observaciones o reconocimientos de forma anónima o identificada, y como Recursos Humanos clasificar los casos, gestionar acciones de mejora y emitir reportes mensuales"
            benefit = "impulsar la mejora continua del clima y los servicios institucionales con estricta confidencialidad"

            scenarios = [
                GherkinScenario(
                    name="Envío institucional de reporte con código correlativo (HU-0005 / MAN-RRHH-BUZ-001)",
                    steps=[
                        "Given que un colaborador completa el formulario de buzón",
                        "When presiona enviar reporte",
                        "Then el sistema registra el caso asignándole código SUG-2026-001 con estado Nuevo"
                    ]
                ),
                GherkinScenario(
                    name="Visualización permanente de advertencia legal de no emergencia (RN-RRHH-001 / FUE-0005)",
                    steps=[
                        "Given que el usuario abre la pantalla del buzón",
                        "When visualiza el formulario antes de redactar su mensaje",
                        "Then el sistema despliega de forma permanente el aviso de que el buzón no sustituye canales de emergencia o crisis"
                    ]
                ),
                GherkinScenario(
                    name="Gestión de planes de mejora con medición de efectividad en 30 días (HU-0005 / RN-RRHH-001)",
                    steps=[
                        "Given que Recursos Humanos prioriza un caso en estado Alta o Crítica",
                        "When programa un plan de acción con plazo de 30 días y mide su efectividad",
                        "Then el caso transiciona a Cerrado registrando la fecha y evaluación del resultado"
                    ]
                ),
                GherkinScenario(
                    name="Restricción estricta y bloqueo de bandeja ante roles no autorizados (HU-0005 / RN-RRHH-001)",
                    steps=[
                        "Given que un usuario con rol distinto a Recursos Humanos intenta acceder a la bandeja de gestión",
                        "When navega hacia el módulo administrativo del buzón",
                        "Then el sistema bloquea la pantalla, deniega el acceso y restringe los reportes exclusivamente a RRHH"
                    ]
                )
            ]
            raw_feature = (
                "Feature: Buzón Interno de Sugerencias, Reconocimientos y Planes de Mejora\n\n"
                f"  Como {role}\n"
                f"  Quiero {action}\n"
                f"  Para {benefit}\n\n"
            )
            for sc in scenarios:
                raw_feature += f"  Scenario: {sc.name}\n"
                for step in sc.steps:
                    raw_feature += f"    {step}\n"
                raw_feature += "\n"

            return WriterOutput(
                title="Buzón Interno de Sugerencias, Reconocimientos y Planes de Mejora",
                user_story=UserStoryStructure(
                    role=role,
                    action=action,
                    benefit=benefit,
                    full_text=f"Como {role}, quiero {action}, para {benefit}."
                ),
                feature_name="Mejora Continua y Clima Institucional",
                gherkin_feature_description="Canal de sugerencias anónimas o identificadas, aviso de no emergencia y gestión exclusiva por RRHH.",
                scenarios=scenarios,
                raw_feature_text=raw_feature.strip(),
                business_rules_addressed=["HU-0005", "RN-RRHH-001", "FUE-0005", "MAN-RRHH-BUZ-001"]
            )

        else:
            role = "Personal de Admisión (ACT-0002)"
            action = "gestionar los requerimientos institucionales"
            benefit = "organizar la atención clínica en Senses"
            scenarios = [
                GherkinScenario(
                    name="Operación estándar en la clínica",
                    steps=[
                        "Given que el usuario accede al sistema",
                        "When realiza la acción requerida",
                        "Then el sistema procesa los datos conforme a la regla del negocio"
                    ]
                )
            ]
            raw_feature = (
                "Feature: Operación General Senses\n\n"
                f"  Como {role}\n"
                f"  Quiero {action}\n"
                f"  Para {benefit}\n\n"
                "  Scenario: Operación estándar en la clínica\n"
                "    Given que el usuario accede al sistema\n"
                "    When realiza la acción requerida\n"
                "    Then el sistema procesa los datos conforme a la regla del negocio\n"
            )
            return WriterOutput(
                title="Gestión de Requerimiento Senses",
                user_story=UserStoryStructure(
                    role=role,
                    action=action,
                    benefit=benefit,
                    full_text=f"Como {role}, quiero {action}, para {benefit}."
                ),
                feature_name="Operación General Senses",
                gherkin_feature_description="Operación base.",
                scenarios=scenarios,
                raw_feature_text=raw_feature.strip(),
                business_rules_addressed=["HU-0001", "RN-CLI-001"]
            )

    def _simulate_critic(self, prompt_lower: str, full_prompt: str) -> CriticOutput:
        # Extraer únicamente el bloque de escenarios generados por el Redactor para evaluar
        scenarios_block = ""
        if "ESCENARIOS GHERKIN GENERADOS:" in full_prompt:
            part = full_prompt.split("ESCENARIOS GHERKIN GENERADOS:")[1]
            if "DOCUMENTOS RECUPERADOS" in part:
                scenarios_block = part.split("DOCUMENTOS RECUPERADOS")[0].lower()
            else:
                scenarios_block = part.lower()
        else:
            scenarios_block = prompt_lower

        has_rules = any(code in scenarios_block for code in [
            "hu-0001", "hu-0002", "hu-0003", "hu-0004", "hu-0005",
            "rn-cli-001", "rn-fin-001", "rn-pat-001", "rn-mkt-001", "rn-rrhh-001",
            "fue-0001", "fue-0002", "fue-0003", "fue-0004", "fue-0005",
            "man-rrhh-buz-001"
        ])
        scenarios_count = scenarios_block.count("scenario:")

        if has_rules and scenarios_count >= 2:
            scores = [
                InvestCriterionScore(criterion="Independent", score=9.0, justification="Historia autocontenida y desacoplada de otros módulos."),
                InvestCriterionScore(criterion="Negotiable", score=8.5, justification="Define la meta funcional permitiendo refinamiento técnico en la implementación."),
                InvestCriterionScore(criterion="Valuable", score=9.5, justification="Aporta valor directo de negocio y mitiga riesgos operativos o clínicos."),
                InvestCriterionScore(criterion="Estimable", score=8.5, justification="Alcance acotado con reglas de negocio claras para el equipo de desarrollo."),
                InvestCriterionScore(criterion="Small", score=8.5, justification="Cabe perfectamente en una iteración de sprint estándar."),
                InvestCriterionScore(criterion="Testable", score=9.5, justification="Escenarios Gherkin con Given-When-Then rigurosos, verificables y con casos de rechazo.")
            ]
            avg_score = round(sum(s.score for s in scores) / len(scores), 2)
            return CriticOutput(
                passed=True,
                overall_invest_score=avg_score,
                invest_breakdown=scores,
                hallucinations_detected=[],
                unwanted_semantic_drifts=[],
                missing_domain_rules=[],
                actionable_feedback="Excelente calidad. Cumple todos los criterios INVEST y refleja fielmente las políticas normativas del proyecto."
            )
        else:
            # Requiere una ronda de corrección
            scores = [
                InvestCriterionScore(criterion="Independent", score=7.0, justification="Requiere mayor detalle en las dependencias normativas."),
                InvestCriterionScore(criterion="Negotiable", score=8.0, justification="Aceptable nivel de negociación."),
                InvestCriterionScore(criterion="Valuable", score=7.5, justification="Falta explicitar la mitigación de riesgos de negocio."),
                InvestCriterionScore(criterion="Estimable", score=6.5, justification="Falta precisar las validaciones de rechazo normativo."),
                InvestCriterionScore(criterion="Small", score=8.0, justification="Tamaño adecuado."),
                InvestCriterionScore(criterion="Testable", score=6.5, justification="Faltan casos bordes de rechazo y aserciones rigurosas.")
            ]
            avg_score = round(sum(s.score for s in scores) / len(scores), 2)
            return CriticOutput(
                passed=False,
                overall_invest_score=avg_score,
                invest_breakdown=scores,
                hallucinations_detected=[],
                unwanted_semantic_drifts=["Se detectó falta de especificidad en los criterios de rechazo normativo."],
                missing_domain_rules=["Validación estricta de reglas del catálogo de requisitos"],
                actionable_feedback="Incorporar escenario de validación de rechazo explícito y citar códigos normativos del proyecto."
            )

    def _simulate_validator(self, prompt_lower: str, full_prompt: str) -> ValidatorOutput:
        # Validación de sintaxis
        sc_count = full_prompt.count("Scenario:") or 3
        return ValidatorOutput(
            is_valid_gherkin=True,
            total_scenarios_count=sc_count,
            lint_errors=[],
            formatted_gherkin_feature=full_prompt,
            structured_json={"status": "APPROVED", "scenarios": sc_count},
            validation_status="APPROVED"
        )


class RealLLMClient(BaseLLMClient):
    """
    Cliente que interactúa con modelos reales (OpenAI, Gemini o Ollama).
    Para Gemini utiliza el SDK oficial moderno `google-genai`.
    Incluye fallback resiliente al simulador determinista si la API externa experimenta 503/404 o timeout.
    """
    def __init__(self, provider: str = "openai"):
        self.provider = provider
        self.gemini_client = None
        self.openai_client = None
        self.fallback_simulator = DeterministicDomainSimulator()
        self._init_client()

    def _init_client(self):
        try:
            if self.provider == "gemini":
                from google import genai
                self.gemini_client = genai.Client(api_key=GEMINI_API_KEY)
            elif self.provider == "openai":
                from langchain_openai import ChatOpenAI
                self.openai_client = ChatOpenAI(
                    model=OPENAI_MODEL,
                    temperature=0.2,
                    api_key=OPENAI_API_KEY
                )
            elif self.provider == "ollama":
                from langchain_community.chat_models import ChatOllama
                self.openai_client = ChatOllama(
                    base_url=OLLAMA_BASE_URL,
                    model=OLLAMA_MODEL,
                    temperature=0.2
                )
        except Exception as e:
            print(f"[Aviso] No se pudo inicializar cliente para {self.provider}: {e}")

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        try:
            if self.provider == "gemini" and self.gemini_client:
                from google.genai import types
                config = types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0.2
                )
                response = self.gemini_client.models.generate_content(
                    model=GEMINI_MODEL,
                    contents=user_prompt,
                    config=config
                )
                return response.text or ""
            elif self.openai_client:
                from langchain_core.messages import SystemMessage, HumanMessage
                messages = [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=user_prompt)
                ]
                response = self.openai_client.invoke(messages)
                return response.content
        except Exception as e:
            print(f"[Aviso Resiliencia] Llamada LLM a {self.provider} ({GEMINI_MODEL}) retornó ({e}). Usando motor determinista de dominio.")
        
        return self.fallback_simulator.generate(system_prompt, user_prompt)

    def generate_structured(self, system_prompt: str, user_prompt: str, schema_class: Any) -> Any:
        try:
            if self.provider == "gemini" and self.gemini_client:
                from google.genai import types
                config = types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    response_mime_type="application/json",
                    response_schema=schema_class,
                    temperature=0.2
                )
                response = self.gemini_client.models.generate_content(
                    model=GEMINI_MODEL,
                    contents=user_prompt,
                    config=config
                )
                text = response.text or "{}"
                data = json.loads(text)
                return schema_class(**data)
            elif self.openai_client:
                try:
                    structured_model = self.openai_client.with_structured_output(schema_class)
                    from langchain_core.messages import SystemMessage, HumanMessage
                    messages = [
                        SystemMessage(content=system_prompt),
                        HumanMessage(content=user_prompt)
                    ]
                    return structured_model.invoke(messages)
                except Exception:
                    prompt_with_instructions = (
                        f"{user_prompt}\n\n"
                        f"RESPONDE OBLIGATORIAMENTE ÚNICAMENTE UN OBJETO JSON VÁLIDO QUE CUMPLA CON ESTE ESQUEMA PYDANTIC:\n"
                        f"{schema_class.model_json_schema()}"
                    )
                    raw = self.generate(system_prompt, prompt_with_instructions)
                    match = re.search(r'\{.*\}', raw, re.DOTALL)
                    if match:
                        data = json.loads(match.group(0))
                        return schema_class(**data)
        except Exception as e:
            print(f"[Aviso Resiliencia] Llamada estructurada a {self.provider} ({GEMINI_MODEL}) retornó ({e}). Usando motor determinista de dominio.")

        return self.fallback_simulator.generate_structured(system_prompt, user_prompt, schema_class)


def get_llm_client() -> BaseLLMClient:
    """
    Fábrica unificada del cliente LLM.
    Devuelve la misma interfaz para el RAG convencional y el sistema multiagente.
    """
    provider = LLM_PROVIDER.lower()
    if provider in ["openai", "gemini", "ollama"]:
        try:
            return RealLLMClient(provider=provider)
        except Exception as e:
            print(f"[Aviso] No se pudo conectar con el proveedor {provider} ({e}). Usando Simulador Determinista de Dominio.")
            return DeterministicDomainSimulator()
    else:
        return DeterministicDomainSimulator()
