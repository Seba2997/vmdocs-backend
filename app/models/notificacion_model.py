from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.database import Base

class TipoNotificacion(str, enum.Enum):
    CLIENTE = "CLIENTE"
    CASO = "CASO"

class Notificacion(Base):
    __tablename__ = "notificaciones"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), index=True, nullable=False)
    tipo = Column(SQLEnum(TipoNotificacion), nullable=False)
    referencia_id = Column(Integer, nullable=False)
    mensaje = Column(String(500), nullable=False)
    leida = Column(Boolean, default=False)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())

    usuario = relationship("Usuario", backref="notificaciones")
