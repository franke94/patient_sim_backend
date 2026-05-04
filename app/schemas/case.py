from datetime import datetime

from pydantic import BaseModel, ConfigDict
from app.models.enums import LanguageEnum

class CaseCreate(BaseModel):
    title: str
    case_description: str
    address: str
    gps_lat: float
    gps_lng: float
    patient_name: str
    caller_name: str
    caller_prompt: str


class CaseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True) #Pydantic liest hiermit direkt die Attribute des SQLAlchemy-Objektes, muss kein dict sein

    id: int
    title: str
    language: LanguageEnum
    address: str
    gps_lat: float
    gps_lng: float
    patient_name: str
    caller_name: str
    created_at: datetime
