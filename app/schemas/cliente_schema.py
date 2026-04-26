from pydantic import BaseModel, EmailStr
from typing import Optional

class ClienteBase(BaseModel):
    nombre: str
    email: Optional[EmailStr] = None
    telefono: Optional[str] = None

class ClienteCreate(ClienteBase):
    pass

class ClienteUpdate(BaseModel):
    nombre: Optional[str] = None
    email: Optional[EmailStr] = None
    telefono: Optional[str] = None

class ClienteResponse(ClienteBase):
    id: int
    estado: bool

    class Config:
        from_attributes = True