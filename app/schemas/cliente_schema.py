from pydantic import BaseModel, EmailStr, Field, model_validator
from typing import Optional
from datetime import datetime
from app.models.cliente_model import TipoCliente

class ClienteBase(BaseModel):
    tipo: TipoCliente
    nombre: str = Field(..., max_length=150)
    apellido: Optional[str] = Field(None, max_length=150)
    razon_social: Optional[str] = Field(None, max_length=255)
    rut: str = Field(..., max_length=20)
    email: Optional[EmailStr] = None
    telefono: Optional[str] = Field(None, max_length=50)
    direccion: Optional[str] = Field(None, max_length=255)
    comuna: Optional[str] = Field(None, max_length=100)
    ciudad: Optional[str] = Field(None, max_length=100)
    observaciones: Optional[str] = None

class ClienteCreate(ClienteBase):
    @model_validator(mode='after')
    def validate_tipo_cliente(self):
        if self.tipo == TipoCliente.PERSONA:
            if not self.nombre or not self.apellido:
                raise ValueError("Para PERSONA, nombre y apellido son obligatorios.")
            self.razon_social = None  # Limpiar si enviaron algo
        elif self.tipo == TipoCliente.EMPRESA:
            if not self.razon_social:
                raise ValueError("Para EMPRESA, razon_social es obligatoria.")
            self.apellido = None # Permitido null, lo forzamos a null
        return self

class ClienteUpdate(BaseModel):
    tipo: Optional[TipoCliente] = None
    nombre: Optional[str] = Field(None, max_length=150)
    apellido: Optional[str] = Field(None, max_length=150)
    razon_social: Optional[str] = Field(None, max_length=255)
    rut: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    telefono: Optional[str] = Field(None, max_length=50)
    direccion: Optional[str] = Field(None, max_length=255)
    comuna: Optional[str] = Field(None, max_length=100)
    ciudad: Optional[str] = Field(None, max_length=100)
    observaciones: Optional[str] = None

    @model_validator(mode='after')
    def validate_tipo_cliente_update(self):
        if self.tipo == TipoCliente.PERSONA:
            self.razon_social = None
        elif self.tipo == TipoCliente.EMPRESA:
            self.apellido = None
        return self

class ClienteResponse(ClienteBase):
    id: int
    estado: bool
    created_by: int
    updated_by: Optional[int] = None
    fecha_creacion: Optional[datetime] = None
    fecha_actualizacion: Optional[datetime] = None

    class Config:
        from_attributes = True