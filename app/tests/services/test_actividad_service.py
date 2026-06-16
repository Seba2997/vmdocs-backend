import pytest
from unittest.mock import MagicMock
from app.services.actividad_service import registrar_actividad, obtener_actividades
from app.models.actividad_model import Actividad, AccionActividad

def test_registrar_actividad_exitosa():
    db = MagicMock()
    actividad = registrar_actividad(db, 1, AccionActividad.CREACION, "Caso", 10, "Test", 10, "Detalles")
    
    assert actividad.usuario_id == 1
    assert actividad.accion == AccionActividad.CREACION
    db.add.assert_called_once()
    db.commit.assert_called_once()
    db.refresh.assert_called_once()

def test_registrar_actividad_falla_silenciosa():
    db = MagicMock()
    db.add.side_effect = Exception("DB Error")
    
    actividad = registrar_actividad(db, 1, AccionActividad.CREACION, "Caso", 10, "Test")
    
    assert actividad is None
    db.rollback.assert_called_once()

def test_obtener_actividades_admin():
    db = MagicMock()
    mock_query = db.query().options()
    mock_query.count.return_value = 5
    mock_query.order_by().offset().limit().all.return_value = [Actividad()] * 5
    
    total, actividades = obtener_actividades(db, usuario_id=1, es_admin=True)
    
    assert total == 5
    assert len(actividades) == 5
    mock_query.filter.assert_not_called()

def test_obtener_actividades_usuario():
    db = MagicMock()
    mock_query = db.query().options()
    mock_filter = mock_query.filter.return_value
    mock_filter.count.return_value = 2
    mock_filter.order_by().offset().limit().all.return_value = [Actividad()] * 2
    
    total, actividades = obtener_actividades(db, usuario_id=1, es_admin=False)
    
    assert total == 2
    assert len(actividades) == 2
    mock_query.filter.assert_called_once()

def test_obtener_actividades_paginacion():
    db = MagicMock()
    mock_query = db.query().options()
    mock_query.count.return_value = 10
    
    mock_order_by = mock_query.order_by.return_value
    mock_offset = mock_order_by.offset.return_value
    mock_limit = mock_offset.limit.return_value
    mock_limit.all.return_value = [Actividad()] * 5
    
    obtener_actividades(db, usuario_id=1, es_admin=True, skip=5, limit=5)
    
    mock_order_by.offset.assert_called_once_with(5)
    mock_offset.limit.assert_called_once_with(5)
