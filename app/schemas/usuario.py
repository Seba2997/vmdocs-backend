from pydantic import BaseModel


# Clase create usuario para crear usuario 
class UsuarioCreate(BaseModel):
    nombre: str
    apellido: str
    email: str
    password: str
    rol: str = "USER"
    estado: bool = True

# Clase update usuario para cambios parciales
class UsuarioUpdate(BaseModel):
    nombre: str | None = None
    apellido: str | None = None
    email: str | None = None
    rol: str | None = None
    estado: bool | None = None

class UsuarioPasswordUpdate(BaseModel):
    password: str

# Clase respuesta para mostrar usuario 
class UsuarioResponse(BaseModel):
    id: int
    nombre: str
    apellido: str
    email: str
    rol: str
    estado: bool

    # Para que Pydantic trabaje con SQLAlchemy
    class Config:
        from_attributes = True