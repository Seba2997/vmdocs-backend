from sqlalchemy.orm import Session
from app.models.caso_model import Caso
from app.schemas.caso_schema import CasoCreate, CasoUpdate
from fastapi import HTTPException


def crear_caso(db: Session, caso: CasoCreate):
    nuevo_caso = Caso(**caso.model_dump())
    db.add(nuevo_caso)
    db.commit()
    db.refresh(nuevo_caso)
    return nuevo_caso


def obtener_casos(db: Session):
    return db.query(Caso).filter(Caso.activo == True).all()


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


def actualizar_caso(db: Session, caso_id: int, data: CasoUpdate):
    caso = db.query(Caso).filter(Caso.id == caso_id, Caso.activo == True).first()
    if not caso:
        raise HTTPException(status_code=404, detail="Caso no encontrado")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(caso, key, value)

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
