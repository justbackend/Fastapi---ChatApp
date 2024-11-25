from __future__ import annotations

from sqlalchemy import Column, String, Integer, Enum, Boolean, Date, UniqueConstraint, BigInteger, and_, ForeignKey, \
    select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship, backref, Mapped
from sqlalchemy.testing.schema import mapped_column

from app.base import Base
from app.exceptions import NotFoundException
from app.user.schemas import UserRole




class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    phone_number: Mapped[str] = mapped_column(String(9), nullable=False, unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(64))
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    role: Mapped[str] = mapped_column(String(15), nullable=False, index=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    @classmethod
    async def get(cls, db_session: AsyncSession, model_id: int):
        """

        :param db_session:
        :param model_id:
        :return:
        """
        stmt = select(cls).where(cls.id == model_id)
        result = await db_session.execute(stmt)
        instance = result.scalars().first()
        if instance is None:
            raise NotFoundException("Kiritilganlar bo'yicha malumot mavjud emas")
        return instance

    def __str__(self):
        return self.phone_number



