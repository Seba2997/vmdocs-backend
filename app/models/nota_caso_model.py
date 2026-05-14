from sqlalchemy import Column, Integer, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class NotaCaso(Base):
    __tablename__ = "notas_caso"

    id = Column(Integer, primary_key=True, index=True)
    contenido = Column(Text, nullable=False)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())

    # FKs
    caso_id = Column(Integer, ForeignKey("casos.id"), index=True, nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), index=True, nullable=False)

    # Relaciones
    caso = relationship("Caso") # Opcional: back_populates en Caso si quieres acceder desde el objeto caso
    usuario = relationship("Usuario")
