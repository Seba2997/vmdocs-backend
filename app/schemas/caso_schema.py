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
    titulo: Optional[str] = None
    descripcion: Optional[str] = None
    estado: Optional[FaseCaso] = None


class CasoResponse(CasoBase):
    id: int
    activo: bool
    fecha_creacion: Optional[datetime] = None
    fecha_actualizacion: Optional[datetime] = None

    class Config:
        from_attributes = True
