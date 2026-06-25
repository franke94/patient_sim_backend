from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, DateTime, ForeignKey, Enum as SQLEnum, JSON, func, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import CategoryEnum, SeverityEnum, SourceEnum

if TYPE_CHECKING:
    from app.models.case import Case
    from app.models.call import Call
    from app.models.agent import AgentRun


class ABCDEAssessment(Base):
    """ABCDE Kategorie, bezieht sich immer entweder auf einen Call oder einen Case"""
    __tablename__ = "abcde_assessments"

    id: Mapped[int] = mapped_column(primary_key=True)
    case_id: Mapped[int | None] = mapped_column(ForeignKey("cases.id"))
    call_id: Mapped[int | None] = mapped_column(ForeignKey("calls.id"))
    agent_run_id: Mapped[int | None] = mapped_column(ForeignKey("agent_runs.id"))

    source: Mapped[SourceEnum] = mapped_column(SQLEnum(SourceEnum))
    category: Mapped[CategoryEnum] = mapped_column(SQLEnum(CategoryEnum))
    findings: Mapped[list[str]] = mapped_column(JSON, default=list)
    severity: Mapped[SeverityEnum] = mapped_column(SQLEnum(SeverityEnum))

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

    case: Mapped["Case | None"] = relationship(back_populates="abcde_assessments")
    call: Mapped["Call | None"] = relationship(back_populates="abcde_assessments")
    agent_run: Mapped["AgentRun | None"] = relationship(back_populates="abcde_assessments")


class InjuryAssessment(Base):
    """Injury assessment einer bestimmten Quelle (truth, calltaker, AI agent), läuft als Liste"""
    __tablename__ = "injury_assessment"

    id: Mapped[int] = mapped_column(primary_key=True)
    case_id: Mapped[int | None] = mapped_column(ForeignKey("cases.id"))
    call_id: Mapped[int | None] = mapped_column(ForeignKey("calls.id"))
    agent_run_id: Mapped[int | None] = mapped_column(ForeignKey("agent_runs.id"))

    source: Mapped[SourceEnum] = mapped_column(SQLEnum(SourceEnum))
    injuries: Mapped[list[dict]] = mapped_column(JSON, default=list)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

    case: Mapped["Case | None"] = relationship(back_populates="injury_assessments")
    call: Mapped["Call | None"] = relationship(back_populates="injury_assessments")
    agent_run: Mapped["AgentRun | None"] = relationship(back_populates="injury_assessments")

class AddressAssessment(Base):
    __tablename__ = "address_assessments"
    id: Mapped[int] = mapped_column(primary_key=True)
    call_id: Mapped[int] = mapped_column(ForeignKey("calls.id"))
    agent_run_id: Mapped[Optional[int]] = mapped_column(ForeignKey("agent_runs.id"), nullable=True)
    source: Mapped[SourceEnum] = mapped_column(SQLEnum(SourceEnum), default=SourceEnum.AI_AGENT)
    address_candidates: Mapped[list] = mapped_column(JSON, default=list)   # roher LLM-Output
    matched_addresses: Mapped[list] = mapped_column(JSON, default=list)    # nach DB-Match + Distanz
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    call: Mapped["Call"] = relationship(back_populates="address_assessments")
    agent_run: Mapped[Optional["AgentRun"]] = relationship()


class OnSceneAssessment(Base):
    __tablename__ = "onscene_assessments"
    id: Mapped[int] = mapped_column(primary_key=True)
    call_id: Mapped[int] = mapped_column(ForeignKey("calls.id"))
    agent_run_id: Mapped[Optional[int]] = mapped_column(ForeignKey("agent_runs.id"), nullable=True)
    source: Mapped[SourceEnum] = mapped_column(SQLEnum(SourceEnum), default=SourceEnum.AI_AGENT)
    findings: Mapped[list] = mapped_column(JSON, default=list)   # zitierte Belege
    onscene_status: Mapped[str] = mapped_column(String(20))      # yes | no | unknown
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    call: Mapped["Call"] = relationship(back_populates="onscene_assessments")
    agent_run: Mapped[Optional["AgentRun"]] = relationship()