from pydantic import BaseModel,Field

from app.models import AgentRun
from app.models.enums import AgentTypeEnum
from app.simulation.agents.base import BaseAgent, OutputT


class LocationAgentOutput(BaseModel):
    address: str | None = Field(default=None, description="Vollständige Adresse") #ToDo: Nach Straße und Stadt filtern
    patient_name: str | None = Field(default=None)
    caller_name: str | None = Field(default=None)


class LocationAgent(BaseAgent[LocationAgentOutput]):
    agent_type = AgentTypeEnum.LOCATION_AGENT
    output_schema = LocationAgentOutput

    def build_prompt(self) -> str:
        return (
            "Du bist ein Auswertungs-Agent in einer Rettungsleitstelle. "
            "Deine Spezialität: Adressen und Personennamen aus dem Notruf extrahieren.\n\n"
            "Aufgabe: Lies das Transkript und extrahiere "
            "(a) die Einsatzadresse, (b) den Patientennamen, (c) den Anrufernamen. "
            "Wenn eine Information nicht erwähnt wurde, setze das entsprechende Feld auf null. "
            "Erfinde nichts.\n\n"
            "Antworte mit folgendem JSON-Schema:\n"
            "{\n"
            '  "address": string | null,\n'
            '  "patient_name": string | null,\n'
            '  "caller_name": string | null\n'
            "}"
        )

    def persist(self, output: OutputT, run: AgentRun) -> None:
        # Bewusst leer, der Output liegt komplett in run.raw_output
        return None