from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.usuario import Usuario
from app.schemas.actividad_schema import ActividadListResponse
from app.services import actividad_service
from app.routes.auth import obtener_usuario_actual_activo

router = APIRouter(prefix="/actividades", tags=["Actividades"])

@router.get("/", response_model=ActividadListResponse)
def listar_actividades(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obtener_usuario_actual_activo)
):
    es_admin = current_user.rol == "ADMIN"
    total, actividades = actividad_service.obtener_actividades(db, current_user.id, es_admin, skip, limit)
    return {"total": total, "actividades": actividades}
