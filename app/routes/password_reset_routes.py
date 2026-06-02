from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.password_reset_schemas import (
    ForgotPasswordRequest,
    ResetPasswordRequest,
    PasswordResetResponse,
    TokenInfoResponse,
)
from app.services.password_reset_service import (
    crear_solicitud_recuperacion,
    obtener_info_token,
    procesar_reseteo_password,
)

router = APIRouter(prefix="/auth", tags=["Recuperación de Contraseña"])


@router.post("/forgot-password", response_model=PasswordResetResponse)
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """Solicita un enlace de recuperación de contraseña por correo."""
    return crear_solicitud_recuperacion(db, request.email)


@router.get("/token-info/{token}", response_model=TokenInfoResponse)
def token_info(token: str, db: Session = Depends(get_db)):
    """
    Consulta el estado de un token de recuperación.
    Siempre responde 200 con el campo `status`:
      - valid   → el token es válido y puede usarse
      - expired → expiró (5 minutos)
      - used    → ya fue utilizado
      - invalid → no existe
    """
    return obtener_info_token(db, token)


@router.post("/reset-password", response_model=PasswordResetResponse)
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    """Restablece la contraseña usando un token válido."""
    if request.new_password != request.confirm_password:
        raise HTTPException(status_code=400, detail="Las contraseñas no coinciden.")
    return procesar_reseteo_password(db, request.token, request.new_password)
