from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.caso_schema import CasoCreate, CasoUpdate, CasoResponse
from app.services import caso_service
from typing import List

router = APIRouter(prefix="/casos", tags=["Casos"])


@router.post(
    "/crear_caso",
    response_model=CasoResponse,
    operation_id="crear_caso",
    summary="Crear caso",
    description="Registra un nuevo caso asociado a un cliente existente.",
)
def crear_caso(caso: CasoCreate, db: Session = Depends(get_db)):
    return caso_service.crear_caso(db, caso)


@router.get(
    "/obtener_todos",
    response_model=List[CasoResponse],
    operation_id="listar_casos",
    summary="Listar casos activos",
    description="Retorna todos los casos con estado activo registrados en el sistema.",
)
def listar_casos(db: Session = Depends(get_db)):
    return caso_service.obtener_casos(db)


@router.get(
    "/obtener_inactivos",
    response_model=List[CasoResponse],
    operation_id="listar_casos_inactivos",
    summary="Listar casos inactivos",
    description="Retorna todos los casos con estado inactivo (desactivados) registrados en el sistema.",
)
def listar_casos_inactivos(db: Session = Depends(get_db)):
    return caso_service.obtener_casos_inactivos(db)


@router.get(
    "/obtener_por_cliente/{cliente_id}",
    response_model=List[CasoResponse],
    operation_id="listar_casos_por_cliente",
    summary="Listar casos por cliente",
    description="Retorna todos los casos activos asociados a un cliente específico.",
)
def listar_casos_por_cliente(cliente_id: int, db: Session = Depends(get_db)):
    return caso_service.obtener_casos_por_cliente(db, cliente_id)


@router.get(
    "/obtener_caso/{caso_id}",
    response_model=CasoResponse,
    operation_id="obtener_caso_por_id",
    summary="Obtener caso por ID",
    description="Retorna los datos de un caso activo específico. Lanza 404 si no existe o está inactivo.",
)
def obtener_caso(caso_id: int, db: Session = Depends(get_db)):
    return caso_service.obtener_caso_por_id(db, caso_id)


@router.put(
    "/actualizar_caso/{caso_id}",
    response_model=CasoResponse,
    operation_id="actualizar_caso",
    summary="Actualizar caso",
    description="Actualiza los datos de un caso existente. Solo se modifican los campos enviados en el body.",
)
def actualizar_caso(caso_id: int, data: CasoUpdate, db: Session = Depends(get_db)):
    return caso_service.actualizar_caso(db, caso_id, data)


@router.patch(
    "/switch_caso/{caso_id}",
    status_code=200,
    operation_id="toggle_estado_caso",
    summary="Activar / Desactivar caso",
    description="Cambia el estado activo del caso de forma alternada (toggle).",
)
def toggle_estado_caso(caso_id: int, db: Session = Depends(get_db)):
    return caso_service.toggle_estado_caso(db, caso_id)
