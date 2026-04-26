from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base




class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), nullable=False)
    email = Column(String(255), unique=True, nullable=True)
    telefono = Column(String(50), nullable=True)
    estado = Column(Boolean, default=True) 


