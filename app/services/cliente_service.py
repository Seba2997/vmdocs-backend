from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.cliente_model import Cliente
from app.models.caso_model import Caso
from app.models.caso_usuario_model import CasoUsuario
from app.schemas.cliente_schema import ClienteCreate, ClienteUpdate


# ─────────────────────────────────────────────
# CONTROL DE ACCESO
# ─────────────────────────────────────────────

def usuario_tiene_acceso_a_cliente(db: Session, usuario_id: int, cliente_id: int) -> bool:
    """
    Verifica si un usuario tiene acceso a un cliente específico.
    El acceso se concede si el usuario está asignado a al menos un caso
    activo de ese cliente (dos saltos: cliente → caso → caso_usuario).
    """
    resultado = (
        db.query(CasoUsuario)
        .join(Caso, Caso.id == CasoUsuario.caso_id)
        .filter(
            Caso.cliente_id == cliente_id,
            Caso.activo == True,
            CasoUsuario.usuario_id == usuario_id,
        )
        .first()
    )
    return resultado is not None


def verificar_acceso_a_cliente_o_403(db: Session, usuario_id: int, cliente_id: int) -> None:
    """
    Lanza 403 si el usuario no tiene ningún caso asignado para el cliente indicado.
    """
    if not usuario_tiene_acceso_a_cliente(db, usuario_id, cliente_id):
        raise HTTPException(
            status_code=403,
            detail="No tienes permiso para acceder a este cliente",
        )


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
    return nuevo_cliente


def obtener_clientes_admin(db: Session) -> list[Cliente]:
    """Retorna todos los clientes activos. Solo para ADMIN."""
    return db.query(Cliente).filter(Cliente.estado == True).all()


def obtener_clientes_por_usuario(db: Session, usuario_id: int) -> list[Cliente]:
    """
    Retorna los clientes activos que tienen al menos un caso activo
    donde el usuario está asignado.
    Usa JOIN de dos saltos: Cliente → Caso → CasoUsuario.
    """
    clientes = (
        db.query(Cliente)
        .join(Caso, Caso.cliente_id == Cliente.id)
        .join(CasoUsuario, CasoUsuario.caso_id == Caso.id)
        .filter(
            Cliente.estado == True,
            Caso.activo == True,
            CasoUsuario.usuario_id == usuario_id,
        )
        .distinct()  # evitar duplicados si hay múltiples casos por cliente
        .all()
    )
    return clientes


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