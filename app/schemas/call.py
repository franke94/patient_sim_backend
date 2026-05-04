from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.models.enums import CallStatusEnum, LanguageEnum
from app.schemas.chat import ChatMessageRead
from app.schemas.assessment import ABCDEAssessmentRead, InjuryAssessmentRead
from app.schemas.agent import AgentRunRead

class CallCreate(BaseModel):
    case_id: int
    #Status ist am anfang immer running, wird automatisch gesetzt


class CallPatchEntries(BaseModel):
    address_entered: str | None = None
    patient_name_entered: str | None = None
    caller_name_entered: str | None = None


class CallRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    case_id: int
    status: CallStatusEnum
    language: LanguageEnum
    started_at: datetime
    finished_at: datetime | None
    address_entered: str | None
    patient_name_entered: str | None
    caller_name_entered: str | None


class CallDetailRead(CallRead): #Vererbung von der Klasse CallRead, ermögtlicht eine Detailierte Ansicht
    """Detailierte Übersicht über den Call: GET /calls/{id}. """
    messages: list[ChatMessageRead] = []
    abcde_assessments: list[ABCDEAssessmentRead] = []
    injury_assessments: list[InjuryAssessmentRead] = []
    agent_runs: list[AgentRunRead] = []


#Hinzugefügt, damit man auch vergangene Calls im Frontend öffnen kann
class CallSummaryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    case_id: int
    case_title: str
    language: LanguageEnum
    status: CallStatusEnum
    started_at: datetime
    finished_at: datetime | None