import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException, UploadFile
from app.services.documento_service import (
    _validar_archivo,
    subir_documento,
    generar_signed_url,
    toggle_estado_documento,
    eliminar_definitivamente
)
from app.models.documento_model import Documento
from app.models.caso_model import Caso
from app.config import TAMANO_MAXIMO_BYTES

def test_validar_archivo_falla_tamano_y_mime():
    mock_file = MagicMock(spec=UploadFile)
    mock_file.content_type = "application/x-msdos-program"
    mock_file.filename = "virus.exe"
    
    with pytest.raises(HTTPException) as exc_info:
        _validar_archivo(mock_file, 1000)
    assert exc_info.value.status_code == 400
    
    mock_file.content_type = "application/pdf"
    mock_file.filename = "doc.pdf"
    with pytest.raises(HTTPException) as exc_info:
        # Excede tamaño máximo
        _validar_archivo(mock_file, TAMANO_MAXIMO_BYTES + 1)
    assert exc_info.value.status_code == 413

@patch("app.services.documento_service._get_supabase")
@patch("app.services.documento_service._extraer_texto")
def test_subir_documento_exitoso(mock_extraer_texto, mock_get_supabase):
    db = MagicMock()
    # El caso existe y activo
    db.query().filter().first.return_value = Caso(id=1, activo=True)
    
    mock_file = MagicMock()
    mock_file.content_type = "application/pdf"
    mock_file.filename = "test.pdf"
    mock_file.file.read.return_value = b"Contenido del PDF"
    
    mock_extraer_texto.return_value = "Texto extraido"
    mock_supabase_client = MagicMock()
    mock_get_supabase.return_value = mock_supabase_client
    
    doc = subir_documento(db, 1, 2, mock_file)
    
    assert doc.nombre_original == "test.pdf"
    assert doc.usuario_id == 2
    mock_supabase_client.storage.from_().upload.assert_called_once()
    db.add.assert_called_once()
    db.commit.assert_called_once()

@patch("app.services.documento_service._get_supabase")
def test_generar_signed_url_exitoso(mock_get_supabase):
    db = MagicMock()
    db.query().filter().first.return_value = Documento(id=1, nombre_storage="path/file", activo=True)
    
    mock_supabase_client = MagicMock()
    mock_supabase_client.storage.from_().create_signed_url.return_value = {"signedUrl": "https://signed.url"}
    mock_get_supabase.return_value = mock_supabase_client
    
    res = generar_signed_url(db, 1)
    
    assert res["signed_url"] == "https://signed.url"

def test_toggle_estado_documento_falla_permisos():
    db = MagicMock()
    # Documento subido por usuario 2
    db.query().filter().first.return_value = Documento(id=1, usuario_id=2, activo=True)
    
    with pytest.raises(HTTPException) as exc_info:
        # Usuario 3 intenta moverlo
        toggle_estado_documento(db, 1, usuario_solicitante_id=3)
    assert exc_info.value.status_code == 403

@patch("app.services.documento_service._get_supabase")
def test_eliminar_definitivamente_exitoso(mock_get_supabase):
    db = MagicMock()
    # Inactivo y subido por el mismo usuario 2
    mock_doc = Documento(id=1, usuario_id=2, activo=False, nombre_storage="path/file", nombre_original="f")
    db.query().filter().first.return_value = mock_doc
    
    mock_supabase_client = MagicMock()
    mock_get_supabase.return_value = mock_supabase_client
    
    res = eliminar_definitivamente(db, 1, usuario_solicitante_id=2)
    
    assert "eliminado definitivamente" in res["mensaje"]
    mock_supabase_client.storage.from_().remove.assert_called_once_with(["path/file"])
    db.delete.assert_called_once_with(mock_doc)
    db.commit.assert_called_once()
