import os
from functools import lru_cache

from app.simulation.llm.base import LLMMessage, LLMClient, LLMError
from dotenv import load_dotenv
load_dotenv()

# lru_cache sorgt dafür, dass der Client genau einmal pro Prozess gebaut wird
# Vorteil: Ruft nur einmal auf, nachtiel: Wenn man den Provider wechseln will muss man get_llm_client.cache_clear() aufrufen
@lru_cache(maxsize=1)
def get_llm_client() -> LLMClient:
    """Return the configured LLM client (chached for the process lieftime)"""
    provider = os.getenv("LLM_Provider", "openai").lower()

    if provider == "openai":
        from app.simulation.llm.openai_client import OpenAiClient
        return OpenAiClient()
    if provider == "anthropic":
        from app.simulation.llm.anthropic_client import AnthropicClient
        return AnthropicClient()
    if provider == "lmstudio":
        from app.simulation.llm.lmstudio_client import LMStudioClient
        return LMStudioClient()
    raise LLMError(f"Unknown LLM_Provider")


__all__ = ["LLMClient", "LLMError", "LLMMessage", "get_llm_client"]
