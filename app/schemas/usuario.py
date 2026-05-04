from pydantic import BaseModel, EmailStr, Field
from enum import Enum

from app.models.usuario import RolUsuario  # fuente única de verdad

# Clase create usuario para crear usuario 
class UsuarioCreate(BaseModel):
    nombre: str
    apellido: str
    email: EmailStr
    password: str
    rol: RolUsuario = RolUsuario.USER
    estado: bool = True

# Clase update usuario para cambios parciales
class UsuarioUpdate(BaseModel):
    nombre: str | None = None
    apellido: str | None = None
    email: EmailStr | None = None

class UsuarioPasswordUpdate(BaseModel):
    password: str

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