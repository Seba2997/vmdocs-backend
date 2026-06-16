import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from app.services.caso_service import (
    crear_caso,
    obtener_caso_por_id,
    asignar_usuario_a_caso
)
from app.schemas.caso_schema import CasoCreate
from app.models.caso_model import Caso
from app.models.usuario import Usuario
from app.models.caso_usuario_model import CasoUsuario

@patch("app.services.notificacion_service.notificar_a_administradores")
def test_crear_caso_exitoso(mock_notificar):
    db = MagicMock()
    caso_in = CasoCreate(titulo="Caso Test", descripcion="Desc", cliente_id=1, tipo_tarifa="FIJA", monto_tarifa=1000)
    
    caso_creado = crear_caso(db, caso_in, creador_id=1)
    
    assert caso_creado.titulo == "Caso Test"
    assert db.add.call_count == 2  # Caso y CasoUsuario
    db.commit.assert_called_once()
    mock_notificar.assert_called_once()

def test_obtener_caso_por_id_exitoso():
    db = MagicMock()
    mock_caso = Caso(id=1, activo=True)
    db.query().filter().first.return_value = mock_caso
    
    caso = obtener_caso_por_id(db, 1)
    assert caso.id == 1

def test_obtener_caso_por_id_falla_inactivo():
    db = MagicMock()
    db.query().filter().first.return_value = None
    
    with pytest.raises(HTTPException) as exc_info:
        obtener_caso_por_id(db, 1)
    assert exc_info.value.status_code == 404

@patch("app.services.notificacion_service.crear_notificacion")
def test_asignar_usuario_a_caso_exitoso(mock_crear_notificacion):
    db = MagicMock()
    mock_caso = Caso(id=1, activo=True, titulo="Test")
    mock_usuario = Usuario(id=2, estado=True)
    
    # 1. Caso existe, 2. Usuario existe, 3. No hay asignacion previa
    db.query().filter().first.side_effect = [mock_caso, mock_usuario, None]
    
    def mock_refresh(obj):
        obj.caso = mock_caso
    db.refresh.side_effect = mock_refresh
    
    asignacion = asignar_usuario_a_caso(db, 1, 2)
    
    assert asignacion.caso_id == 1
    assert asignacion.usuario_id == 2
    db.add.assert_called_once()
    db.commit.assert_called_once()
    mock_crear_notificacion.assert_called_once()

def test_asignar_usuario_a_caso_falla_duplicado():
    db = MagicMock()
    mock_caso = Caso(id=1, activo=True)
    mock_usuario = Usuario(id=2, estado=True)
    mock_asignacion = CasoUsuario(caso_id=1, usuario_id=2)
    
    # Asignacion ya existe en la 3ra query
    db.query().filter().first.side_effect = [mock_caso, mock_usuario, mock_asignacion]
    
    with pytest.raises(HTTPException) as exc_info:
        asignar_usuario_a_caso(db, 1, 2)
    assert exc_info.value.status_code == 409
