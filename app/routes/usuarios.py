from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.usuario import UsuarioCreate, UsuarioResponse, UsuarioUpdate
from app.services.usuario_service import (
    crear_usuario,
    editar_usuario,
    mostrar_todos_usuarios,
    mostrar_usuario,
    cambiar_estado_usuario,
)

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


@router.post("/crearusuario/", response_model=UsuarioResponse)
def crear_usuario_endpoint(
    usuario: UsuarioCreate,
    db: Session = Depends(get_db)
):
    return crear_usuario(db, usuario)

@router.patch("/editarusuario/{usuario_id}", response_model=UsuarioResponse)
def editar_usuario_endpoint(
    usuario_id: int,
    datos: UsuarioUpdate,
    db: Session = Depends(get_db)
):
    return editar_usuario(db, usuario_id, datos)

@router.get("/obtenerusuario/{usuario_id}", response_model=UsuarioResponse)
def obtener_usuario_endpoint(
    usuario_id: int,
    db: Session = Depends(get_db)
):
    return mostrar_usuario(db, usuario_id)


@router.get("/obtenertodos/", response_model=list[UsuarioResponse])
def obtener_todos_usuarios_endpoint(
    db: Session = Depends(get_db)
):
    return mostrar_todos_usuarios(db)


@router.patch("/cambiarestado/{usuario_id}", response_model=UsuarioResponse)
def cambiar_estado_usuario_endpoint(
    usuario_id: int,
    db: Session = Depends(get_db)
):
    return cambiar_estado_usuario(db, usuario_id)