import pytest
from fastapi import HTTPException
from unittest.mock import MagicMock
from app.services.usuario_service import (
    validar_password_segura,
    crear_usuario,
    cambiar_estado_usuario
)
from app.schemas.usuario import UsuarioCreate
from app.models.usuario import Usuario

def test_validar_password_segura_exitosa():
    # Arrange & Act & Assert
    # No debería levantar excepción
    validar_password_segura("Password123!")

def test_validar_password_segura_falla_por_longitud():
    # Arrange & Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        validar_password_segura("Pw1!")
    
    assert exc_info.value.status_code == 400
    assert "al menos 8 caracteres" in exc_info.value.detail

def test_crear_usuario_exitoso():
    # Arrange
    db = MagicMock()
    # Simular que el correo no existe (first() retorna None)
    db.query().filter().first.return_value = None
    
    usuario_in = UsuarioCreate(
        nombre="Test",
        apellido="User",
        email="test@example.com",
        password="Password123!",
        rol="USER",
        estado=True
    )

    # Act
    nuevo_usuario = crear_usuario(db, usuario_in)

    # Assert
    assert nuevo_usuario.email == "test@example.com"
    db.add.assert_called_once()
    db.commit.assert_called_once()
    db.refresh.assert_called_once()

def test_crear_usuario_falla_correo_existente():
    # Arrange
    db = MagicMock()
    # Simular que el correo ya existe
    db.query().filter().first.return_value = Usuario(id=1, email="test@example.com")
    
    usuario_in = UsuarioCreate(
        nombre="Test",
        apellido="User",
        email="test@example.com",
        password="Password123!",
        rol="USER",
        estado=True
    )

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        crear_usuario(db, usuario_in)

    assert exc_info.value.status_code == 400
    assert "correo ya está registrado" in exc_info.value.detail

def test_cambiar_estado_usuario_falla_admin_maestro():
    # Arrange
    db = MagicMock()
    usuario_id = 1
    ejecutor_id = 2

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        cambiar_estado_usuario(db, usuario_id, ejecutor_id)

    assert exc_info.value.status_code == 403
    assert "Administrador Maestro no puede ser desactivado" in exc_info.value.detail
