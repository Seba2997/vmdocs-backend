from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.usuario import Usuario
from app.schemas.notificacion_schema import NotificacionListResponse, NotificacionResponse
from app.services import notificacion_service
from app.utils.jwt_security import obtener_usuario_actual_activo

router = APIRouter(prefix="/notificaciones", tags=["Notificaciones"])

@router.get("/", response_model=NotificacionListResponse)
def listar_notificaciones(
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obtener_usuario_actual_activo)
):
    total, notificaciones = notificacion_service.obtener_notificaciones(db, current_user.id, limit)
    return {"total": total, "notificaciones": notificaciones}

@router.patch("/{notificacion_id}/leer", response_model=NotificacionResponse)
def leer_notificacion(
    notificacion_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obtener_usuario_actual_activo)
):
    return notificacion_service.marcar_como_leida(db, notificacion_id, current_user.id)

@router.patch("/leer_todas")
def leer_todas_notificaciones(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obtener_usuario_actual_activo)
):
    return notificacion_service.marcar_todas_como_leidas(db, current_user.id)
