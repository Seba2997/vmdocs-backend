from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.password_reset_schemas import ForgotPasswordRequest, ResetPasswordRequest, PasswordResetResponse
from app.services.password_reset_service import crear_solicitud_recuperacion, procesar_reseteo_password

router = APIRouter(prefix="/auth", tags=["Recuperación de Contraseña"])

@router.post("/forgot-password", response_model=PasswordResetResponse)
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    return crear_solicitud_recuperacion(db, request.email)

@router.post("/reset-password", response_model=PasswordResetResponse)
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    if request.new_password != request.confirm_password:
        raise HTTPException(status_code=400, detail="Las contraseñas no coinciden.")
    
    return procesar_reseteo_password(db, request.token, request.new_password)
