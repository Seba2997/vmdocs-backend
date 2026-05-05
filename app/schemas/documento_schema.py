from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DocumentoResponse(BaseModel):
    """
    Schema de respuesta base para un documento.
    Devuelve la metadata almacenada en PostgreSQL, sin URL.
    """
    id:               int
    nombre_original:  str
    tipo_mime:        str
    tamano:           int
    fecha_subida:     Optional[datetime] = None
    activo:           bool
    caso_id:          int
    usuario_id:       int

    class Config:
        from_attributes = True


class DocumentoDetalleResponse(DocumentoResponse):
    """
    Schema extendido que incluye el nombre físico en storage y
    la fecha de última actualización. Útil para endpoints de administración.
    """
    nombre_storage:       str
    fecha_actualizacion:  Optional[datetime] = None

    class Config:
        from_attributes = True


class DocumentoDescargaResponse(BaseModel):
    """
    Schema para el endpoint de descarga.
    Devuelve únicamente la signed URL temporal de Supabase.
    """
    signed_url: str
    expira_en:  int  # segundos hasta expiración
