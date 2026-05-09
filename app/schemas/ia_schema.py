from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# ─────────────────────────────────────────────
# RESUMEN IA
# ─────────────────────────────────────────────

class ResumenIAResponse(BaseModel):
    """
    Respuesta del endpoint de resumen IA.
    Devuelve el resumen generado por Gemini y la fecha en que fue guardado.
    """
    documento_id: int
    resumen_ia:   str
    generado_en:  Optional[datetime] = None

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────
# FICHA IA
# ─────────────────────────────────────────────

class FichaIAResponse(BaseModel):
    """
    Respuesta del endpoint de ficha IA.
    Estructura normalizada que devuelve Gemini en formato JSON.
    """
    documento_id:        int
    tipo_documento:      Optional[str]       = None
    partes_involucradas: Optional[List[str]] = None
    fechas_importantes:  Optional[List[str]] = None
    montos_detectados:   Optional[List[str]] = None
    resumen_corto:       Optional[str]       = None
    generado_en:         Optional[datetime]  = None

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────
# PREGUNTA AL DOCUMENTO
# ─────────────────────────────────────────────

class PreguntaIARequest(BaseModel):
    """
    Cuerpo de la solicitud para el endpoint de pregunta al documento.
    """
    pregunta: str


class PreguntaIAResponse(BaseModel):
    """
    Respuesta del endpoint de pregunta al documento.
    """
    documento_id: int
    pregunta:     str
    respuesta:    str
