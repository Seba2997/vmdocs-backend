from sqlalchemy.orm import Session
from fastapi import HTTPException
import re

from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate
from app.utils.security import hash_password

def validar_password_segura(password: str):
    """
    Valida que la contraseña cumpla con los requisitos mínimos
    y lanza errores específicos para cada caso.
    """
    if len(password) < 8:
        raise HTTPException(
            status_code=400, 
            detail="La contraseña debe tener al menos 8 caracteres (dígitos)."
        )
    if len(password) > 50:
        raise HTTPException(
            status_code=400, 
            detail="La contraseña no puede tener más de 50 caracteres."
        )
    if not re.search(r'[A-Z]', password):
        raise HTTPException(
            status_code=400, 
            detail="La contraseña debe contener al menos una letra mayúscula."
        )
    if not re.search(r'[0-9]', password):
        raise HTTPException(
            status_code=400, 
            detail="La contraseña debe contener al menos un número (dígito)."
        )
    if not re.search(r'[!@#$%^&*(),.?":{}|<>*\-_+=\[\]\\]', password):
        raise HTTPException(
            status_code=400, 
            detail="La contraseña debe contener al menos un símbolo especial."
        )

def crear_usuario(db: Session, usuario: UsuarioCreate):
    
    usuario_existente = db.query(Usuario).filter(
        Usuario.email == usuario.email
    ).first()

    if usuario_existente:
        raise HTTPException(status_code=400, detail="El correo ya está registrado")
    
    # Validar contraseña antes de crear
    validar_password_segura(usuario.password)
    
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


def cambiar_estado_usuario(db: Session, usuario_id: int, ejecutor_id: int):

    # Regla: No se puede cambiar el estado del Administrador Maestro (ID 1)
    if usuario_id == 1:
        raise HTTPException(
            status_code=403, 
            detail="El Administrador Maestro no puede ser desactivado por razones de seguridad."
        )

    # Regla: Ningún usuario puede cambiar su propio estado (autodesactivación)
    if usuario_id == ejecutor_id:
        raise HTTPException(
            status_code=403, 
            detail="Por seguridad, no puedes cambiar tu propio estado de acceso."
        )

    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    usuario.estado = not usuario.estado
    db.commit()
    db.refresh(usuario)
    return usuario

def cambiar_rol_usuario(db: Session, usuario_id: int, nuevo_rol: str):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    usuario.rol = nuevo_rol
    db.commit()
    db.refresh(usuario)
    return usuario

def cambiar_password(db: Session, usuario_id: int, password: str, ejecutor_id: int):
    # Regla: Solo el propio usuario puede cambiar su contraseña
    if usuario_id != ejecutor_id:
        raise HTTPException(
            status_code=403, 
            detail="No tienes permisos para cambiar la contraseña de otro usuario. Solo puedes cambiar la tuya."
        )

    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Validar formato de la nueva contraseña
    validar_password_segura(password)

    usuario.password = hash_password(password)
    db.commit()
    db.refresh(usuario)
    return usuario

