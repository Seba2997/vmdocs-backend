from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.cliente_schema import ClienteCreate, ClienteUpdate, ClienteResponse
from app.services import cliente_service
from typing import List

router = APIRouter(prefix="/clientes", tags=["Clientes"])

@router.post(
    "/crear_cliente",
    response_model=ClienteResponse,
    operation_id="crear_cliente",
    summary="Crear cliente",
    description="Registra un nuevo cliente en el sistema. El email debe ser único si se proporciona.",
)
def crear_cliente(cliente: ClienteCreate, db: Session = Depends(get_db)):
    return cliente_service.crear_cliente(db, cliente)


@router.get(
    "/obtener_todos",
    response_model=List[ClienteResponse],
    operation_id="listar_clientes",
    summary="Listar clientes activos",
    description="Retorna todos los clientes con estado activo registrados en el sistema.",
)
def listar_clientes(db: Session = Depends(get_db)):
    return cliente_service.obtener_clientes(db)


@router.get(
    "/obtener_cliente/{cliente_id}",
    response_model=ClienteResponse,
    operation_id="obtener_cliente_por_id",
    summary="Obtener cliente por ID",
    description="Retorna los datos de un cliente activo específico. Lanza 404 si no existe o está inactivo.",
)
def obtener_cliente(cliente_id: int, db: Session = Depends(get_db)):
    return cliente_service.obtener_cliente_por_id(db, cliente_id)


@router.put(
    "/actualizar_cliente/{cliente_id}",
    response_model=ClienteResponse,
    operation_id="actualizar_cliente",
    summary="Actualizar cliente",
    description="Actualiza los datos de un cliente existente. Solo se modifican los campos enviados en el body.",
)
def actualizar_cliente(cliente_id: int, data: ClienteUpdate, db: Session = Depends(get_db)):
    return cliente_service.actualizar_cliente(db, cliente_id, data)


@router.patch(
    "/switch_cliente/{cliente_id}",
    status_code=200,
    operation_id="toggle_estado_cliente",
    summary="Activar / Desactivar cliente",
    description="Cambia el estado del cliente de forma alternada (toggle). Si está activo lo desactiva, y viceversa.",
)
def toggle_estado_cliente(cliente_id: int, db: Session = Depends(get_db)):
    return cliente_service.toggle_estado_cliente(db, cliente_id)