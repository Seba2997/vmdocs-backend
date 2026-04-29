from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class CasoUsuario(Base):
    """
    Tabla intermedia explícita para la relación N:M entre Caso y Usuario.
    Un caso puede tener múltiples usuarios asignados,
    y un usuario puede estar asignado a múltiples casos.
    """
    __tablename__ = "caso_usuario"

    id = Column(Integer, primary_key=True, index=True)
    caso_id = Column(Integer, ForeignKey("casos.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    fecha_asignacion = Column(DateTime(timezone=True), server_default=func.now())

    # Restricción única: un usuario no puede estar asignado dos veces al mismo caso
    __table_args__ = (
        UniqueConstraint("caso_id", "usuario_id", name="uq_caso_usuario"),
    )

    # Relaciones ORM hacia los modelos padre
    caso = relationship("Caso", back_populates="asignaciones")
    usuario = relationship("Usuario", back_populates="asignaciones")
