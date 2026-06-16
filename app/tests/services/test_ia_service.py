import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from app.services.ia_service import (
    generar_resumen,
    generar_ficha,
    preguntar_documento,
    _parsear_y_validar_ficha,
    _obtener_texto_documento
)
from app.models.documento_model import Documento

def test_generar_resumen_usa_cache():
    db = MagicMock()
    doc_mock = Documento(id=1, activo=True, resumen_ia="Resumen en BD")
    db.query().filter().first.return_value = doc_mock

    res = generar_resumen(db, 1, forzar=False)
    
    assert res.resumen_ia == "Resumen en BD"
    db.commit.assert_not_called()

@patch("app.services.ia_service._get_groq_client")
@patch("app.services.ia_service._llamar_groq")
def test_generar_resumen_llama_groq(mock_llamar, mock_get_client):
    db = MagicMock()
    doc_mock = Documento(id=1, activo=True, resumen_ia=None, texto_extraido="Texto del pdf")
    db.query().filter().first.return_value = doc_mock
    
    mock_llamar.return_value = "Nuevo resumen"
    
    res = generar_resumen(db, 1, forzar=False)
    
    assert res.resumen_ia == "Nuevo resumen"
    mock_llamar.assert_called_once()
    db.commit.assert_called_once()

def test_generar_ficha_parsea_json_valido():
    json_valido = '{"tipo_documento": "Contrato", "partes_involucradas": ["Juan"], "fechas_importantes": [], "montos_detectados": [], "resumen_corto": "Res"}'
    ficha = _parsear_y_validar_ficha(json_valido)
    assert ficha["tipo_documento"] == "Contrato"
    assert ficha["partes_involucradas"] == ["Juan"]

@patch("app.services.ia_service._get_groq_client")
@patch("app.services.ia_service._llamar_groq")
def test_preguntar_documento_exitoso(mock_llamar, mock_get_client):
    db = MagicMock()
    doc_mock = Documento(id=1, activo=True, texto_extraido="Hola")
    db.query().filter().first.return_value = doc_mock
    mock_llamar.return_value = "La respuesta es 42"
    
    res = preguntar_documento(db, 1, "Cual es la respuesta?")
    
    assert res == "La respuesta es 42"
    mock_llamar.assert_called_once()
    db.commit.assert_not_called()

def test_obtener_texto_documento_falla_sin_texto():
    doc_mock = Documento(id=1, texto_extraido=None)
    with pytest.raises(HTTPException) as exc_info:
        _obtener_texto_documento(doc_mock)
    assert exc_info.value.status_code == 422
