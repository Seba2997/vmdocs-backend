import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
from fastapi import HTTPException
from app.services.password_reset_service import (
    crear_solicitud_recuperacion,
    obtener_info_token,
    procesar_reseteo_password
)
from app.models.usuario import Usuario
from app.models.password_reset import PasswordResetToken
import app.services.password_reset_service as pr_service

@patch("app.services.password_reset_service.send_reset_password_email")
def test_crear_solicitud_recuperacion_usuario_existente(mock_send_email):
    # Arrange
    db = MagicMock()
    mock_usuario = Usuario(id=1, email="test@example.com")
    db.query().filter().first.return_value = mock_usuario
    
    # Act
    response = crear_solicitud_recuperacion(db, "test@example.com")

    # Assert
    assert response["message"] == "Si el correo está registrado, recibirás un enlace en breve."
    db.add.assert_called_once()
    db.commit.assert_called_once()
    mock_send_email.assert_called_once()
    assert mock_send_email.call_args[0][0] == "test@example.com"

@patch("app.services.password_reset_service.send_reset_password_email")
def test_crear_solicitud_recuperacion_usuario_inexistente(mock_send_email):
    # Arrange
    db = MagicMock()
    db.query().filter().first.return_value = None
    
    # Act
    response = crear_solicitud_recuperacion(db, "notfound@example.com")

    # Assert
    assert response["message"] == "Si el correo está registrado, recibirás un enlace en breve."
    db.add.assert_not_called()
    db.commit.assert_not_called()
    mock_send_email.assert_not_called()

def test_obtener_info_token_valido():
    # Arrange
    db = MagicMock()
    # Simular solicitud de token
    mock_solicitud = PasswordResetToken(
        user_id=1, 
        is_used=False, 
        expires_at=datetime.utcnow() + timedelta(minutes=5)
    )
    # Simular usuario
    mock_usuario = Usuario(id=1, email="test@example.com", nombre="Juan", apellido="Perez")
    
    # Configurar los retornos de db.query().filter().first() en orden
    db.query().filter().first.side_effect = [mock_solicitud, mock_usuario]

    # Act
    info = obtener_info_token(db, "fake-token")

    # Assert
    assert info["status"] == "valid"
    assert info["email"] == "test@example.com"
    assert info["nombre"] == "Juan Perez"

def test_procesar_reseteo_password_exitoso():
    # Arrange
    db = MagicMock()
    mock_solicitud = PasswordResetToken(
        user_id=1, 
        is_used=False, 
        expires_at=datetime.utcnow() + timedelta(minutes=5)
    )
    mock_usuario = Usuario(id=1, password="old-hash")
    db.query().filter().first.side_effect = [mock_solicitud, mock_usuario]

    # Act
    response = procesar_reseteo_password(db, "fake-token", "NewPassword123!")

    # Assert
    assert response["message"] == "Contraseña actualizada con éxito."
    assert mock_solicitud.is_used is True
    assert mock_usuario.password != "old-hash"
    db.commit.assert_called_once()

def test_procesar_reseteo_password_token_expirado():
    # Arrange
    db = MagicMock()
    mock_solicitud = PasswordResetToken(
        user_id=1, 
        is_used=False, 
        expires_at=datetime.utcnow() - timedelta(minutes=5)
    )
    db.query().filter().first.return_value = mock_solicitud

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        procesar_reseteo_password(db, "fake-token", "NewPassword123!")

    assert exc_info.value.status_code == 410
    assert "ha expirado" in exc_info.value.detail
