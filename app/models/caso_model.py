import enum
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Enum, Text, Date
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
    descripcion = Column(Text, nullable=True)
    
    numero_rol = Column(String(100), nullable=True)
    tribunal = Column(String(255), nullable=True)
    materia = Column(String(150), nullable=True)
    prioridad = Column(String(20), default='MEDIA', nullable=False)
    fecha_inicio = Column(Date, nullable=True)
    fecha_cierre = Column(Date, nullable=True)
    
    estado = Column(Enum(FaseCaso), default=FaseCaso.abierto, nullable=False)
    activo = Column(Boolean, default=True)           # soft-delete
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())

    # FK → Cliente
    cliente_id = Column(Integer, ForeignKey("clientes.id"), index=True, nullable=False)
    
    created_by = Column(Integer, ForeignKey("usuarios.id"), index=True, nullable=False)
    updated_by = Column(Integer, ForeignKey("usuarios.id"), nullable=True)

    # Relación ORM → Cliente
    cliente = relationship("Cliente", back_populates="casos")

    # Relación ORM → tabla intermedia CasoUsuario (N:M explícito)
    asignaciones = relationship("CasoUsuario", back_populates="caso", cascade="all, delete-orphan")
