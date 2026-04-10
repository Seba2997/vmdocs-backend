from pydantic import BaseModel

class UsuarioCreate(BaseModel):
    nombre: str
    email: str
    password: str
    rol: str = "USER"

class UsuarioResponse(BaseModel):
    id: int
    nombre: str
    email: str
    rol: str

    class Config:
        from_attributes = True