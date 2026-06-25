from typing import Literal
from pydantic import BaseModel
from app.models import AgentRun
from app.models.enums import AgentTypeEnum, SourceEnum
from app.models.assessment import OnSceneAssessment
from app.simulation.agents.base import BaseAgent


class OnSceneAgentOutput(BaseModel):
    findings: list[str]
    onscene_status: Literal["yes", "no", "unknown"]
    confidence: float | None = None


class OnSceneAgent(BaseAgent[OnSceneAgentOutput]):
    agent_type = AgentTypeEnum.ON_SCENE_AGENT
    output_schema = OnSceneAgentOutput

    def build_prompt(self) -> str:
        return (
            "Bestimme, ob der Anrufer physisch am Einsatzort ist.\n"
            "'yes': 'ich bin bei', 'ich sehe', aktive Hilfe. "
            "'no': beschreibt Gefundenes aus der Ferne, anderer Ort. "
            "Unklar → 'unknown'.\n"
            'JSON: {"findings": ["zitat", ...], "onscene_status": "yes|no|unknown", "confidence": 0.0-1.0}'
        )

    def persist(self, output: OnSceneAgentOutput, run: AgentRun) -> None:
        self.db.add(OnSceneAssessment(
            call_id=run.call_id, agent_run_id=run.id, source=SourceEnum.AI_AGENT,
            findings=output.findings, onscene_status=output.onscene_status,
            confidence=output.confidence,
        ))