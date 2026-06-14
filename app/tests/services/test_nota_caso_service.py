import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException
from app.services.nota_caso_service import (
    crear_nota,
    actualizar_nota,
    eliminar_nota
)
from app.models.nota_caso_model import NotaCaso
from app.models.caso_model import Caso
from app.schemas.nota_caso_schema import NotaCasoCreate, NotaCasoUpdate

def test_crear_nota_exitoso():
    db = MagicMock()
    db.query().filter().first.return_value = Caso(id=1)
    
    nota_in = NotaCasoCreate(contenido="Nota test")
    res = crear_nota(db, 1, 2, nota_in)
    
    assert res.contenido == "Nota test"
    assert res.caso_id == 1
    assert res.usuario_id == 2
    db.add.assert_called_once()
    db.commit.assert_called_once()

def test_crear_nota_falla_caso_no_encontrado():
    db = MagicMock()
    db.query().filter().first.return_value = None
    
    with pytest.raises(HTTPException) as exc_info:
        crear_nota(db, 1, 2, NotaCasoCreate(contenido="Test"))
    assert exc_info.value.status_code == 404

def test_actualizar_nota_exitoso():
    db = MagicMock()
    # Usuario dueño
    mock_nota = NotaCaso(id=1, usuario_id=2, contenido="Antiguo")
    db.query().filter().first.return_value = mock_nota
    
    res = actualizar_nota(db, 1, 2, False, NotaCasoUpdate(contenido="Nuevo"))
    
    assert res.contenido == "Nuevo"
    db.commit.assert_called_once()

def test_actualizar_nota_falla_permisos():
    db = MagicMock()
    # Dueño es 2
    mock_nota = NotaCaso(id=1, usuario_id=2, contenido="Antiguo")
    db.query().filter().first.return_value = mock_nota
    
    with pytest.raises(HTTPException) as exc_info:
        # Intenta editar el usuario 3 (no admin)
        actualizar_nota(db, 1, 3, False, NotaCasoUpdate(contenido="Nuevo"))
    assert exc_info.value.status_code == 403

def test_eliminar_nota_admin_exitoso():
    db = MagicMock()
    # Dueño es 2
    mock_nota = NotaCaso(id=1, usuario_id=2)
    db.query().filter().first.return_value = mock_nota
    
    # Intenta borrar el admin (usuario 10, es_admin=True)
    res = eliminar_nota(db, 1, 10, True)
    
    assert "eliminada" in res["mensaje"]
    db.delete.assert_called_once()
    db.commit.assert_called_once()
