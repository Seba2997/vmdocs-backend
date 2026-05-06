import enum

from sqlalchemy import Column, Integer, String, Boolean, Enum
from sqlalchemy.orm import relationship
from app.database import Base


class RolUsuario(str, enum.Enum):
    ADMIN = "ADMIN"
    USER  = "USER"


class Usuario(Base):
    __tablename__ = "usuarios"

    id       = Column(Integer, primary_key=True, index=True)
    nombre   = Column(String, nullable=False)
    apellido = Column(String, nullable=False)
    email    = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    rol      = Column(Enum(RolUsuario), default=RolUsuario.USER, nullable=False)
    estado   = Column(Boolean, default=True)

    # Relación ORM → tabla intermedia CasoUsuario (N:M explícito)
    asignaciones = relationship("CasoUsuario", back_populates="usuario", cascade="all, delete-orphan")
