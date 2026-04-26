import enum
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class FaseCaso(str, enum.Enum):
    abierto      = "Abierto"
    discusion    = "Discusion"
    conciliacion = "Conciliacion"
    prueba       = "Prueba"
    impugnacion  = "Impugnacion"
    cerrado      = "Cerrado"


class Caso(Base):
    __tablename__ = "casos"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(200), nullable=False)
    descripcion = Column(String(1000), nullable=True)
    estado = Column(Enum(FaseCaso), default=FaseCaso.abierto, nullable=False)
    activo = Column(Boolean, default=True)           # soft-delete
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())

    # FK → Cliente
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)

    # Relación ORM
    cliente = relationship("Cliente", back_populates="casos")
