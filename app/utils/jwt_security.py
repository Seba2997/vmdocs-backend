from datetime import datetime, timedelta, timezone
from typing import Annotated
import jwt

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.auth_config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from app.schemas.auth import TokenData
from app.database import get_db
from app.models.usuario import Usuario
# Importamos la función de verificación de contraseña del archivo original
from app.utils.security import verify_password

# Instancia para que Swagger detecte el login
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Excepción centralizada
credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="No se pudo validar las credenciales",
    headers={"WWW-Authenticate": "Bearer"},
)

def crear_token_de_acceso(data: dict, expires_delta: timedelta | None = None) -> str:
    """Genera un JWT con el payload proveído."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decodificar_token_de_acceso(token: str) -> TokenData:
    """Decodifica y valida el JWT."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
        token_data = TokenData(user_id=int(user_id_str))
        return token_data
    except jwt.InvalidTokenError:
        raise credentials_exception
    except ValueError:
        # En caso de que el 'sub' no se pueda convertir a entero
        raise credentials_exception

def obtener_usuario_actual(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db)
) -> Usuario:
    """Dependencia para obtener al usuario a partir del token."""
    token_data = decodificar_token_de_acceso(token)
    usuario = db.query(Usuario).filter(Usuario.id == token_data.user_id).first()
    if usuario is None:
        raise credentials_exception
    return usuario

def obtener_usuario_actual_activo(
    current_user: Annotated[Usuario, Depends(obtener_usuario_actual)]
) -> Usuario:
    """Dependencia para verificar que el usuario logueado está activo."""
    if not current_user.estado:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="El usuario está inactivo"
        )
    return current_user

def requerir_rol(rol_requerido: str):
    """Factory de dependencias para exigir un rol específico."""
    def verificar_rol_de_usuario(current_user: Annotated[Usuario, Depends(obtener_usuario_actual_activo)]):
        if current_user.rol != rol_requerido:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operación no permitida. Se requiere rol: {rol_requerido}"
            )
        return current_user
    return verificar_rol_de_usuario
