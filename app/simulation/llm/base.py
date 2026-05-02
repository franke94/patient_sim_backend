from dataclasses import dataclass
from typing import Literal, Protocol

Role = Literal["system", "user", "assistant"]


#Datacalss ist sauberer als JSON, da die Form begrenzt ist
@dataclass
class LLMMessage:
    """Provider agnostic chat message"""
    role: Role
    content: str

@dataclass
class LLMResponse:
    """Provider-agnostic chat response"""
    text: str
    tokens_used: int | None


class LLMClient(Protocol):
    """Any LLM provider must implement this single method"""

    def chat(
        self,
        system_prompt: str,
        messages: list[LLMMessage], #System Prompt und messages getrennt um flexibel hinsichtlich des Mdoells zu sein
        *,
        max_tokens = 500,
        temperature: float = 0.7, #Kann man später wieder streichen?
        json_mode: bool = False,
        ) -> LLMResponse:
        """Return the assistants's reply text and provider usage info"""
        ...

class LLMError(Exception):
    """Raised when an LLM provider fails (Network, auth, rate-limit,..."""