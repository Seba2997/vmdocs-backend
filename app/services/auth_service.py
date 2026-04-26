from sqlalchemy.orm import Session
from app.models.usuario import Usuario
from app.utils.security import verify_password
from app.utils.jwt_security import credentials_exception

def autenticar_usuario(db: Session, email: str, password: str) -> Usuario:
    """
    Verifica las credenciales del usuario y retorna la entidad Usuario si es válido.
    Levanta la credentials_exception si las credenciales fallan.
    """
    # 1. Buscar usuario por email
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if not usuario:
        raise credentials_exception

    # 2. Verificar contraseña
    if not verify_password(password, usuario.password):
        raise credentials_exception

    return usuario
