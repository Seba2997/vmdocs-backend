import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from app.services.auth_service import autenticar_usuario
from app.models.usuario import Usuario
from app.utils.jwt_security import credentials_exception

@patch("app.services.auth_service.verify_password")
def test_autenticar_usuario_exitoso(mock_verify_password):
    # Arrange
    db = MagicMock()
    mock_usuario = Usuario(id=1, email="test@example.com", password="hashed_password", estado=True)
    db.query().filter().first.return_value = mock_usuario
    mock_verify_password.return_value = True

    # Act
    resultado = autenticar_usuario(db, "test@example.com", "Password123!")

    # Assert
    assert resultado.id == 1
    assert resultado.email == "test@example.com"
    mock_verify_password.assert_called_once_with("Password123!", "hashed_password")

def test_autenticar_usuario_falla_correo_incorrecto():
    # Arrange
    db = MagicMock()
    db.query().filter().first.return_value = None

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        autenticar_usuario(db, "noexiste@example.com", "Password123!")

    assert exc_info.value == credentials_exception
    assert exc_info.value.status_code == 401

@patch("app.services.auth_service.verify_password")
def test_autenticar_usuario_falla_password_incorrecta(mock_verify_password):
    # Arrange
    db = MagicMock()
    mock_usuario = Usuario(id=1, email="test@example.com", password="hashed_password", estado=True)
    db.query().filter().first.return_value = mock_usuario
    mock_verify_password.return_value = False

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        autenticar_usuario(db, "test@example.com", "WrongPassword!")

    assert exc_info.value == credentials_exception
    assert exc_info.value.status_code == 401

@patch("app.services.auth_service.verify_password")
def test_autenticar_usuario_falla_usuario_inactivo(mock_verify_password):
    # Arrange
    db = MagicMock()
    mock_usuario = Usuario(id=1, email="test@example.com", password="hashed_password", estado=False)
    db.query().filter().first.return_value = mock_usuario
    mock_verify_password.return_value = True

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        autenticar_usuario(db, "test@example.com", "Password123!")

    assert exc_info.value.status_code == 403
    assert "cuenta está desactivada" in exc_info.value.detail

def test_autenticar_usuario_falla_usuario_no_encontrado():
    # Arrange
    db = MagicMock()
    # first() devuelve None
    db.query().filter().first.return_value = None

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        autenticar_usuario(db, "test@example.com", "Password123!")

    assert exc_info.value == credentials_exception
    assert exc_info.value.status_code == 401
