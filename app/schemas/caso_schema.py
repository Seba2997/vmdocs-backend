from pydantic import BaseModel, Field, model_validator
from typing import Optional
from datetime import datetime, date
from app.models.caso_model import FaseCaso


class CasoBase(BaseModel):
    titulo: str
    descripcion: Optional[str] = None
    estado: FaseCaso = FaseCaso.abierto
    cliente_id: int
    numero_rol: Optional[str] = Field(None, max_length=100)
    tribunal: Optional[str] = Field(None, max_length=255)
    materia: Optional[str] = Field(None, max_length=150)
    prioridad: str = Field('MEDIA', pattern='^(ALTA|MEDIA|BAJA)$')
    fecha_inicio: Optional[date] = None
    fecha_cierre: Optional[date] = None


class CasoCreate(CasoBase):
    @model_validator(mode='after')
    def validate_fechas(self):
        if self.fecha_inicio and self.fecha_cierre:
            if self.fecha_cierre < self.fecha_inicio:
                raise ValueError("La fecha de cierre no puede ser menor a la fecha de inicio.")
        return self


class CasoUpdate(BaseModel):
    """Campos editables por un usuario asignado o ADMIN. No incluye cambio de fase."""
    titulo: Optional[str] = None
    descripcion: Optional[str] = None
    numero_rol: Optional[str] = Field(None, max_length=100)
    tribunal: Optional[str] = Field(None, max_length=255)
    materia: Optional[str] = Field(None, max_length=150)
    prioridad: Optional[str] = Field(None, pattern='^(ALTA|MEDIA|BAJA)$')
    fecha_inicio: Optional[date] = None
    fecha_cierre: Optional[date] = None
    
    @model_validator(mode='after')
    def validate_fechas_update(self):
        if self.fecha_inicio and self.fecha_cierre:
            if self.fecha_cierre < self.fecha_inicio:
                raise ValueError("La fecha de cierre no puede ser menor a la fecha de inicio.")
        return self


class CasoFaseUpdate(BaseModel):
    """Schema exclusivo para avanzar/retroceder la fase de un caso."""
    estado: FaseCaso


class CasoResponse(CasoBase):
    id: int
    activo: bool
    created_by: int
    updated_by: Optional[int] = None
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

