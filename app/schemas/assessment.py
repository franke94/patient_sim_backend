from app.models.enums import SeverityEnum, SourceEnum, CategoryEnum
from datetime import datetime
from pydantic import BaseModel, ConfigDict, model_validator


class Injury(BaseModel):
    """Enthält eine Injury mit severity, als Teil der Injury List"""
    description: str
    severity: SeverityEnum


class ABCDEAssessmentCreate(BaseModel):
    case_id: int | None = None
    call_id: int | None = None
    source: SourceEnum
    category: CategoryEnum
    findings: list[str] = []
    severity: SeverityEnum
    agent_run_id: int | None = None

    # Entweder case_id oder call_id müssen gesetzt sein
    @model_validator(mode="after")
    def _xor_case_call(self) -> "ABCDEAssessmentCreate":
        if (self.case_id is None) == (self.call_id is None):
            raise ValueError("Exactly one of case_id, call_id must be set")
        return self


class ABCDEAssessmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    case_id: int | None
    call_id: int | None
    source: SourceEnum
    category: CategoryEnum
    findings: list[str]
    severity: SeverityEnum
    agent_run_id: int | None
    created_at: datetime


    # Entweder case_id oder call_id müssen gesetzt sein
class InjuryAssessmentCreate(BaseModel):
    case_id: int | None = None
    call_id: int | None = None
    source: SourceEnum
    injuries: list[Injury] = []
    agent_run_id: int | None = None

    @model_validator(mode="after")
    def _xor_case_call(self) -> "InjuryAssessmentCreate":
        if (self.case_id is None) == (self.call_id is None):
            raise ValueError("Exactly one of case_id, call_id must be set")
        return self


class InjuryAssessmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    case_id: int | None
    call_id: int | None
    source: SourceEnum
    injuries: list[Injury]
    agent_run_id: int | None
    created_at: datetime