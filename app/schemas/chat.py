from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.models.enums import MessageRoleEnum


class ChatMessageCreate(BaseModel):
    """POST /calls/{id}/messages -> Deshlab muss keine call_id mitgegeben werden"""
    content: str
    transcription: bool = False   # Caller-Antwort mit simulierten Transkriptionsfehlern


class ChatMessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    call_id: int
    role: MessageRoleEnum
    content: str
    order_index: int
    created_at: datetime