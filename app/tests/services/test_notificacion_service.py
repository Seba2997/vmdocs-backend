import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException
from app.services.notificacion_service import (
    crear_notificacion,
    notificar_a_administradores,
    obtener_notificaciones,
    marcar_como_leida,
    marcar_todas_como_leidas
)
from app.models.notificacion_model import Notificacion, TipoNotificacion
from app.models.usuario import Usuario

def test_crear_notificacion_exitosa():
    # Arrange
    db = MagicMock()
    
    # Act
    resultado = crear_notificacion(db, 1, TipoNotificacion.CASO, 10, "Mensaje de prueba")

    # Assert
    assert resultado.usuario_id == 1
    assert resultado.tipo == TipoNotificacion.CASO
    assert resultado.mensaje == "Mensaje de prueba"
    db.add.assert_called_once()
    db.commit.assert_called_once()
    db.refresh.assert_called_once()

def test_notificar_a_administradores():
    # Arrange
    db = MagicMock()
    admin1 = Usuario(id=1, rol="ADMIN", estado=True)
    admin2 = Usuario(id=2, rol="ADMIN", estado=True)
    db.query().filter().all.return_value = [admin1, admin2]

    # Act
    notificar_a_administradores(db, TipoNotificacion.CASO, 10, "Alerta general")

    # Assert
    # crear_notificacion hace add, commit y refresh por cada admin
    assert db.add.call_count == 2
    assert db.commit.call_count == 2

def test_obtener_notificaciones_paginacion():
    # Arrange
    db = MagicMock()
    # Simular la cuenta y luego la lista
    db.query().filter().count.return_value = 10
    db.query().filter().order_by().limit().all.return_value = [Notificacion(), Notificacion()]

    # Act
    total, lista = obtener_notificaciones(db, 1, limit=5)

    # Assert
    assert total == 10
    assert len(lista) == 2

def test_marcar_como_leida_exitosa():
    # Arrange
    db = MagicMock()
    mock_notificacion = Notificacion(id=1, usuario_id=1, leida=False)
    db.query().filter().first.return_value = mock_notificacion

    # Act
    resultado = marcar_como_leida(db, 1, 1)

    # Assert
    assert resultado.leida is True
    db.commit.assert_called_once()
    db.refresh.assert_called_once()

def test_marcar_todas_como_leidas_exitosa():
    # Arrange
    db = MagicMock()

    # Act
    resultado = marcar_todas_como_leidas(db, 1)

    # Assert
    assert resultado["mensaje"] == "Todas las notificaciones marcadas como leídas"
    db.query().filter().update.assert_called_once_with({"leida": True})
    db.commit.assert_called_once()
