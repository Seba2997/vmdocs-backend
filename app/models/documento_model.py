from sqlalchemy import Column, Integer, String, Boolean, BigInteger, ForeignKey, DateTime, Text, JSON
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

    # Resultados IA (caché)
    # Solo PDFs con texto (no imágenes)
    texto_extraido = Column(Text, nullable=True)   # texto plano extraído del PDF
    resumen_ia     = Column(Text,     nullable=True)   # resumen generado por Gemini
    ficha_ia       = Column(JSON,     nullable=True)   # ficha estructurada (dict)
    ia_generado_en = Column(DateTime(timezone=True), nullable=True)  # última vez generado

    # Relaciones ORM
    caso    = relationship("Caso",    backref="documentos")
    usuario = relationship("Usuario", backref="documentos")
