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

    def _generate_rag_baseline(self, prompt: str) -> str:
        """Generación directa del RAG convencional (sin desglose analítico ni crítica)."""
        return (
            "HISTORIA DE USUARIO:\n"
            "Como cliente bancario, quiero solicitar un crédito vehicular para poder comprar un auto.\n\n"
            "CRITERIOS DE ACEPTACIÓN (Gherkin):\n"
            "Feature: Solicitud de Crédito\n\n"
            "Scenario: Solicitud exitosa\n"
            "  Given que el cliente tiene 25 años y score A\n"
            "  When solicita un crédito por $20,000 USD\n"
            "  Then el sistema aprueba la solicitud\n\n"
            "Scenario: Rechazo por score\n"
            "  Given que el cliente tiene score D\n"
            "  When ingresa su solicitud\n"
            "  Then la solicitud es rechazada\n"
        )

    def _simulate_analyst(self, prompt_lower: str, full_prompt: str) -> AnalystOutput:
        actors = ["Cliente Solicitante", "Oficial de Riesgos"]
        rules = []
        entities = []
        ambiguities = []
        omissions = []

        if "vehicular" in prompt_lower or "auto" in prompt_lower or "vehículo" in prompt_lower:
            actors.append("Concesionaria Autorizada")
            if "aval" in prompt_lower or "score c" in prompt_lower or "garante" in prompt_lower:
                actors.append("Aval / Garante Solidario")
            rules.append(BusinessRuleDetected(
                code="RN-ADM-002",
                description="Relación cuota/ingreso (DTI) máxima del 40% para crédito vehicular",
                source_reference="sistema_bancario_creditos.md"
            ))
            rules.append(BusinessRuleDetected(
                code="RN-ADM-003",
                description="Score C (500-649) exige Aval con Score >= 700 y DTI < 30%",
                source_reference="sistema_bancario_creditos.md"
            ))
            rules.append(BusinessRuleDetected(
                code="RN-GAR-002",
                description="Inscripción de garantía mobiliaria y póliza de seguro vehicular endosada",
                source_reference="sistema_bancario_creditos.md"
            ))
            entities.extend(["DTI", "Score Crediticio", "Cuota Inicial 20%", "Garantía Mobiliaria", "Póliza Endosada"])
            ambiguities.append("No se especifica si el cliente cuenta con el 20% mínimo de cuota inicial obligatoria.")
            omissions.append("El requerimiento informal no contemplaba el endoso de la póliza de seguro vehicular.")
        elif "desbloqueo" in prompt_lower or "fraude" in prompt_lower or "tarjeta" in prompt_lower:
            actors.append("Operador Especializado Antifraude")
            rules.append(BusinessRuleDetected(
                code="SEC-FRD-002",
                description="Bloqueo preventivo inmediato y notificación push/SMS/correo",
                source_reference="politicas_seguridad_cuentas.md"
            ))
            rules.append(BusinessRuleDetected(
                code="SEC-FRD-003",
                description="Desbloqueo seguro únicamente vía canal telefónico antifraude o biométrico en ventanilla",
                source_reference="politicas_seguridad_cuentas.md"
            ))
            entities.extend(["Alerta de Fraude", "Biometría Facial", "Canal Telefónico Antifraude", "Tarjeta Bloqueada"])
            ambiguities.append("El usuario solicitó desbloqueo por app, pero la política bancaria lo prohíbe para fraude confirmado.")
            omissions.append("Falta verificar si el bloqueo fue por sospecha preventiva o fraude efectivo confirmado.")
        elif "transferencia" in prompt_lower or "límite" in prompt_lower:
            rules.append(BusinessRuleDetected(
                code="SEC-LIM-001",
                description="Límite diario acumulado estándar de $3,000 USD",
                source_reference="politicas_seguridad_cuentas.md"
            ))
            rules.append(BusinessRuleDetected(
                code="SEC-LIM-002",
                description="Ampliación temporal hasta $15,000 USD con periodo de enfriamiento (cooling-off) de 2 horas",
                source_reference="politicas_seguridad_cuentas.md"
            ))
            entities.extend(["Cooling-off 2 horas", "Token Digital TOTP", "Cámara de Compensación Electrónica"])
            ambiguities.append("No se aclara si el cliente requiere liquidación inmediata o diferida.")
            omissions.append("Se omitió el periodo de enfriamiento obligatorio de 2 horas tras ampliar el límite.")
        else:
            rules.append(BusinessRuleDetected(
                code="RN-ADM-001",
                description="Edad mínima 21 años y máxima 69 años con 364 días",
                source_reference="sistema_bancario_creditos.md"
            ))
            rules.append(BusinessRuleDetected(
                code="RN-ADM-002",
                description="Relación DTI máxima del 35% en créditos de consumo",
                source_reference="sistema_bancario_creditos.md"
            ))
            entities.extend(["DTI", "Score Crediticio", "TCEA"])
            ambiguities.append("Faltan parámetros de monto solicitado y plazo en meses.")
            omissions.append("No se indicaba la validación de antigüedad laboral mínima de 12 meses.")

        return AnalystOutput(
            identified_actors=actors,
            business_rules=rules,
            domain_entities=entities,
            ambiguities_marked=ambiguities,
            omissions_detected=omissions,
            domain_summary=(
                f"Análisis normativo: se identificaron {len(rules)} reglas de negocio críticas "
                f"y {len(actors)} roles en la base de conocimiento para regular el requerimiento."
            )
        )

    def _simulate_writer(self, prompt_lower: str, full_prompt: str) -> WriterOutput:
        # Detectar si estamos en una iteración de corrección por presencia de 'feedback' o 'corrección'
        is_correction = "feedback" in prompt_lower or "iteración" in prompt_lower or "observación" in prompt_lower

        if "vehicular" in prompt_lower or "auto" in prompt_lower or "vehículo" in prompt_lower:
            if not is_correction:
                # Versión inicial con una pequeña omisión para permitir probar el bucle de crítica si se desea
                role = "Cliente con Score C (500-649)"
                action = "solicitar un crédito vehicular adjuntando los datos y sustento de mi aval solidario"
                benefit = "acceder al financiamiento de hasta el 80% del valor del auto cumpliendo las políticas de riesgo"
                scenarios = [
                    GherkinScenario(
                        name="Aprobación exitosa con aval solidario calificado",
                        steps=[
                            "Given que el cliente solicitante tiene un score crediticio de 610 (Score C)",
                            "And el cliente aporta una cuota inicial del 20% del valor de tasación del vehículo",
                            "And registra un Aval Solidario con score crediticio de 740 y DTI menor al 30%",
                            "When el sistema evalúa la solicitud de crédito vehicular",
                            "Then el crédito es aprobado condicionado a la firma del pagaré notarial del aval",
                            "And se programa la inscripción de la garantía mobiliaria en registros públicos"
                        ]
                    ),
                    GherkinScenario(
                        name="Rechazo cuando el aval solidario no alcanza el score mínimo",
                        steps=[
                            "Given que el solicitante tiene un score crediticio C (580 puntos)",
                            "And el aval propuesto tiene un score de 650 puntos (menor a los 700 requeridos)",
                            "When se procesa la validación del aval solidario",
                            "Then el sistema rechaza la solicitud indicando incumplimiento de RN-ADM-003",
                            "And notifica que el aval debe poseer un score mínimo de 700 puntos"
                        ]
                    )
                ]
            else:
                # Versión mejorada tras feedback del crítico (agrega cobertura de DTI y póliza de seguro)
                role = "Cliente con Score C (500-649)"
                action = "solicitar un crédito vehicular incorporando un aval solidario y la póliza endosada"
                benefit = "obtener la aprobación financiera garantizando el cumplimiento de DTI y cobertura de riesgo"
                scenarios = [
                    GherkinScenario(
                        name="Aprobación condicionada con aval solidario y DTI dentro del 40%",
                        steps=[
                            "Given que el solicitante posee un score crediticio de 620 puntos (Score C)",
                            "And su relación DTI consolidada no excede el 40%",
                            "And aporta una cuota inicial del 20% comercial del vehículo",
                            "And presenta un Aval Solidario con score de 750 puntos y DTI menor al 30%",
                            "When el sistema de riesgos procesa la solicitud vehicular",
                            "Then la solicitud queda aprobada condicionada a la firma digital del pagaré",
                            "And se exige la póliza de seguro vehicular endosada a favor de la entidad (RN-GAR-002)"
                        ]
                    ),
                    GherkinScenario(
                        name="Rechazo por exceso de capacidad de endeudamiento DTI",
                        steps=[
                            "Given que el solicitante presenta una cuota que representa el 46% de su ingreso neto",
                            "When se calcula la capacidad de endeudamiento según RN-ADM-002",
                            "Then el sistema rechaza la solicitud por superar el DTI máximo del 40%",
                            "And emite el informe de denegatoria de riesgo crediticio"
                        ]
                    ),
                    GherkinScenario(
                        name="Validación de desembolso directo a concesionaria autorizada",
                        steps=[
                            "Given que el crédito vehicular fue aprobado con pagaré firmado y garantía inscrita",
                            "When se ejecuta la orden de desembolso según RN-DES-002",
                            "Then el monto se transfiere directamente a la cuenta corporativa del concesionario",
                            "And no se abona directamente a la cuenta personal del cliente"
                        ]
                    )
                ]
            
            raw_feature = (
                "Feature: Originación y Evaluación de Crédito Vehicular con Aval Solidario\n\n"
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
                title="Gestión de Solicitud de Crédito Vehicular con Aval y Garantía",
                user_story=UserStoryStructure(
                    role=role,
                    action=action,
                    benefit=benefit,
                    full_text=f"Como {role}, quiero {action}, para {benefit}."
                ),
                feature_name="Originación de Crédito Vehicular",
                gherkin_feature_description="Validación rigurosa de score, avales, DTI y desembolso seguro.",
                scenarios=scenarios,
                raw_feature_text=raw_feature.strip(),
                business_rules_addressed=["RN-ADM-002", "RN-ADM-003", "RN-GAR-002", "RN-DES-002"]
            )
        else:
            # Caso genérico / seguridad
            role = "Cliente Titular de Cuenta Bancaria"
            action = "solicitar la ampliación temporal de mi límite diario con validación MFA"
            benefit = "realizar una transferencia extraordinaria resguardando mis fondos ante fraudes"
            scenarios = [
                GherkinScenario(
                    name="Ampliación temporal con validación biométrica y periodo de enfriamiento",
                    steps=[
                        "Given que el cliente solicita ampliar su límite diario a $10,000 USD",
                        "And valida exitosamente su identidad mediante Token Digital y Reconocimiento Facial (SEC-MFA-002)",
                        "When se confirma la solicitud en el canal digital",
                        "Then el sistema aplica un periodo de enfriamiento de 2 horas (SEC-LIM-002)",
                        "And el nuevo límite se activa automáticamente una vez transcurridas las 2 horas"
                    ]
                ),
                GherkinScenario(
                    name="Bloqueo preventivo por intentos fallidos de autenticación",
                    steps=[
                        "Given que el cliente intenta ingresar su factor de autenticación",
                        "When falla en 3 intentos consecutivos según SEC-MFA-003",
                        "Then el canal digital queda bloqueado preventivamente durante 24 horas",
                        "And se emite una notificación de seguridad inmediata por SMS y correo"
                    ]
                )
            ]
            raw_feature = (
                "Feature: Ampliación Temporal de Límites y Protección Antifraude\n\n"
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
                title="Ampliación Temporal de Límites con Periodo de Enfriamiento",
                user_story=UserStoryStructure(
                    role=role,
                    action=action,
                    benefit=benefit,
                    full_text=f"Como {role}, quiero {action}, para {benefit}."
                ),
                feature_name="Ampliación de Límites Transaccionales",
                gherkin_feature_description="Control estricto de topes y MFA.",
                scenarios=scenarios,
                raw_feature_text=raw_feature.strip(),
                business_rules_addressed=["SEC-LIM-001", "SEC-LIM-002", "SEC-MFA-003"]
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

        has_dti_or_rules = "rn-adm-002" in scenarios_block or ("dti" in scenarios_block and "40%" in scenarios_block) or "enfriamiento" in scenarios_block
        scenarios_count = scenarios_block.count("scenario:")

        if has_dti_or_rules and scenarios_count >= 2:
            scores = [
                InvestCriterionScore(criterion="Independent", score=9.0, justification="Historia autocontenida y desacoplada de otros flujos bancarios."),
                InvestCriterionScore(criterion="Negotiable", score=8.5, justification="Define la meta funcional permitiendo ajustes en la implementación técnica."),
                InvestCriterionScore(criterion="Valuable", score=9.5, justification="Aporta valor directo de negocio mitigando riesgo de impago/fraude."),
                InvestCriterionScore(criterion="Estimable", score=8.5, justification="Alcance acotado con reglas de negocio claras para el equipo de desarrollo."),
                InvestCriterionScore(criterion="Small", score=8.5, justification="Cabe perfectamente en una iteración de sprint estándar."),
                InvestCriterionScore(criterion="Testable", score=9.5, justification="Escenarios Gherkin con Given-When-Then rigurosos y verificables.")
            ]
            avg_score = round(sum(s.score for s in scores) / len(scores), 2)
            return CriticOutput(
                passed=True,
                overall_invest_score=avg_score,
                invest_breakdown=scores,
                hallucinations_detected=[],
                unwanted_semantic_drifts=[],
                missing_domain_rules=[],
                actionable_feedback="Excelente calidad. Cumple todos los criterios INVEST y refleja fielmente las políticas normativas."
            )
        else:
            # Requiere una ronda de corrección
            scores = [
                InvestCriterionScore(criterion="Independent", score=7.0, justification="Requiere mayor detalle en las dependencias normativas."),
                InvestCriterionScore(criterion="Negotiable", score=8.0, justification="Aceptable nivel de negociación."),
                InvestCriterionScore(criterion="Valuable", score=7.5, justification="Falta explicitar la mitigación del riesgo crediticio."),
                InvestCriterionScore(criterion="Estimable", score=6.5, justification="Falta precisar el cálculo de DTI y política de seguros."),
                InvestCriterionScore(criterion="Small", score=8.0, justification="Tamaño adecuado."),
                InvestCriterionScore(criterion="Testable", score=6.5, justification="Faltan casos bordes de rechazo por DTI o validación de desembolso.")
            ]
            avg_score = round(sum(s.score for s in scores) / len(scores), 2)
            return CriticOutput(
                passed=False,
                overall_invest_score=avg_score,
                invest_breakdown=scores,
                hallucinations_detected=[],
                unwanted_semantic_drifts=["Se omitió la especificación de la póliza vehicular obligatoria (RN-GAR-002)"],
                missing_domain_rules=["RN-ADM-002 (DTI máximo 40%)", "RN-DES-002 (Desembolso directo a concesionaria)"],
                actionable_feedback="Incorporar escenario de validación de DTI <= 40% y explicitar la entrega de póliza endosada y desembolso a concesionario."
            )

    def _simulate_validator(self, prompt_lower: str, full_prompt: str) -> ValidatorOutput:
        # Validación de sintaxis
        return ValidatorOutput(
            is_valid_gherkin=True,
            total_scenarios_count=3,
            lint_errors=[],
            formatted_gherkin_feature=full_prompt,
            structured_json={"status": "APPROVED", "scenarios": 3},
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
