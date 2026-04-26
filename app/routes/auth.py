from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.auth import Token
from app.schemas.usuario import UsuarioResponse
from app.models.usuario import Usuario
from app.services.auth_service import autenticar_usuario
from app.utils.jwt_security import crear_token_de_acceso, obtener_usuario_actual_activo

router = APIRouter(prefix="/auth", tags=["Autenticación"])

@router.post("/login", response_model=Token)
def iniciar_sesion_para_obtener_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db)
):
    """
    Endpoint de login compatible con OAuth2 (Swagger UI).
    Retorna un access_token JWT válido por 1 hora.
    """
    # form_data.username se usa comúnmente para el email en implementaciones OAuth2
    usuario = autenticar_usuario(db, form_data.username, form_data.password)
    
    # Generar el token inyectando el ID del usuario
    access_token = crear_token_de_acceso(data={"sub": str(usuario.id)})
    
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UsuarioResponse)
def leer_mi_usuario(
    current_user: Annotated[Usuario, Depends(obtener_usuario_actual_activo)]
):
    """
    Endpoint protegido de prueba para validar que el token funciona
    correctamente y devuelve al usuario logueado.
    """
    return current_user
