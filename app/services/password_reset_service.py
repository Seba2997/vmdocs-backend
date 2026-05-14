import secrets
import hashlib
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.usuario import Usuario
from app.models.password_reset import PasswordResetToken
from app.services.email_service import send_reset_password_email
from app.utils.security import hash_password
from app.services.usuario_service import validar_password_segura

def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()

def crear_solicitud_recuperacion(db: Session, email: str):
    # 1. Buscar usuario
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    
    # Por seguridad, no revelamos si el usuario existe o no
    if not usuario:
        return {"message": "Si el correo está registrado, recibirás un enlace en breve."}

    # 2. Generar token
    raw_token = secrets.token_urlsafe(32)
    token_hash = hash_token(raw_token)
    
    # 3. Guardar en BD
    nueva_solicitud = PasswordResetToken(
        user_id=usuario.id,
        token_hash=token_hash,
        expires_at=datetime.utcnow() + timedelta(hours=1)
    )
    
    db.add(nueva_solicitud)
    db.commit()
    
    # 4. Enviar email
    send_reset_password_email(usuario.email, raw_token)
    
    return {"message": "Si el correo está registrado, recibirás un enlace en breve."}

def procesar_reseteo_password(db: Session, token: str, new_password: str):
    token_hash = hash_token(token)
    
    # Buscar token válido
    solicitud = db.query(PasswordResetToken).filter(
        PasswordResetToken.token_hash == token_hash,
        PasswordResetToken.is_used == False,
        PasswordResetToken.expires_at > datetime.utcnow()
    ).first()
    
    if not solicitud:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El enlace es inválido o ha expirado."
        )
    
    # Buscar usuario
    usuario = db.query(Usuario).filter(Usuario.id == solicitud.user_id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado."
        )
    
    # Validar fortaleza de la contraseña
    validar_password_segura(new_password)
    
    # Actualizar password
    usuario.password = hash_password(new_password)

    
    # Marcar token como usado
    solicitud.is_used = True
    
    db.commit()
    
    return {"message": "Contraseña actualizada con éxito."}
