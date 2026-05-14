import enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class TipoCliente(str, enum.Enum):
    PERSONA = "PERSONA"
    EMPRESA = "EMPRESA"


class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(Enum(TipoCliente), nullable=False)
    nombre = Column(String(150), nullable=False)
    apellido = Column(String(150), nullable=True)
    razon_social = Column(String(255), nullable=True)
    rut = Column(String(20), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, nullable=True)
    telefono = Column(String(50), nullable=True)
    direccion = Column(String(255), nullable=True)
    comuna = Column(String(100), nullable=True)
    ciudad = Column(String(100), nullable=True)
    observaciones = Column(Text, nullable=True)
    estado = Column(Boolean, default=True)
    
    created_by = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    updated_by = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())

    # Relación ORM
    casos = relationship("Caso", back_populates="cliente")
