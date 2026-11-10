"""
Fábrica de LLM unificada con logs de traza para depuración en consola.
Asegura validez interna estricta: ambos pipelines (RAG y Multiagente) consumen
exactamente la misma instancia o modelo.
Soporta OpenAI, Google Gemini, Ollama y NVIDIA NIM.
NO incluye simulador determinista: si la API real falla, lanza excepción
para evitar confundir resultados mock con resultados reales.
"""
import os
import json
import re
import time
from typing import Dict, Any, Optional, List, Iterator
from src.config import (
    LLM_PROVIDER,
    OPENAI_API_KEY,
    OPENAI_MODEL,
    GEMINI_API_KEY,
    GEMINI_MODEL,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    NVIDIA_API_KEY,
    NVIDIA_BASE_URL,
    NVIDIA_MODEL,
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
    def generate(self, system_prompt: str, user_prompt: str, stream: bool = False) -> str:
        raise NotImplementedError

    def generate_structured(self, system_prompt: str, user_prompt: str, schema_class: Any) -> Any:
        raise NotImplementedError


class RealLLMClient(BaseLLMClient):
    """
    Cliente que interactúa con modelos reales (OpenAI, Gemini, Ollama, NVIDIA NIM).
    NO hace fallback silencioso al simulador: reintenta hasta agotar intentos
    y, si persiste el error, lanza excepción.
    Incluye logs de traza en consola para supervisar tiempos y estados de cada llamada.
    """
    def __init__(self, provider: str = "nvidia", max_retries: int = 3, base_delay: float = 3.0):
        self.provider = provider
        self.gemini_client = None
        self.openai_client = None
        self.nvidia_client = None
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.call_counter = 0
        self._init_client()

    def _init_client(self):
        try:
            if self.provider == "gemini":
                from google import genai
                self.gemini_client = genai.Client(api_key=GEMINI_API_KEY)
                print(f"[LLM] Cliente Gemini inicializado (modelo: {GEMINI_MODEL})")
            elif self.provider == "openai":
                from langchain_openai import ChatOpenAI
                self.openai_client = ChatOpenAI(
                    model=OPENAI_MODEL,
                    temperature=0.0,
                    api_key=OPENAI_API_KEY
                )
                print(f"[LLM] Cliente OpenAI inicializado (modelo: {OPENAI_MODEL})")
            elif self.provider == "ollama":
                from langchain_community.chat_models import ChatOllama
                self.openai_client = ChatOllama(
                    base_url=OLLAMA_BASE_URL,
                    model=OLLAMA_MODEL,
                    temperature=0.0
                )
                print(f"[LLM] Cliente Ollama inicializado (modelo: {OLLAMA_MODEL})")
            elif self.provider == "nvidia":
                from langchain_openai import ChatOpenAI
                if not NVIDIA_API_KEY:
                    raise ValueError("NVIDIA_API_KEY no configurada en .env")
                self.nvidia_client = ChatOpenAI(
                    model=NVIDIA_MODEL,
                    temperature=0.0,
                    api_key=NVIDIA_API_KEY,
                    base_url=NVIDIA_BASE_URL,
                )
                print(f"[LLM] Cliente NVIDIA NIM inicializado (modelo: {NVIDIA_MODEL}, base: {NVIDIA_BASE_URL})")
        except Exception as e:
            print(f"[Error] No se pudo inicializar cliente para {self.provider}: {e}")
            raise

    def _retry_call(self, func, label: str, *args, **kwargs):
        """Ejecuta una llamada con reintentos exponenciales. No cae al mock."""
        last_error = None
        for attempt in range(1, self.max_retries + 1):
            try:
                print(f"[LLM] Enviando a {self.provider} — {label} (intento {attempt}/{self.max_retries})")
                start = time.time()
                result = func(*args, **kwargs)
                elapsed = time.time() - start
                print(f"[LLM] Respuesta recibida de {self.provider} — {label} en {elapsed:.2f}s")
                return result
            except Exception as e:
                last_error = e
                msg = str(e)
                if "503" in msg or "UNAVAILABLE" in msg or "high demand" in msg or "timeout" in msg.lower():
                    delay = self.base_delay * attempt
                    print(f"[LLM] {self.provider} no disponible ({msg[:90]}...). Reintentando en {delay}s...")
                    time.sleep(delay)
                else:
                    raise e
        print(f"[Error] {self.provider} falló tras {self.max_retries} intentos. Último error: {last_error}")
        raise last_error

    def generate(self, system_prompt: str, user_prompt: str, stream: bool = False) -> str:
        self.call_counter += 1
        label = f"generate #{self.call_counter}"

        def _call_nvidia_stream() -> str:
            from langchain_core.messages import SystemMessage, HumanMessage
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            print(f"[LLM] Streaming de {self.provider} — {label}")
            collected = []
            for chunk in self.nvidia_client.stream(messages):
                content = chunk.content or ""
                collected.append(content)
                print(content, end="", flush=True)
            print()  # nueva línea al final
            return "".join(collected)

        def _call_nvidia_normal() -> str:
            from langchain_core.messages import SystemMessage, HumanMessage
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            response = self.nvidia_client.invoke(messages)
            return response.content or ""

        def _call_gemini() -> str:
            from google.genai import types
            config = types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.0
            )
            response = self.gemini_client.models.generate_content(
                model=GEMINI_MODEL,
                contents=user_prompt,
                config=config
            )
            return response.text or ""

        def _call_openai() -> str:
            from langchain_core.messages import SystemMessage, HumanMessage
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            response = self.openai_client.invoke(messages)
            return response.content or ""

        if self.provider == "nvidia" and stream:
            return _call_nvidia_stream()
        elif self.provider == "nvidia":
            return self._retry_call(_call_nvidia_normal, label)
        elif self.provider == "gemini":
            return self._retry_call(_call_gemini, label)
        elif self.provider in ["openai", "ollama"]:
            return self._retry_call(_call_openai, label)
        else:
            raise RuntimeError(f"Cliente {self.provider} no inicializado")

    def generate_structured(self, system_prompt: str, user_prompt: str, schema_class: Any) -> Any:
        self.call_counter += 1
        label = f"generate_structured #{self.call_counter} ({schema_class.__name__})"

        def _call_nvidia() -> Any:
            from langchain_core.messages import SystemMessage, HumanMessage
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            try:
                structured_model = self.nvidia_client.with_structured_output(schema_class)
                return structured_model.invoke(messages)
            except Exception:
                # Fallback: generar texto libre y extraer JSON
                prompt_with_instructions = (
                    f"{user_prompt}\n\n"
                    f"RESPONDE OBLIGATORIAMENTE ÚNICAMENTE UN OBJETO JSON VÁLIDO QUE CUMPLA CON ESTE ESQUEMA PYDANTIC:\n"
                    f"{schema_class.model_json_schema()}"
                )
                raw = self.generate(system_prompt, prompt_with_instructions, stream=False)
                match = re.search(r'\{.*\}', raw, re.DOTALL)
                if match:
                    data = json.loads(match.group(0))
                    return schema_class(**data)
                raise ValueError("No se pudo extraer JSON válido de la respuesta")

        def _call_gemini() -> Any:
            from google.genai import types
            config = types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                response_schema=schema_class,
                temperature=0.0
            )
            response = self.gemini_client.models.generate_content(
                model=GEMINI_MODEL,
                contents=user_prompt,
                config=config
            )
            text = response.text or "{}"
            data = json.loads(text)
            return schema_class(**data)

        def _call_openai() -> Any:
            from langchain_core.messages import SystemMessage, HumanMessage
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            try:
                structured_model = self.openai_client.with_structured_output(schema_class)
                return structured_model.invoke(messages)
            except Exception:
                prompt_with_instructions = (
                    f"{user_prompt}\n\n"
                    f"RESPONDE OBLIGATORIAMENTE ÚNICAMENTE UN OBJETO JSON VÁLIDO QUE CUMPLA CON ESTE ESQUEMA PYDANTIC:\n"
                    f"{schema_class.model_json_schema()}"
                )
                raw = self.generate(system_prompt, prompt_with_instructions, stream=False)
                match = re.search(r'\{.*\}', raw, re.DOTALL)
                if match:
                    data = json.loads(match.group(0))
                    return schema_class(**data)
                raise ValueError("No se pudo extraer JSON válido de la respuesta")

        if self.provider == "nvidia":
            return self._retry_call(_call_nvidia, label)
        elif self.provider == "gemini":
            return self._retry_call(_call_gemini, label)
        elif self.provider in ["openai", "ollama"]:
            return self._retry_call(_call_openai, label)
        else:
            raise RuntimeError(f"Cliente {self.provider} no inicializado")


def get_llm_client() -> BaseLLMClient:
    """
    Fábrica unificada del cliente LLM.
    Devuelve SOLO cliente real. Si falla, lanza excepción (no usa mock).
    """
    provider = LLM_PROVIDER.lower()
    if provider in ["openai", "gemini", "ollama", "nvidia"]:
        return RealLLMClient(provider=provider)
    else:
        raise ValueError(f"Proveedor '{provider}' no soportado. Usa 'openai', 'gemini', 'ollama' o 'nvidia'.")
