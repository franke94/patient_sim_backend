"""Anthropic Claude implementation of the LLMClient protocol."""
import os

from anthropic import Anthropic, AnthropicError

from app.simulation.llm.base import LLMError, LLMMessage, LLMResponse


class AnthropicClient:
    """Calls Anthropic's Messages API."""

    def __init__(self, model: str = "claude-haiku-4-5-20251001") -> None:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise LLMError("ANTHROPIC_API_KEY is not set")
        self._client = Anthropic(api_key=api_key)
        self._model = model

    def chat(
        self,
        system_prompt: str,
        messages: list[LLMMessage],
        *,
        max_tokens: int = 500,
        temperature: float = 0.7,
        json_mode: bool = False
    ) -> str:
        # Anthropic erlaubt nur 'user' und 'assistant' im messages-Array.
        # 'system'-Inhalte gehen in den separaten system-Parameter.
        api_messages = [
            {"role": m.role, "content": m.content}
            for m in messages
            if m.role in ("user", "assistant")
        ]

        if json_mode:
            system_prompt += (
                "\n\nWICHTIG: Antworte ausschließlich mit gültigem JSON. "
        "Kein Markdown, kein Fließtext, keine Code-Fences. Nur das JSON-Objekt.")


        try:
            response = self._client.messages.create(
                model=self._model,
                system=system_prompt,
                messages=api_messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )
        except AnthropicError as exc:
            raise LLMError(f"Anthropic request failed: {exc}") from exc

        # Antworten kommen als content-blocks; uns interessiert der erste Text-Block.
        first = response.content[0]

        text = getattr(first, "text", "") or ""
        usage = response.usage
        tokens = (usage.input_tokens + usage.output_tokens) if usage else None
        return LLMResponse(text=text, tokens_used=tokens)

        #return getattr(first, "text", "") or ""