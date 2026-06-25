from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.models.enums import AgentTypeEnum, AgentRunStatusEnum

class PlausibilityResultRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int; call_id: int
    on_scene_score: float
    candidates: list[dict]
    created_at: datetime

class ResolveLocationBody(BaseModel):
    on_scene_human_result: bool | None = None   # Calltaker-Override