from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.usuario import Usuario
from app.schemas.cliente_schema import ClienteCreate, ClienteUpdate, ClienteResponse
from app.services import cliente_service
from app.utils.jwt_security import requerir_rol, obtener_usuario_actual_activo

router = APIRouter(prefix="/clientes", tags=["Clientes"])


@router.post(
    "/crear_cliente",
    response_model=ClienteResponse,
    operation_id="crear_cliente",
    summary="Crear cliente",
    description=(
        "Registra un nuevo cliente en el sistema. "
        "Cualquier usuario autenticado puede crear clientes. "
        "El email debe ser único si se proporciona."
    ),
    status_code=201,
)
def crear_cliente(
    cliente: ClienteCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obtener_usuario_actual_activo),
):
    return cliente_service.crear_cliente(db, cliente)


@router.get(
    "/obtener_todos",
    response_model=List[ClienteResponse],
    operation_id="listar_clientes",
    summary="Listar clientes activos",
    description=(
        "Retorna todos los clientes activos. "
        "Cualquier usuario autenticado puede ver el directorio completo de clientes. "
        "Los casos y documentos mantienen su control de acceso por asignación."
    ),
)
def listar_clientes(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obtener_usuario_actual_activo),
):
    return cliente_service.obtener_clientes_admin(db)


@router.get(
    "/obtener_inactivos",
    response_model=List[ClienteResponse],
    operation_id="listar_clientes_inactivos",
    summary="Listar clientes inactivos",
    description="Retorna todos los clientes inactivos. Solo ADMIN.",
)
def listar_clientes_inactivos(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(requerir_rol("ADMIN")),
):
    return cliente_service.obtener_clientes_inactivos(db)


@router.get(
    "/obtener_cliente/{cliente_id}",
    response_model=ClienteResponse,
    operation_id="obtener_cliente_por_id",
    summary="Obtener cliente por ID",
    description=(
        "Retorna un cliente activo por ID. "
        "Cualquier usuario autenticado puede consultar cualquier cliente activo."
    ),
)
def obtener_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obtener_usuario_actual_activo),
):
    return cliente_service.obtener_cliente_por_id(db, cliente_id)


@router.put(
    "/actualizar_cliente/{cliente_id}",
    response_model=ClienteResponse,
    operation_id="actualizar_cliente",
    summary="Actualizar cliente",
    description=(
        "Actualiza los datos de un cliente existente. "
        "Cualquier usuario autenticado puede actualizar información del directorio de clientes."
    ),
)
def actualizar_cliente(
    cliente_id: int,
    data: ClienteUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obtener_usuario_actual_activo),
):
    return cliente_service.actualizar_cliente(db, cliente_id, data)


@router.patch(
    "/switch_cliente/{cliente_id}",
    status_code=200,
    operation_id="toggle_estado_cliente",
    summary="Activar / Desactivar cliente",
    description=(
        "Cambia el estado del cliente de forma alternada (toggle). "
        "Si está activo lo desactiva, y viceversa. Solo ADMIN."
    ),
)
def toggle_estado_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(requerir_rol("ADMIN")),
):
    return cliente_service.toggle_estado_cliente(db, cliente_id)
