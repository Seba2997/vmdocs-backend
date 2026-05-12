from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional
from app.models.notificacion_model import TipoNotificacion

class NotificacionBase(BaseModel):
    mensaje: str
    tipo: TipoNotificacion
    referencia_id: int

class NotificacionCreate(NotificacionBase):
    usuario_id: int

class NotificacionResponse(NotificacionBase):
    id: int
    usuario_id: int
    leida: bool
    fecha_creacion: datetime

    model_config = ConfigDict(from_attributes=True)

class NotificacionListResponse(BaseModel):
    total: int
    notificaciones: List[NotificacionResponse]
