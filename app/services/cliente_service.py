from sqlalchemy.orm import Session
from app.models.cliente_model import Cliente
from app.schemas.cliente_schema import ClienteCreate, ClienteUpdate
from fastapi import HTTPException

def crear_cliente(db: Session, cliente: ClienteCreate):
    # validar email único (si viene)
    if cliente.email:
        existente = db.query(Cliente).filter(Cliente.email == cliente.email).first()
        if existente:
            raise HTTPException(status_code=400, detail="El email ya está registrado")

    nuevo_cliente = Cliente(**cliente.model_dump())
    db.add(nuevo_cliente)
    db.commit()
    db.refresh(nuevo_cliente)
    return nuevo_cliente


def obtener_clientes(db: Session):
    return db.query(Cliente).filter(Cliente.estado == True).all()


def obtener_cliente_por_id(db: Session, cliente_id: int):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id, Cliente.estado == True).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente


def actualizar_cliente(db: Session, cliente_id: int, data: ClienteUpdate):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id, Cliente.estado == True).first()

    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    # validar email único si cambia
    if data.email and data.email != cliente.email:
        existente = db.query(Cliente).filter(Cliente.email == data.email).first()
        if existente:
            raise HTTPException(status_code=400, detail="El email ya está registrado")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(cliente, key, value)

    db.commit()
    db.refresh(cliente)
    return cliente


def toggle_estado_cliente(db: Session, cliente_id: int):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()

    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    cliente.estado = not cliente.estado
    db.commit()
    db.refresh(cliente)

    estado_texto = "activado" if cliente.estado else "desactivado"
    return {"mensaje": f"Cliente {estado_texto}", "estado": cliente.estado}