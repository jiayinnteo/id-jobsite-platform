"""User and Company models."""

import enum
import uuid

from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class UserRole(str, enum.Enum):
    """The five roles the platform serves."""

    ID_BOSS = "ID_BOSS"
    ID = "ID"
    CLIENT = "CLIENT"
    CONTRACTOR = "CONTRACTOR"
    WORKER = "WORKER"


class CompanyType(str, enum.Enum):
    ID_FIRM = "ID_FIRM"
    CONTRACTOR = "CONTRACTOR"


class Company(Base):
    __tablename__ = "companies"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    type: Mapped[CompanyType] = mapped_column(
        SAEnum(CompanyType, name="company_type"), nullable=False
    )

    users: Mapped[list["User"]] = relationship(back_populates="company")


class User(Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        SAEnum(UserRole, name="user_role"), nullable=False
    )
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    company_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("companies.id"), nullable=True
    )

    company: Mapped[Company | None] = relationship(back_populates="users")
