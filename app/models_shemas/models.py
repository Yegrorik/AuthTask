from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
from sqlalchemy import text

from enum import Enum

from ..settings.data_base import Base

class UserRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"

class User(Base):
    __tablename__ = "users"

    id : Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    name : Mapped[str]
    surname : Mapped[str]

    email : Mapped[str] = mapped_column(String, unique=True, nullable=False)
    hashed_password : Mapped[str]

    role : Mapped[str] = mapped_column(
        default=UserRole.USER,
        server_default=UserRole.USER,
        nullable=False
    )

    is_active : Mapped[bool] = mapped_column(Boolean, default=True, server_default=text("'true'"))