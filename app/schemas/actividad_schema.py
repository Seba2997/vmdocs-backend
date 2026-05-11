from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.actividad_model import AccionActividad

class UsuarioInfo(BaseModel):
    id: int
    nombre: str
    apellido: str
    rol: str
    
    class Config:
        from_attributes = True

class ActividadResponse(BaseModel):
    id: int
    usuario_id: Optional[int]
    accion: AccionActividad
    entidad_tipo: str
    entidad_id: int
    caso_id: Optional[int]
    descripcion: str
    detalles: Optional[str]
    fecha: datetime
    
    usuario: Optional[UsuarioInfo] = None

    class Config:
        from_attributes = True

class ActividadListResponse(BaseModel):
    total: int
    actividades: list[ActividadResponse]
