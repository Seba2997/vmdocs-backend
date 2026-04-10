from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.usuario import UsuarioCreate, UsuarioResponse
from app.services.usuario_service import crear_usuario

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


@router.post("/", response_model=UsuarioResponse)
def crear_usuario_endpoint(
    usuario: UsuarioCreate,
    db: Session = Depends(get_db)
):
    return crear_usuario(db, usuario)