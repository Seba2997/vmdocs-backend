from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.database import Base

class AccionActividad(str, enum.Enum):
    CREACION = "CREACION"
    ACTUALIZACION = "ACTUALIZACION"
    ELIMINACION = "ELIMINACION"
    ASIGNACION = "ASIGNACION"
    SUBIDA = "SUBIDA"
    ANALISIS_IA = "ANALISIS_IA"

class EntidadActividad(str, enum.Enum):
    CLIENTE = "CLIENTE"
    CASO = "CASO"
    DOCUMENTO = "DOCUMENTO"
    USUARIO = "USUARIO"

class Actividad(Base):
    __tablename__ = "actividades"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True)
    accion = Column(SQLEnum(AccionActividad), nullable=False)
    entidad_tipo = Column(SQLEnum(EntidadActividad), nullable=False)
    entidad_id = Column(Integer, nullable=False)
    caso_id = Column(Integer, ForeignKey("casos.id", ondelete="CASCADE"), index=True, nullable=True)
    descripcion = Column(String, nullable=False)
    detalles = Column(Text, nullable=True)
    fecha = Column(DateTime(timezone=True), server_default=func.now())

    usuario = relationship("Usuario", backref="actividades")
    caso = relationship("Caso")
