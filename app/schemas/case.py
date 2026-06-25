from datetime import datetime

from pydantic import BaseModel, ConfigDict
from app.models.enums import LanguageEnum, AMLAccuracyEnum

class CaseCreate(BaseModel):
    title: str
    case_description: str
    patient_name: str
    caller_name: str
    caller_prompt: str


class CaseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    language: LanguageEnum
    gold_address_id: int
    aml_lat: float | None
    aml_lon: float | None
    aml_accuracy: AMLAccuracyEnum | None
    patient_name: str
    caller_name: str
    created_at: datetime
