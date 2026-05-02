from abc import ABC, abstractmethod
from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, ValidationError
from sqlalchemy.orm import Session

from app.models import AgentRun, Call
from app.models.enums import AgentRunStatusEnum, AgentTypeEnum
from app.simulation.llm import LLMError, LLMMessage, get_llm_client

OutputT = TypeVar("OutputT", bound=BaseModel)  #Jeder Agent kann ein eigenes strukturiertes Output-Fomrat definieren, über pydantic wird validiert




class BaseAgent(ABC, Generic[OutputT]):
    """Base Skelett für LLM-driven bachground agent

    3 wesentliche Punkte:
    - agent_type:   AgentTypeEnum
    - output_schema: pydantic class describing the expected JSON
    - built_prompt: System Propmpt for the specific agent
    - persist:  What to do with parsed output

    Base Agent handles: AgentRun lifecycle, LLM call, JSON parsing, error capture
    """

    agent_type: AgentTypeEnum
    output_schema: type[BaseModel]

    def __init__(self, call: Call, db: Session) -> None:
        self.call = call
        self.db = db

    @abstractmethod
    def build_prompt(self) -> str:
        """Return the system prompt that defines the agent's task."""

    @abstractmethod
    def persist(self, output: OutputT, run: AgentRun) -> None:
        """Persist the parsed output (create assessments, etc.). May be a no-op."""

    def _to_llm_messages(self) -> list[LLMMessage]:
        ordered = sorted(self.call.messages, key = lambda m: m.order_index)
        return [LLMMessage(role=m.role.value, content=m.content) for m in ordered]

    def run(self) -> AgentRun:
        """Execute the agent and return the persisted AgentRun row"""
        run = AgentRun(
            call_id = self.call.id,
            agent_type = self.agent_type,
            status=AgentRunStatusEnum.RUNNING,
            input_snapshot={"message_count": len(self.call.messages)},
            started_at=datetime.utcnow()
        ) #Agent Zeile wird angelgt, Status ist damit Running
        self.db.add(run)
        self.db.flush() #makes run.id availiable

        try:
            client = get_llm_client()
            result = client.chat(   #Hier wird das LLM aufgerufen
                system_prompt=self.build_prompt(), #Was tun wenn es kein Build_prompt gibt? Sollte es geben!
                messages=self._to_llm_messages(),
                json_mode=True,
                max_tokens=5000,
            )
            output = self.output_schema.model_validate_json(result.text)  #JSON validieren
            run.raw_output = output.model_dump()  #Roh Output sichern
            run.tokens_used = result.tokens_used
            self.persist(output, run) #Domänenspezifisch speichern
            run.status = AgentRunStatusEnum.SUCCESS

        except (LLMError, ValidationError) as exc:
            run.status = AgentRunStatusEnum.FAILED
            run.error_message = f"{type(exc).__name__}: {exc}"

        finally:
            run.finished_at = datetime.utcnow()

        return run