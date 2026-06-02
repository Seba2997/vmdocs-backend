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

# ──────────────────────────────────────────
# Utilidades internas
# ──────────────────────────────────────────

def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def _invalidar_tokens_activos(db: Session, user_id: int) -> None:
    """Invalida todos los tokens pendientes (no usados) del usuario."""
    db.query(PasswordResetToken).filter(
        PasswordResetToken.user_id == user_id,
        PasswordResetToken.is_used == False,
    ).update({"is_used": True})


# ──────────────────────────────────────────
# Operaciones principales
# ──────────────────────────────────────────

def crear_solicitud_recuperacion(db: Session, email: str) -> dict:
    """
    Genera un token de recuperación de contraseña e invalida tokens 
    anteriores del mismo usuario.
    Por seguridad, siempre responde el mismo mensaje genérico.
    """
    usuario = db.query(Usuario).filter(Usuario.email == email).first()

    # No revelamos si el correo existe o no
    if not usuario:
        return {"message": "Si el correo está registrado, recibirás un enlace en breve."}

    # Invalidar tokens anteriores pendientes
    _invalidar_tokens_activos(db, usuario.id)

    # Generar token y hash
    raw_token = secrets.token_urlsafe(32)
    token_hash = hash_token(raw_token)

    # Guardar token (expira en 5 minutos)
    nuevo_token = PasswordResetToken(
        user_id=usuario.id,
        token_hash=token_hash,
        expires_at=datetime.utcnow() + timedelta(minutes=5),
    )
    db.add(nuevo_token)
    db.commit()

    # Enviar email
    send_reset_password_email(usuario.email, raw_token)

    return {"message": "Si el correo está registrado, recibirás un enlace en breve."}


def obtener_info_token(db: Session, token: str) -> dict:
    """
    Consulta el estado de un token sin lanzar excepciones.
    Retorna siempre un dict con: status, email, nombre.

    Usado por el frontend antes de mostrar el formulario de reseteo.
    """
    token_hash = hash_token(token)
    solicitud = db.query(PasswordResetToken).filter(
        PasswordResetToken.token_hash == token_hash
    ).first()

    if not solicitud:
        return {"status": "invalid", "email": None, "nombre": None}

    # Obtener info del usuario para el frontend
    usuario = db.query(Usuario).filter(Usuario.id == solicitud.user_id).first()
    email_usuario = usuario.email if usuario else None
    nombre_usuario = f"{usuario.nombre} {usuario.apellido}".strip() if usuario else None

    if solicitud.is_used:
        return {"status": "used", "email": None, "nombre": None}

    if solicitud.expires_at < datetime.utcnow():
        return {"status": "expired", "email": email_usuario, "nombre": nombre_usuario}

    return {
        "status": "valid",
        "email": email_usuario,
        "nombre": nombre_usuario,
    }


def procesar_reseteo_password(db: Session, token: str, new_password: str) -> dict:
    """
    Valida el token y actualiza la contraseña del usuario.
    - Token expirado  → 410 Gone
    - Token inválido/usado → 400 Bad Request
    """
    token_hash = hash_token(token)

    solicitud = db.query(PasswordResetToken).filter(
        PasswordResetToken.token_hash == token_hash
    ).first()

    if not solicitud:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El enlace de recuperación es inválido.",
        )

    if solicitud.is_used:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este enlace ya fue utilizado. Solicita uno nuevo.",
        )

    if solicitud.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Tu enlace para cambiar la contraseña ha expirado. Solicita uno nuevo.",
        )

    # Buscar usuario asociado al token
    usuario = db.query(Usuario).filter(Usuario.id == solicitud.user_id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado.",
        )

    # Validar fortaleza de la contraseña
    validar_password_segura(new_password)

    # Actualizar contraseña y marcar token como usado
    usuario.password = hash_password(new_password)
    solicitud.is_used = True

    db.commit()

    return {"message": "Contraseña actualizada con éxito."}
