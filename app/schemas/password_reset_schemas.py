from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)


class PasswordResetResponse(BaseModel):
    message: str


class TokenInfoResponse(BaseModel):
    """
    Respuesta del endpoint GET /auth/token-info/{token}.
    Siempre responde 200 — el campo `status` indica el estado real del token.

    status:
      - "valid"   → el token existe, no expiró y no fue usado
      - "expired" → el token existe pero ya expiró
      - "used"    → el token ya fue utilizado
      - "invalid" → el token no existe en la base de datos
    """
    status: str
    email: Optional[str] = None
    nombre: Optional[str] = None
