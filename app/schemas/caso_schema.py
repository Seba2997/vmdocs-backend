from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.caso_model import FaseCaso


class CasoBase(BaseModel):
    titulo: str
    descripcion: Optional[str] = None
    estado: FaseCaso = FaseCaso.abierto
    cliente_id: int


class CasoCreate(CasoBase):
    pass


class CasoUpdate(BaseModel):
    """Campos editables por un usuario asignado o ADMIN. No incluye cambio de fase."""
    titulo: Optional[str] = None
    descripcion: Optional[str] = None


class CasoFaseUpdate(BaseModel):
    """Schema exclusivo para avanzar/retroceder la fase de un caso."""
    estado: FaseCaso


class CasoResponse(CasoBase):
    id: int
    activo: bool
    fecha_creacion: Optional[datetime] = None
    fecha_actualizacion: Optional[datetime] = None

    class Config:
        from_attributes = True


class CasoUsuarioResponse(BaseModel):
    
    id: int
    caso_id: int
    usuario_id: int
    fecha_asignacion: Optional[datetime] = None

    class Config:
        from_attributes = True
