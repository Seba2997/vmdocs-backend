from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.usuario import Usuario
from app.utils.security import verify_password
from app.utils.jwt_security import credentials_exception

def autenticar_usuario(db: Session, email: str, password: str) -> Usuario:
    """
    Verifica las credenciales del usuario y retorna la entidad Usuario si es válido.
    Levanta la credentials_exception si las credenciales fallan.
    Levanta 403 si el usuario existe pero está desactivado.
    """
    # 1. Buscar usuario por email
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if not usuario:
        raise credentials_exception

    # 2. Verificar contraseña
    if not verify_password(password, usuario.password):
        raise credentials_exception

    # 3. Verificar que el usuario esté activo
    if not usuario.estado:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="La cuenta está desactivada. Contacta al administrador.",
        )

    return usuario
