import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from app.services.cliente_service import (
    crear_cliente,
    actualizar_cliente,
    toggle_estado_cliente
)
from app.schemas.cliente_schema import ClienteCreate, ClienteUpdate
from app.models.cliente_model import Cliente

@patch("app.services.notificacion_service.notificar_a_administradores")
def test_crear_cliente_nuevo_exitoso(mock_notificar):
    db = MagicMock()
    # Simular que no existe cliente con RUT/Email
    db.query().filter().first.return_value = None
    
    cliente_in = ClienteCreate(rut="12345678-9", nombre="Juan", apellido="Perez", email="juan@example.com", tipo="PERSONA")
    nuevo_cliente = crear_cliente(db, cliente_in, creador_id=1)
    
    assert nuevo_cliente.rut == "12345678-9"
    db.add.assert_called_once()
    db.commit.assert_called_once()
    mock_notificar.assert_called_once()

@patch("app.services.notificacion_service.notificar_a_administradores")
def test_crear_cliente_reactiva_inactivo(mock_notificar):
    db = MagicMock()
    # Existe pero inactivo
    cliente_existente = Cliente(id=1, rut="12345678-9", estado=False)
    db.query().filter().first.return_value = cliente_existente
    
    cliente_in = ClienteCreate(rut="12345678-9", nombre="Juan", apellido="Perez", email="juan@example.com", tipo="PERSONA")
    resultado = crear_cliente(db, cliente_in, creador_id=1)
    
    assert resultado.estado is True
    assert resultado.nombre == "Juan"
    db.add.assert_not_called()
    db.commit.assert_called_once()
    mock_notificar.assert_called_once()

def test_crear_cliente_falla_existente_activo():
    db = MagicMock()
    # Existe y está activo
    cliente_existente = Cliente(id=1, rut="12345678-9", estado=True)
    db.query().filter().first.return_value = cliente_existente
    
    cliente_in = ClienteCreate(rut="12345678-9", nombre="Juan", apellido="Perez", email="juan@example.com", tipo="PERSONA")
    
    with pytest.raises(HTTPException) as exc_info:
        crear_cliente(db, cliente_in, creador_id=1)
    assert exc_info.value.status_code == 400

def test_actualizar_cliente_exitoso():
    db = MagicMock()
    cliente_existente = Cliente(id=1, nombre="Viejo", email="viejo@example.com", estado=True)
    
    # 1. Busca el cliente, 2. Valida email único (no encuentra otro)
    db.query().filter().first.side_effect = [cliente_existente, None]
    
    update_in = ClienteUpdate(nombre="Nuevo", email="nuevo@example.com")
    resultado = actualizar_cliente(db, 1, update_in, usuario_id=2)
    
    assert resultado.nombre == "Nuevo"
    assert resultado.updated_by == 2
    db.commit.assert_called_once()

def test_toggle_estado_cliente_exitoso():
    db = MagicMock()
    cliente_existente = Cliente(id=1, estado=True)
    db.query().filter().first.return_value = cliente_existente
    
    res = toggle_estado_cliente(db, 1)
    
    assert res["estado"] is False
    assert cliente_existente.estado is False
    db.commit.assert_called_once()
