from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.usuario import Usuario
from app.schemas.caso_schema import CasoCreate, CasoUpdate, CasoFaseUpdate, CasoResponse, CasoUsuarioResponse
from app.schemas.usuario import UsuarioResponse
from app.services import caso_service
from app.utils.jwt_security import requerir_rol, obtener_usuario_actual_activo
from app.services.actividad_service import registrar_actividad
from app.models.actividad_model import AccionActividad

router = APIRouter(prefix="/casos", tags=["Casos"])


# ─────────────────────────────────────────────
# ENDPOINTS CRUD EXISTENTES (ajustados con control de acceso)
# ─────────────────────────────────────────────

@router.post(
    "/crear_caso",
    response_model=CasoResponse,
    operation_id="crear_caso",
    summary="Crear caso",
    description=(
        "Cualquier usuario autenticado puede crear un caso. "
        "El creador queda auto-asignado al caso automáticamente. "
        "ADMIN puede además asignar otros usuarios con el endpoint de asignación."
    ),
    status_code=201,
)
def crear_caso(
    caso: CasoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obtener_usuario_actual_activo),
):
    nuevo_caso = caso_service.crear_caso(db, caso, creador_id=current_user.id)
    registrar_actividad(db, current_user.id, AccionActividad.CREACION, "Caso", nuevo_caso.id, f"Nuevo caso aperturado: {nuevo_caso.titulo}", nuevo_caso.id)
    return nuevo_caso


@router.get(
    "/obtener_todos",
    response_model=List[CasoResponse],
    operation_id="listar_casos",
    summary="Listar casos activos",
    description=(
        "Retorna casos activos con control de acceso por rol: "
        "ADMIN recibe todos; USER recibe solo los casos donde esté asignado."
    ),
)
def listar_casos(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obtener_usuario_actual_activo),
):
    es_admin = current_user.rol == "ADMIN"
    return caso_service.obtener_casos(
        db,
        usuario_id=current_user.id,
        es_admin=es_admin,
    )


@router.get(
    "/obtener_inactivos",
    response_model=List[CasoResponse],
    operation_id="listar_casos_inactivos",
    summary="Listar casos inactivos",
    description="Retorna todos los casos inactivos. Solo ADMIN.",
)
def listar_casos_inactivos(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(requerir_rol("ADMIN")),
):
    return caso_service.obtener_casos_inactivos(db)


@router.get(
    "/obtener_por_cliente/{cliente_id}",
    response_model=List[CasoResponse],
    operation_id="listar_casos_por_cliente",
    summary="Listar casos por cliente",
    description=(
        "Retorna casos activos de un cliente. "
        "ADMIN: ve todos. USER: solo los que tiene asignados."
    ),
)
def listar_casos_por_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obtener_usuario_actual_activo),
):
    casos = caso_service.obtener_casos_por_cliente(db, cliente_id)

    # USER: filtrar solo los casos donde está asignado
    if current_user.rol != "ADMIN":
        casos = [
            c for c in casos
            if caso_service.usuario_tiene_acceso_a_caso(db, current_user.id, c.id)
        ]

    return casos


@router.get(
    "/obtener_caso/{caso_id}",
    response_model=CasoResponse,
    operation_id="obtener_caso_por_id",
    summary="Obtener caso por ID",
    description=(
        "Retorna un caso activo por ID. "
        "ADMIN: acceso total. USER: solo si está asignado al caso."
    ),
)
def obtener_caso(
    caso_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obtener_usuario_actual_activo),
):
    # Verificar acceso si no es ADMIN
    if current_user.rol != "ADMIN":
        caso_service.verificar_acceso_a_caso_o_403(db, current_user.id, caso_id)

    return caso_service.obtener_caso_por_id(db, caso_id)


@router.put(
    "/actualizar_caso/{caso_id}",
    response_model=CasoResponse,
    operation_id="actualizar_caso",
    summary="Actualizar caso",
    description=(
        "Actualiza título y descripción de un caso activo. "
        "ADMIN: acceso total. USER: solo si está asignado al caso. "
        "Para cambiar la fase usar PATCH /fase_caso/{caso_id}."
    ),
)
def actualizar_caso(
    caso_id: int,
    data: CasoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obtener_usuario_actual_activo),
):
    if current_user.rol != "ADMIN":
        caso_service.verificar_acceso_a_caso_o_403(db, current_user.id, caso_id)
    caso_actualizado = caso_service.actualizar_caso(db, caso_id, data)
    registrar_actividad(db, current_user.id, AccionActividad.ACTUALIZACION, "Caso", caso_id, f"Datos del caso actualizados", caso_id)
    return caso_actualizado


@router.patch(
    "/fase_caso/{caso_id}",
    response_model=CasoResponse,
    operation_id="cambiar_fase_caso",
    summary="Cambiar fase del caso",
    description=(
        "Actualiza únicamente la fase (estado) de un caso activo. "
        "ADMIN: acceso total. USER: solo si está asignado al caso."
    ),
)
def cambiar_fase_caso(
    caso_id: int,
    data: CasoFaseUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obtener_usuario_actual_activo),
):
    if current_user.rol != "ADMIN":
        caso_service.verificar_acceso_a_caso_o_403(db, current_user.id, caso_id)
    caso_actualizado = caso_service.cambiar_fase_caso(db, caso_id, data)
    registrar_actividad(db, current_user.id, AccionActividad.ACTUALIZACION, "Caso", caso_id, f"Fase cambiada a: {data.estado}", caso_id)
    return caso_actualizado


@router.patch(
    "/switch_caso/{caso_id}",
    status_code=200,
    operation_id="toggle_estado_caso",
    summary="Activar / Desactivar caso",
    description="Cambia el estado activo del caso de forma alternada (toggle). Solo ADMIN.",
)
def toggle_estado_caso(
    caso_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(requerir_rol("ADMIN")),
):
    return caso_service.toggle_estado_caso(db, caso_id)


# ─────────────────────────────────────────────
# ENDPOINTS DE ASIGNACIÓN (N:M Caso ↔ Usuario)
# ─────────────────────────────────────────────

@router.post(
    "/{caso_id}/usuarios/{usuario_id}",
    response_model=CasoUsuarioResponse,
    operation_id="asignar_usuario_a_caso",
    summary="Asignar usuario a caso",
    description=(
        "Asigna un usuario activo a un caso activo. "
        "Valida existencia, estado activo y unicidad de la asignación. "
        "Solo ADMIN."
    ),
    status_code=201,
)
def asignar_usuario_a_caso(
    caso_id: int,
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(requerir_rol("ADMIN")),
):
    asignacion = caso_service.asignar_usuario_a_caso(db, caso_id, usuario_id)
    registrar_actividad(db, current_user.id, AccionActividad.ASIGNACION, "Caso", caso_id, f"Se asignó un nuevo usuario al equipo", caso_id)
    return asignacion


@router.delete(
    "/{caso_id}/usuarios/{usuario_id}",
    operation_id="desasignar_usuario_de_caso",
    summary="Desasignar usuario de caso",
    description="Elimina la asignación entre un usuario y un caso. Solo ADMIN.",
    status_code=200,
)
def desasignar_usuario_de_caso(
    caso_id: int,
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(requerir_rol("ADMIN")),
):
    return caso_service.desasignar_usuario_de_caso(db, caso_id, usuario_id)


@router.get(
    "/{caso_id}/usuarios",
    response_model=List[UsuarioResponse],
    operation_id="listar_usuarios_de_caso",
    summary="Listar usuarios asignados a un caso",
    description=(
        "Retorna los usuarios activos asignados a un caso activo. "
        "ADMIN: acceso total. USER: solo si está asignado al caso."
    ),
)
def listar_usuarios_de_caso(
    caso_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obtener_usuario_actual_activo),
):
    # USER: verificar que tiene acceso al caso antes de ver sus compañeros
    if current_user.rol != "ADMIN":
        caso_service.verificar_acceso_a_caso_o_403(db, current_user.id, caso_id)

    return caso_service.obtener_usuarios_de_caso(db, caso_id)
