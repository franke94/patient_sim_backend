from datetime import datetime
from sqlalchemy import String, Text, Float, DateTime, func, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING, Optional
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship



if TYPE_CHECKING:
    from app.models.call import Call
    from app.models.assessment import ABCDEAssessment, InjuryAssessment

from app.database import Base

class PlausibilityResult(Base):
    __tablename__ = "plausibility_results"
    id: Mapped[int] = mapped_column(primary_key=True)
    call_id: Mapped[int] = mapped_column(ForeignKey("calls.id"))
    on_scene_score: Mapped[float] = mapped_column(Float)
    candidates: Mapped[list] = mapped_column(JSON, default=list)   # je Kandidat: alle Sub-Scores
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    call: Mapped["Call"] = relationship(back_populates="plausibility_results")