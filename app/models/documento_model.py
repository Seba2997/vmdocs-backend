from sqlalchemy import Column, Integer, String, Boolean, BigInteger, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Documento(Base):
    __tablename__ = "documentos"

    id                = Column(Integer, primary_key=True, index=True)
    nombre_original   = Column(String(255), nullable=False)
    nombre_storage    = Column(String(255), nullable=False, unique=True)  # UUID + extensión
    tipo_mime         = Column(String(100), nullable=False)
    tamano            = Column(BigInteger, nullable=False)               # bytes
    fecha_subida      = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())
    activo            = Column(Boolean, default=True)                    # soft-delete

    # FK → Caso  (ON DELETE RESTRICT por defecto en SQLAlchemy sin cascade en DB)
    caso_id    = Column(Integer, ForeignKey("casos.id", ondelete="RESTRICT"), nullable=False)

    # FK → Usuario (quién subió el documento)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False)

    # Relaciones ORM
    caso    = relationship("Caso",    backref="documentos")
    usuario = relationship("Usuario", backref="documentos")
