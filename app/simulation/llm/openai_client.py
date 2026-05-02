import os
from openai import OpenAI, OpenAIError
from app. simulation.llm.base import LLMError, LLMMessage, LLMResponse

class OpenAiClient:

    def __init__(self, model: str = "gpt-5.4") -> None: #Modell anpassen!
        api_key = os.getenv("OPENAI_API_KEY")
        self._client = OpenAI(api_key=api_key)
        self._model = model

    def chat(self,
             system_prompt: str,
             messages: list[LLMMessage],
             *,
             max_tokens: int = 500,
             temperature: float = 0.7,
             json_mode: bool = False
             ) -> str:
        payload = [{"role": "system", "content": system_prompt}]
        payload.extend({"role": m.role, "content": m.content} for m in messages)

        try:
            kwargs={
                "model": self._model,
                "messages": payload,
               # "max_tokens": max_tokens,
               # "temperature": temperature,
            }
            if json_mode:
                kwargs["response_format"]={"type":"json_object"}



            response = self._client.chat.completions.create(**kwargs)#richtig so?
        except OpenAIError as exc:
            raise LLMError(f"OpenAi request failed: {exc}") from exc

        return LLMResponse(
            text= response.choices[0].message.content or "",
            tokens_used=response.usage.total_tokens if response.usage else None,
        )

                #response.choices[0].message.content or "")