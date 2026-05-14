from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.caso_model import Caso
from app.models.usuario import Usuario
from app.models.caso_usuario_model import CasoUsuario
from app.schemas.caso_schema import CasoCreate, CasoUpdate, CasoFaseUpdate
from app.services import notificacion_service
from app.models.notificacion_model import TipoNotificacion




def crear_caso(db: Session, caso: CasoCreate, creador_id: int) -> Caso:
    """Crea un nuevo caso y auto-asigna al usuario creador."""
    try:
        nuevo_caso = Caso(**caso.model_dump(), created_by=creador_id)
        db.add(nuevo_caso)
        db.flush()  # Obtiene el ID generado sin hacer commit todavía

        # Auto-asignar al creador dentro de la misma transacción
        asignacion = CasoUsuario(caso_id=nuevo_caso.id, usuario_id=creador_id)
        db.add(asignacion)

        db.commit()
        db.refresh(nuevo_caso)
        
        # Notificar a administradores sobre el nuevo caso
        notificacion_service.notificar_a_administradores(
            db,
            TipoNotificacion.CASO,
            nuevo_caso.id,
            f"Nuevo caso creado: {nuevo_caso.titulo}"
        )
        
        return nuevo_caso
    except Exception:
        db.rollback()
        raise


def obtener_casos_inactivos(db: Session):
    return db.query(Caso).filter(Caso.activo == False).all()


def obtener_casos_por_cliente(db: Session, cliente_id: int):
    return db.query(Caso).filter(
        Caso.cliente_id == cliente_id,
        Caso.activo == True
    ).all()


def obtener_caso_por_id(db: Session, caso_id: int):
    caso = db.query(Caso).filter(Caso.id == caso_id, Caso.activo == True).first()
    if not caso:
        raise HTTPException(status_code=404, detail="Caso no encontrado")
    return caso


def actualizar_caso(db: Session, caso_id: int, data: CasoUpdate, usuario_id: int):
    caso = db.query(Caso).filter(Caso.id == caso_id, Caso.activo == True).first()
    if not caso:
        raise HTTPException(status_code=404, detail="Caso no encontrado")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(caso, key, value)
        
    caso.updated_by = usuario_id

    db.commit()
    db.refresh(caso)
    return caso


def toggle_estado_caso(db: Session, caso_id: int):
    caso = db.query(Caso).filter(Caso.id == caso_id).first()
    if not caso:
        raise HTTPException(status_code=404, detail="Caso no encontrado")

    caso.activo = not caso.activo
    db.commit()
    db.refresh(caso)

    estado_texto = "activado" if caso.activo else "desactivado"
    return {"mensaje": f"Caso {estado_texto}", "activo": caso.activo}


def cambiar_fase_caso(db: Session, caso_id: int, data: CasoFaseUpdate) -> Caso:
    """Cambia la fase de un caso activo."""
    caso = db.query(Caso).filter(Caso.id == caso_id, Caso.activo == True).first()
    if not caso:
        raise HTTPException(status_code=404, detail="Caso no encontrado o inactivo")

    caso.estado = data.estado
    db.commit()
    db.refresh(caso)
    return caso




def _obtener_caso_activo_o_404(db: Session, caso_id: int) -> Caso:
    """Retorna el caso si existe y está activo, lanza 404 en caso contrario."""
    caso = db.query(Caso).filter(Caso.id == caso_id, Caso.activo == True).first()
    if not caso:
        raise HTTPException(status_code=404, detail="Caso no encontrado o inactivo")
    return caso


def _obtener_usuario_activo_o_404(db: Session, usuario_id: int) -> Usuario:
    """Retorna el usuario si existe y está activo, lanza 404 en caso contrario."""
    usuario = db.query(Usuario).filter(
        Usuario.id == usuario_id,
        Usuario.estado == True
    ).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado o inactivo")
    return usuario


def _obtener_asignacion(db: Session, caso_id: int, usuario_id: int) -> CasoUsuario | None:
    """Busca una asignación existente entre caso y usuario. Retorna None si no existe."""
    return db.query(CasoUsuario).filter(
        CasoUsuario.caso_id == caso_id,
        CasoUsuario.usuario_id == usuario_id
    ).first()



def usuario_tiene_acceso_a_caso(db: Session, usuario_id: int, caso_id: int) -> bool:
    
    asignacion = _obtener_asignacion(db, caso_id, usuario_id)
    return asignacion is not None


def verificar_acceso_a_caso_o_403(db: Session, usuario_id: int, caso_id: int) -> None:
    """
    Versión que lanza 403 si el usuario no tiene acceso al caso.
    Usar en endpoints donde se requiere acceso garantizado.
    """
    if not usuario_tiene_acceso_a_caso(db, usuario_id, caso_id):
        raise HTTPException(
            status_code=403,
            detail="No tienes permiso para acceder a este caso"
        )



def asignar_usuario_a_caso(db: Session, caso_id: int, usuario_id: int) -> CasoUsuario:
    """Asigna un usuario a un caso validando existencia y duplicidad."""
    # 1. Validar que el caso existe y está activo
    _obtener_caso_activo_o_404(db, caso_id)

    # 2. Validar que el usuario existe y está activo
    _obtener_usuario_activo_o_404(db, usuario_id)

    # 3. Validar que la asignación no existe ya (evitar duplicado)
    asignacion_existente = _obtener_asignacion(db, caso_id, usuario_id)
    if asignacion_existente:
        raise HTTPException(
            status_code=409,
            detail="El usuario ya está asignado a este caso"
        )

    # 4. Crear la asignación
    nueva_asignacion = CasoUsuario(caso_id=caso_id, usuario_id=usuario_id)
    db.add(nueva_asignacion)
    db.commit()
    db.refresh(nueva_asignacion)
    
    # Notificar al usuario asignado
    notificacion_service.crear_notificacion(
        db,
        usuario_id,
        TipoNotificacion.CASO,
        caso_id,
        f"Se te ha asignado un nuevo caso: {nueva_asignacion.caso.titulo}"
    )
    
    return nueva_asignacion


def desasignar_usuario_de_caso(db: Session, caso_id: int, usuario_id: int) -> dict:
    """Elimina la asignación entre un usuario y un caso."""
    # 1. Validar que el caso existe (sin filtrar por activo para poder limpiar)
    caso = db.query(Caso).filter(Caso.id == caso_id).first()
    if not caso:
        raise HTTPException(status_code=404, detail="Caso no encontrado")

    # 2. Validar que el usuario existe
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # 3. Buscar la asignación
    asignacion = _obtener_asignacion(db, caso_id, usuario_id)
    if not asignacion:
        raise HTTPException(
            status_code=404,
            detail="El usuario no está asignado a este caso"
        )

    # 4. Eliminar
    db.delete(asignacion)
    db.commit()
    return {"mensaje": f"Usuario {usuario_id} desasignado del caso {caso_id}"}


def obtener_usuarios_de_caso(db: Session, caso_id: int) -> list[Usuario]:
    """
    Retorna la lista de usuarios activos asignados a un caso activo.
    """
    # 1. Validar que el caso existe y está activo
    _obtener_caso_activo_o_404(db, caso_id)

    # 2. JOIN entre CasoUsuario y Usuario filtrando usuarios activos
    usuarios = (
        db.query(Usuario)
        .join(CasoUsuario, CasoUsuario.usuario_id == Usuario.id)
        .filter(
            CasoUsuario.caso_id == caso_id,
            Usuario.estado == True
        )
        .all()
    )
    return usuarios


def obtener_casos_de_usuario(db: Session, usuario_id: int) -> list[Caso]:
    """
    Retorna la lista de casos activos a los que está asignado un usuario activo.
    """
    # 1. Validar que el usuario existe y está activo
    _obtener_usuario_activo_o_404(db, usuario_id)

    # 2. JOIN entre CasoUsuario y Caso filtrando casos activos
    casos = (
        db.query(Caso)
        .join(CasoUsuario, CasoUsuario.caso_id == Caso.id)
        .filter(
            CasoUsuario.usuario_id == usuario_id,
            Caso.activo == True
        )
        .all()
    )
    return casos


# ─────────────────────────────────────────────
# LISTADOS CON CONTROL DE ACCESO POR ROL
# ─────────────────────────────────────────────

def obtener_casos(db: Session, usuario_id: int | None = None, es_admin: bool = False) -> list[Caso]:
    """Retorna casos activos filtrados por rol y asignaciones."""
    query = db.query(Caso).filter(Caso.activo == True)

    if es_admin:
        return query.all()

    # USER: filtrar por asignación mediante JOIN
    if usuario_id is None:
        raise HTTPException(
            status_code=400,
            detail="Se requiere usuario_id para filtrar casos por usuario"
        )

    casos = (
        query
        .join(CasoUsuario, CasoUsuario.caso_id == Caso.id)
        .filter(CasoUsuario.usuario_id == usuario_id)
        .all()
    )
    return casos
