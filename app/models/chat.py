from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Text, DateTime, ForeignKey, Enum as SQLEnum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import MessageRoleEnum

if TYPE_CHECKING:
    from app.models.call import Call


class ChatMessage(Base):
    """Einzige Nachricht an oder von einem LLM"""
    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    call_id: Mapped[int] = mapped_column(ForeignKey("calls.id"))

    role: Mapped[MessageRoleEnum] = mapped_column(SQLEnum(MessageRoleEnum))
    content: Mapped[str] = mapped_column(Text)
    order_index: Mapped[int] = mapped_column()

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

    call: Mapped["Call"] = relationship(back_populates="messages")