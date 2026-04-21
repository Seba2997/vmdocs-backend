from pydantic import BaseModel

class UsuarioCreate(BaseModel):
    nombre: str
    email: str
    password: str
    rol: str = "USER"
    estado: bool = True


class UsuarioUpdate(BaseModel):
    nombre: str | None = None
    email: str | None = None
    password: str | None = None
    rol: str | None = None
    estado: bool | None = None

class UsuarioResponse(BaseModel):
    id: int
    nombre: str
    email: str
    rol: str
    estado: bool

    class Config:
        from_attributes = True