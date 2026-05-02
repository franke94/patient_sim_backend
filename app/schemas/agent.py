from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.models.enums import AgentTypeEnum, AgentRunStatusEnum


#Wieso braucht man kein AgentRunCreate: der Server erzeugt den Agent, der Client triggert nur den Lauf

class AgentRunRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    call_id: int
    agent_type: AgentTypeEnum
    status: AgentRunStatusEnum
    input_snapshot: dict | None
    raw_output: dict | None
    error_message: str | None
    tokens_used: int | None
    started_at: datetime
    finished_at: datetime | None