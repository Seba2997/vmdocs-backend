from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class NotaCasoBase(BaseModel):
    contenido: str

class NotaCasoCreate(NotaCasoBase):
    pass

class NotaCasoUpdate(NotaCasoBase):
    pass

class UsuarioNotaResponse(BaseModel):
    id: int
    nombre: str
    apellido: Optional[str] = None
    rol: str

    model_config = ConfigDict(from_attributes=True)

class NotaCasoResponse(NotaCasoBase):
    id: int
    caso_id: int
    usuario_id: int
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime] = None
    usuario: Optional[UsuarioNotaResponse] = None

    model_config = ConfigDict(from_attributes=True)
