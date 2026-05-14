"""Endpoints IA: resumen, ficha y pregunta."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.usuario import Usuario
from app.schemas.ia_schema import (
    ResumenIAResponse,
    FichaIAResponse,
    PreguntaIARequest,
    PreguntaIAResponse,
)
from app.services import ia_service, documento_service
from app.utils.jwt_security import obtener_usuario_actual_activo
from app.services.actividad_service import registrar_actividad
from app.models.actividad_model import AccionActividad, EntidadActividad

router = APIRouter(
    prefix="/documentos",
    tags=["IA - Análisis de documentos"],
)


# ─────────────────────────────────────────────────────────────────────────────
# HELPER DE ACCESO
# ─────────────────────────────────────────────────────────────────────────────

def _verificar_acceso_documento(
    db: Session,
    documento_id: int,
    current_user: Usuario,
):
    """
    Obtiene el documento y verifica que el usuario tenga acceso al caso.
    ADMIN: acceso total.
    USER: debe estar asignado al caso del documento.
    """
    doc = documento_service.obtener_documento_por_id(db, documento_id)
    if current_user.rol != "ADMIN":
        documento_service.verificar_acceso_a_caso_o_403(db, current_user.id, doc.caso_id)
    return doc


# ─────────────────────────────────────────────────────────────────────────────
# 1. RESUMEN IA
# ─────────────────────────────────────────────────────────────────────────────

@router.post(
    "/{documento_id}/ia/resumen",
    response_model=ResumenIAResponse,
    operation_id="generar_resumen_ia",
    summary="Generar resumen IA del documento",
    description=(
        "Genera un resumen profesional del documento usando Google Gemini. "
        "El resultado se guarda en la base de datos para evitar recalcular. "
        "Usa ?forzar=true para regenerar aunque ya exista un resumen guardado. "
        "ADMIN: acceso total. USER: solo si está asignado al caso del documento."
    ),
    status_code=200,
)
def generar_resumen_ia(
    documento_id: int,
    forzar: bool = Query(
        default=False,
        description="Si es true, regenera el resumen aunque ya exista uno guardado.",
    ),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obtener_usuario_actual_activo),
):
    _verificar_acceso_documento(db, documento_id, current_user)
    doc = ia_service.generar_resumen(db, documento_id, forzar=forzar)
    registrar_actividad(db, current_user.id, AccionActividad.ANALISIS_IA, EntidadActividad.DOCUMENTO, doc.id, f"Resumen IA generado", doc.caso_id)
    return ResumenIAResponse(
        documento_id=doc.id,
        resumen_ia=doc.resumen_ia,
        generado_en=doc.ia_generado_en,
    )


# ─────────────────────────────────────────────────────────────────────────────
# 2. FICHA IA
# ─────────────────────────────────────────────────────────────────────────────

@router.post(
    "/{documento_id}/ia/ficha",
    response_model=FichaIAResponse,
    operation_id="generar_ficha_ia",
    summary="Generar ficha estructurada IA del documento",
    description=(
        "Genera una ficha con datos clave del documento (tipo, partes, fechas, montos). "
        "El resultado se guarda en la base de datos. "
        "Usa ?forzar=true para regenerar aunque ya exista una ficha guardada. "
        "ADMIN: acceso total. USER: solo si está asignado al caso del documento."
    ),
    status_code=200,
)
def generar_ficha_ia(
    documento_id: int,
    forzar: bool = Query(
        default=False,
        description="Si es true, regenera la ficha aunque ya exista una guardada.",
    ),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obtener_usuario_actual_activo),
):
    _verificar_acceso_documento(db, documento_id, current_user)
    doc = ia_service.generar_ficha(db, documento_id, forzar=forzar)

    ficha = doc.ficha_ia or {}
    registrar_actividad(db, current_user.id, AccionActividad.ANALISIS_IA, EntidadActividad.DOCUMENTO, doc.id, f"Ficha estructurada IA generada", doc.caso_id)
    return FichaIAResponse(
        documento_id=doc.id,
        tipo_documento=ficha.get("tipo_documento"),
        partes_involucradas=ficha.get("partes_involucradas", []),
        fechas_importantes=ficha.get("fechas_importantes", []),
        montos_detectados=ficha.get("montos_detectados", []),
        resumen_corto=ficha.get("resumen_corto"),
        generado_en=doc.ia_generado_en,
    )


# ─────────────────────────────────────────────────────────────────────────────
# 3. PREGUNTA AL DOCUMENTO
# ─────────────────────────────────────────────────────────────────────────────

@router.post(
    "/{documento_id}/ia/pregunta",
    response_model=PreguntaIAResponse,
    operation_id="preguntar_al_documento",
    summary="Hacer una pregunta al documento mediante IA",
    description=(
        "Responde una pregunta del usuario basándose ÚNICAMENTE en el contenido "
        "del documento. La IA no usa conocimiento externo. "
        "Si la información no existe en el documento, responderá explícitamente. "
        "Las respuestas NO se cachean (cada pregunta es independiente). "
        "ADMIN: acceso total. USER: solo si está asignado al caso del documento."
    ),
    status_code=200,
)
def preguntar_al_documento(
    documento_id: int,
    body: PreguntaIARequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obtener_usuario_actual_activo),
):
    doc = _verificar_acceso_documento(db, documento_id, current_user)
    respuesta = ia_service.preguntar_documento(db, documento_id, body.pregunta)
    registrar_actividad(db, current_user.id, AccionActividad.ANALISIS_IA, EntidadActividad.DOCUMENTO, documento_id, f"Consulta interactiva a la IA", doc.caso_id)
    return PreguntaIAResponse(
        documento_id=documento_id,
        pregunta=body.pregunta,
        respuesta=respuesta,
    )
