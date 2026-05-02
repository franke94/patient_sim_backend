from enum import Enum


class SeverityEnum(str, Enum):
    """Gibt die Schwere der ABCDE + Injuries an"""
    NONE = "none"
    MILD = "mild"
    SEVERE = "severe"
    CRITICAL = "critical"


class SourceEnum(str, Enum):
    """Gibt an, wo die einschätzung herkommt. """
    CASE_TRUTH = "case_truth"
    CALL_TAKER = "call_taker"
    AI_AGENT = "ai_agent"


class CategoryEnum(str, Enum):
    """Gibt die Kategorie im ABCDE Schema an"""
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"


class AgentTypeEnum(str, Enum):
    """Gibt die Art des Agents an"""
    A_AGENT = "a_agent"
    B_AGENT = "b_agent"
    C_AGENT = "c_agent"
    D_AGENT = "d_agent"
    E_AGENT = "e_agent"
    LOCATION_AGENT = "location_agent"
    INJURY_AGENT = "injury_agent"
    SINGLE_AGENT = "single_agent"


class MessageRoleEnum(str, Enum):
    """Für die LLM Anfragen"""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class CallStatusEnum(str, Enum):
    """"""
    RUNNING = "running"
    COMPLETED = "completed"


class AgentRunStatusEnum(str, Enum):
    """Für die """
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"

