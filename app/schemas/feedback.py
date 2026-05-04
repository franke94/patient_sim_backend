from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import QualificationEnum


class CallFeedbackCreate(BaseModel):
    realism_score: int | None = Field(default=None, ge=1, le=5)
    ai_assessment_score: int | None = Field(default=None, ge=1, le=5)
    ai_collaboration_score: int | None = Field(default=None, ge=1, le=5)
    qualification: QualificationEnum | None = None
    works_in_dispatch: bool | None = None
    feedback_text: str | None = Field(default=None, max_length=2000)


class CallFeedbackRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    call_id: int
    realism_score: int | None
    ai_assessment_score: int | None
    ai_collaboration_score: int | None
    qualification: QualificationEnum | None
    works_in_dispatch: bool | None
    feedback_text: str | None
    created_at: datetime