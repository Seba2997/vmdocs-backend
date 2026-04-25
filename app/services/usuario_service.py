from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate
from app.utils.security import hash_password

def crear_usuario(db: Session, usuario: UsuarioCreate):
    
    usuario_existente = db.query(Usuario).filter(
        Usuario.email == usuario.email
    ).first()

    if usuario_existente:
        raise HTTPException(status_code=400, detail="El correo ya está registrado")
    
    nuevo_usuario = Usuario(
        nombre=usuario.nombre,
        apellido=usuario.apellido,
        email=usuario.email,
        password=hash_password(usuario.password),
        rol=usuario.rol,
        estado=usuario.estado
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario

def mostrar_usuario(db: Session, usuario_id: int):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    return usuario  

def mostrar_todos_usuarios(db: Session):
    return db.query(Usuario).all()


def editar_usuario(db: Session, usuario_id: int, datos: UsuarioUpdate):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    update_data = datos.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(usuario, key, value)

    db.commit()
    db.refresh(usuario)
    return usuario


def cambiar_estado_usuario(db: Session, usuario_id: int):

    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    usuario.estado = not usuario.estado
    db.commit()
    db.refresh(usuario)
    return usuario

def cambiar_password(db: Session, usuario_id: int, password: str):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    usuario.password = hash_password(password)
    db.commit()
    db.refresh(usuario)
    return usuario

