from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.nota_caso_model import NotaCaso
from app.models.caso_model import Caso
from app.schemas.nota_caso_schema import NotaCasoCreate, NotaCasoUpdate

def listar_notas_por_caso(db: Session, caso_id: int):
    # Verificar que el caso exista
    caso = db.query(Caso).filter(Caso.id == caso_id).first()
    if not caso:
        raise HTTPException(status_code=404, detail="Caso no encontrado")
        
    return db.query(NotaCaso).filter(NotaCaso.caso_id == caso_id).order_by(NotaCaso.fecha_creacion.desc()).all()

def crear_nota(db: Session, caso_id: int, usuario_id: int, nota: NotaCasoCreate):
    caso = db.query(Caso).filter(Caso.id == caso_id).first()
    if not caso:
        raise HTTPException(status_code=404, detail="Caso no encontrado")

    nueva_nota = NotaCaso(
        caso_id=caso_id,
        usuario_id=usuario_id,
        contenido=nota.contenido
    )
    db.add(nueva_nota)
    db.commit()
    db.refresh(nueva_nota)
    return nueva_nota

def actualizar_nota(db: Session, nota_id: int, usuario_id: int, es_admin: bool, nota: NotaCasoUpdate):
    db_nota = db.query(NotaCaso).filter(NotaCaso.id == nota_id).first()
    if not db_nota:
        raise HTTPException(status_code=404, detail="Nota no encontrada")
        
    if db_nota.usuario_id != usuario_id and not es_admin:
        raise HTTPException(status_code=403, detail="No tienes permiso para editar esta nota")

    db_nota.contenido = nota.contenido
    db.commit()
    db.refresh(db_nota)
    return db_nota

def eliminar_nota(db: Session, nota_id: int, usuario_id: int, es_admin: bool):
    db_nota = db.query(NotaCaso).filter(NotaCaso.id == nota_id).first()
    if not db_nota:
        raise HTTPException(status_code=404, detail="Nota no encontrada")
        
    if db_nota.usuario_id != usuario_id and not es_admin:
        raise HTTPException(status_code=403, detail="No tienes permiso para eliminar esta nota")

    db.delete(db_nota)
    db.commit()
    return {"mensaje": "Nota eliminada"}
