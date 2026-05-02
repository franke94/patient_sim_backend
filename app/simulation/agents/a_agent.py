from app.models import ABCDEAssessment, AgentRun
from app.models.enums import AgentTypeEnum, CategoryEnum, SeverityEnum, SourceEnum
from app.simulation.agents.base import BaseAgent
from pydantic import BaseModel, Field

class AAgentOutput(BaseModel):
    """LLMs return shape"""
    findings: list[str] = Field(
        description="Kurze Stichpunkte zu Atemwegs-Beobachtungen",
    )
    severity: SeverityEnum = Field(
        description="Einschätzung der Schwere"
    )
    rationale: str = Field(
        description="Eine kurze Begründung der Schwere-Einschätzung"
    )


class AAgent(BaseAgent[AAgentOutput]):
    agent_type = AgentTypeEnum.A_AGENT
    output_schema = AAgentOutput

    def build_prompt(self) -> str:
        return (
            "Du bist ein medizinischer Auswertungs-Agent in einer Rettungsleitstelle. "
            "Deine Spezialität: das **A** im ABCDE-Schema (Atemwege).\n\n"
            "Aufgabe: Lies das Transkript des Notrufgesprächs unten und extrahiere "
            "ausschließlich Hinweise auf den Zustand der Atemwege des Patienten. "
            "Wenn keine Hinweise vorliegen, gib eine leere `findings`-Liste und "
            "`severity = none` zurück. Halluziniere niemals Befunde.\n\n"
            "Antworte mit folgendem JSON-Schema:\n"
            "{\n"
            '  "findings": [string, ...],\n'
            '  "severity": "none" | "mild" | "severe" | "critical",\n'
            '  "rationale": string\n'
            "}"
        )

    def persist(self, output: AAgentOutput, run: AgentRun) -> None:
        assessment = ABCDEAssessment(
            call_id=self.call.id,
            source=SourceEnum.AI_AGENT,
            category=CategoryEnum.A,
            findings=output.findings,
            severity=output.severity,
            agent_run_id=run.id,
        )
        self.db.add(assessment)