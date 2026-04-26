from pydantic import BaseModel, EmailStr, Field
from enum import Enum

class RolUsuario(str, Enum):
    ADMIN = "ADMIN"
    USER = "USER"

# Clase create usuario para crear usuario 
class UsuarioCreate(BaseModel):
    nombre: str
    apellido: str
    email: EmailStr
    password: str = Field(min_length=8, max_length=50)
    rol: RolUsuario = RolUsuario.USER
    estado: bool = True

# Clase update usuario para cambios parciales
class UsuarioUpdate(BaseModel):
    nombre: str | None = None
    apellido: str | None = None
    email: EmailStr | None = None

class UsuarioPasswordUpdate(BaseModel):
    password: str = Field(min_length=8, max_length=50)

class UsuarioRolUpdate(BaseModel):
    rol: RolUsuario

# Clase respuesta para mostrar usuario 
class UsuarioResponse(BaseModel):
    id: int
    nombre: str
    apellido: str
    email: EmailStr
    rol: RolUsuario
    estado: bool

    # Para que Pydantic trabaje con SQLAlchemy
    class Config:
        from_attributes = True