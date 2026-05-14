from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class CasoUsuario(Base):
    """Tabla intermedia N:M entre Caso y Usuario."""
    __tablename__ = "caso_usuario"

    id = Column(Integer, primary_key=True, index=True)
    caso_id = Column(Integer, ForeignKey("casos.id"), index=True, nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), index=True, nullable=False)
    fecha_asignacion = Column(DateTime(timezone=True), server_default=func.now())

    # Un usuario solo puede asignarse una vez al caso
    __table_args__ = (
        UniqueConstraint("caso_id", "usuario_id", name="uq_caso_usuario"),
    )

    # Relaciones ORM hacia los modelos padre
    caso = relationship("Caso", back_populates="asignaciones")
    usuario = relationship("Usuario", back_populates="asignaciones")
