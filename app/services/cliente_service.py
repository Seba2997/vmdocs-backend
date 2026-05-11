from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.cliente_model import Cliente
from app.schemas.cliente_schema import ClienteCreate, ClienteUpdate
from app.services import notificacion_service
from app.models.notificacion_model import TipoNotificacion


# ─────────────────────────────────────────────
# CONTROL DE ACCESO
# ─────────────────────────────────────────────
# Opción C: los clientes son un directorio compartido. Cualquier usuario
# autenticado puede ver y editar cualquier cliente activo. La confidencialidad
# real se mantiene a nivel de caso y documentos (RBAC estricto allí).

def usuario_tiene_acceso_a_cliente(db: Session, usuario_id: int, cliente_id: int) -> bool:
    """Todo usuario autenticado tiene acceso al directorio de clientes."""
    return True


def verificar_acceso_a_cliente_o_403(db: Session, usuario_id: int, cliente_id: int) -> None:
    """Sin restricción: cualquier usuario autenticado accede al directorio de clientes."""
    pass


# ─────────────────────────────────────────────
# CRUD
# ─────────────────────────────────────────────

def crear_cliente(db: Session, cliente: ClienteCreate) -> Cliente:
    # Validar email único (si viene)
    if cliente.email:
        existente = db.query(Cliente).filter(Cliente.email == cliente.email).first()
        if existente:
            raise HTTPException(status_code=400, detail="El email ya está registrado")

    nuevo_cliente = Cliente(**cliente.model_dump())
    db.add(nuevo_cliente)
    db.commit()
    db.refresh(nuevo_cliente)
    
    # Notificar a administradores
    notificacion_service.notificar_a_administradores(
        db, 
        TipoNotificacion.CLIENTE, 
        nuevo_cliente.id, 
        f"Se ha registrado un nuevo cliente: {nuevo_cliente.nombre}"
    )
    
    return nuevo_cliente


def obtener_clientes_admin(db: Session) -> list[Cliente]:
    """Retorna todos los clientes activos. Solo para ADMIN."""
    return db.query(Cliente).filter(Cliente.estado == True).all()


def obtener_clientes_por_usuario(db: Session, usuario_id: int) -> list[Cliente]:
    """Retorna todos los clientes activos. Opción C: directorio compartido."""
    return db.query(Cliente).filter(Cliente.estado == True).all()


def obtener_clientes_inactivos(db: Session) -> list[Cliente]:
    """Retorna todos los clientes inactivos. Solo para ADMIN."""
    return db.query(Cliente).filter(Cliente.estado == False).all()


def obtener_cliente_por_id(db: Session, cliente_id: int) -> Cliente:
    cliente = db.query(Cliente).filter(
        Cliente.id == cliente_id,
        Cliente.estado == True,
    ).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente


def actualizar_cliente(db: Session, cliente_id: int, data: ClienteUpdate) -> Cliente:
    cliente = db.query(Cliente).filter(
        Cliente.id == cliente_id,
        Cliente.estado == True,
    ).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    # Validar email único si cambia
    if data.email and data.email != cliente.email:
        existente = db.query(Cliente).filter(Cliente.email == data.email).first()
        if existente:
            raise HTTPException(status_code=400, detail="El email ya está registrado")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(cliente, key, value)

    db.commit()
    db.refresh(cliente)
    return cliente


def toggle_estado_cliente(db: Session, cliente_id: int) -> dict:
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    cliente.estado = not cliente.estado
    db.commit()
    db.refresh(cliente)

    estado_texto = "activado" if cliente.estado else "desactivado"
    return {"mensaje": f"Cliente {estado_texto}", "estado": cliente.estado}