# app/simulation/agents/abcde_agents.py
from app.models import ABCDEAssessment, AgentRun
from app.models.enums import AgentTypeEnum, CategoryEnum, SeverityEnum, SourceEnum
from app.simulation.agents.base import BaseAgent
from pydantic import BaseModel, Field


class ABCDEAgentOutput(BaseModel):
    findings: list[str]
    severity: SeverityEnum
    rationale: str


_AGENT_SPECS = {
    AgentTypeEnum.A_AGENT: (CategoryEnum.B, "**A** im ABCDE-Schema (Atemwege)."),
    AgentTypeEnum.B_AGENT: (CategoryEnum.B, "**B** im ABCDE-Schema (Atmung)."),
    AgentTypeEnum.C_AGENT: (CategoryEnum.C, "**C** im ABCDE-Schema (Kreislauf)."),
    AgentTypeEnum.D_AGENT: (CategoryEnum.D, "**D** im ABCDE-Schema (neurologischer Status, GCS)."),
    AgentTypeEnum.E_AGENT: (CategoryEnum.E, "**E** im ABCDE-Schema (Exposition, Umgebung, weitere Funde)."),
}


def make_abcde_agent(at: AgentTypeEnum) -> type[BaseAgent]:
    """Generate an ABCDE agent class for a given type."""
    category, focus = _AGENT_SPECS[at]

    class _GeneratedABCDEAgent(BaseAgent[ABCDEAgentOutput]):
        agent_type = at  # noqa: F821 (closure)
        output_schema = ABCDEAgentOutput

        def build_prompt(self) -> str:
            return (
                "Du bist ein medizinischer Auswertungs-Agent in einer Rettungsleitstelle. "
                f"Deine Spezialität: {focus}\n\n"
                "Aufgabe: Lies das Transkript des Notrufgesprächs und extrahiere "
                "ausschließlich Hinweise auf diesen ABCDE-Bereich. "
                "Wenn keine Hinweise vorliegen, gib eine leere `findings`-Liste "
                "und `severity = none` zurück. Halluziniere niemals Befunde.\n\n"
                "Das Feld 'severity' MUSS exakt einer dieser vier Werte sein:'none', 'mild', 'severe', 'critical'."
                'Antworte als JSON: {"findings": [...], "severity": "...", "rationale": "..."}\n'
            )

        def persist(self, output: ABCDEAgentOutput, run: AgentRun) -> None:
            self.db.add(ABCDEAssessment(
                call_id=self.call.id,
                source=SourceEnum.AI_AGENT,
                category=category,
                findings=output.findings,
                severity=output.severity,
                agent_run_id=run.id,
            ))

    _GeneratedABCDEAgent.__name__ = f"{at.value.upper()}Agent"
    return _GeneratedABCDEAgent