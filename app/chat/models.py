from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Integer, ForeignKey, Text, String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.base import Base

if TYPE_CHECKING:
    from app.user.models import User


class Messages(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    message: Mapped[str] = mapped_column(String(4096), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)

    user: Mapped["User"] = relationship("User")


