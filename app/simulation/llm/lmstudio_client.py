import os
from openai import OpenAI, OpenAIError
from app.simulation.llm.base import LLMError, LLMMessage, LLMResponse


class LMStudioClient:
    """Client for a local LMStudio server (OpenAI-compatible API).

    Configurable via env-vars:
      - LMSTUDIO_BASE_URL  (default: http://localhost:1234/v1)
      - LMSTUDIO_MODEL     (default: local-model)
    """

    def __init__(
        self,
        base_url: str | None = None,
        model: str | None = None,
    ) -> None:
        self._base_url = base_url or os.getenv(
            "LMSTUDIO_BASE_URL", "http://localhost:1234/v1"
        )
        self._model = model or os.getenv("LMSTUDIO_MODEL", "local-model")
        # LMStudio braucht keine Auth, aber die OpenAI-SDK erwartet einen nicht-leeren key.
        self._client = OpenAI(base_url=self._base_url, api_key="lm-studio")

    def chat(
        self,
        system_prompt: str,
        messages: list[LLMMessage],
        *,
        max_tokens: int = 500,
        temperature: float = 0.7,
        json_mode: bool = False,
    ) -> LLMResponse:
        payload = [{"role": "system", "content": system_prompt}]
        payload.extend({"role": m.role, "content": m.content} for m in messages)

        kwargs = {
            "model": self._model,
            "messages": payload,
            "temperature": temperature,
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        try:
            response = self._client.chat.completions.create(**kwargs)
        except OpenAIError as exc:
            raise LLMError(f"LMStudio request failed: {exc}") from exc

        return LLMResponse(
            text=response.choices[0].message.content or "",
            tokens_used=response.usage.total_tokens if response.usage else None,
        )