from sqlalchemy.orm import Session
from sqlalchemy import or_
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

def crear_cliente(db: Session, cliente: ClienteCreate, creador_id: int) -> Cliente:
    # Validar si existe por RUT o Email
    condiciones = [Cliente.rut == cliente.rut]
    if cliente.email:
        condiciones.append(Cliente.email == cliente.email)

    existente = db.query(Cliente).filter(or_(*condiciones)).first()

    if existente:
        if existente.estado:
            # Está activo, no podemos duplicarlo
            conflict_field = "RUT" if existente.rut == cliente.rut else "email"
            raise HTTPException(status_code=400, detail=f"Ya existe un cliente activo con este {conflict_field}")
        else:
            # Está inactivo (papelera). REACTIVACIÓN MÁGICA.
            for key, value in cliente.model_dump().items():
                setattr(existente, key, value)
            existente.estado = True
            existente.updated_by = creador_id
            
            db.commit()
            db.refresh(existente)
            
            notificacion_service.notificar_a_administradores(
                db, 
                TipoNotificacion.CLIENTE, 
                existente.id, 
                f"Se ha reactivado y actualizado un cliente desde la papelera: {existente.nombre}"
            )
            return existente

    nuevo_cliente = Cliente(**cliente.model_dump(), created_by=creador_id)
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


def actualizar_cliente(db: Session, cliente_id: int, data: ClienteUpdate, usuario_id: int) -> Cliente:
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
        
    cliente.updated_by = usuario_id

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