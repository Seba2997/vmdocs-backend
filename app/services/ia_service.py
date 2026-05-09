"""Servicio de integración con Groq AI para VMDocs."""

import json
import logging
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import HTTPException
from pydantic import BaseModel, ValidationError
from sqlalchemy.orm import Session
from groq import Groq

from app.config import GROQ_API_KEY, GROQ_MODEL, GROQ_MAX_CHARS
from app.models.documento_model import Documento

logger = logging.getLogger(__name__)


# Validación interna para la respuesta JSON del modelo

class _FichaValidada(BaseModel):
    tipo_documento: Optional[str] = None
    partes_involucradas: List[str] = []
    fechas_importantes: List[str] = []
    montos_detectados: List[str] = []
    resumen_corto: Optional[str] = None


# Prompt base del sistema

_SYSTEM_PROMPT = (
    "Eres un asistente especializado en analisis de documentos juridicos. "
    "Trabajas EXCLUSIVAMENTE con el documento que el usuario te proporciona. "
    "Nunca inventes informacion que no este en el documento. "
    "Si un dato no existe en el documento, indicalo claramente. "
    "Mantén siempre un lenguaje formal, preciso y objetivo."
)


# Funciones Groq

def _get_groq_client() -> Groq:
    """Instancia el cliente de Groq. Lanza 503 si la API KEY no esta configurada."""
    if not GROQ_API_KEY:
        raise HTTPException(
            status_code=503,
            detail=(
                "El modulo de IA no esta configurado. "
                "Define GROQ_API_KEY en el archivo .env."
            ),
        )
    return Groq(api_key=GROQ_API_KEY)


# -----------------------------------------------------------------------------
# HELPERS INTERNOS
# -----------------------------------------------------------------------------

def _obtener_documento_activo_o_404(db: Session, documento_id: int) -> Documento:
    """Retorna el documento activo o lanza 404."""
    doc = db.query(Documento).filter(
        Documento.id == documento_id,
        Documento.activo == True,
    ).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Documento no encontrado.")
    return doc


def _obtener_texto_documento(doc: Documento) -> str:
    """
    Lee el texto extraido del documento desde texto_extraido.
    Lanza 422 si no hay texto disponible (PDF escaneado, imagen, etc.).
    """
    texto = getattr(doc, "texto_extraido", None)
    if not texto:
        raise HTTPException(
            status_code=422,
            detail=(
                "El documento no tiene texto extraido disponible para analisis IA. "
                "Solo se admiten PDFs con texto embebido, DOCX y XLSX."
            ),
        )
    return texto[:GROQ_MAX_CHARS]


def _limpiar_json_raw(raw: str) -> str:
    """
    Limpia la respuesta del modelo eliminando bloques markdown y espacios.
    Maneja: ```json ... ```, ``` ... ``` y texto plano.

    Aunque json_mode=True deberia evitar esto, se mantiene como fallback
    defensivo para modelos que ignoran parcialmente la instruccion.
    """
    limpio = raw.strip()
    if limpio.startswith("```"):
        lineas = limpio.splitlines()
        lineas = lineas[1:]  # Eliminar primera linea (```json o ```)
        if lineas and lineas[-1].strip() == "```":
            lineas = lineas[:-1]  # Eliminar cierre ```
        limpio = "\n".join(lineas).strip()
    return limpio


def _llamar_groq(
    client: Groq,
    user_prompt: str,
    max_tokens: int,
    json_mode: bool = False,
) -> str:
    """Envía un prompt a Groq y retorna la respuesta."""
    kwargs = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.2,
        "max_tokens": max_tokens,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    try:
        response = client.chat.completions.create(**kwargs)
        texto = response.choices[0].message.content
        if not texto or not texto.strip():
            raise HTTPException(
                status_code=502,
                detail="El modelo de IA devolvio una respuesta vacia. Intenta nuevamente.",
            )
        return texto.strip()
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Error al llamar a Groq API [%s]: %s", type(exc).__name__, exc)
        raise HTTPException(
            status_code=502,
            detail=f"Error de comunicacion con el servicio de IA: {type(exc).__name__}.",
        )


def _marcar_timestamp_ia(db: Session, doc: Documento) -> None:
    """Actualiza el timestamp de ultima generacion IA en el documento."""
    doc.ia_generado_en = datetime.now(timezone.utc)
    db.commit()
    db.refresh(doc)


# -----------------------------------------------------------------------------
# 1. GENERAR RESUMEN IA
# -----------------------------------------------------------------------------

def generar_resumen(db: Session, documento_id: int, forzar: bool = False) -> Documento:
    """
    Genera y persiste un resumen profesional del documento usando Groq.
    Si forzar=False y ya existe resumen en BD, lo devuelve desde cache.
    """
    doc = _obtener_documento_activo_o_404(db, documento_id)

    if doc.resumen_ia and not forzar:
        logger.info("Resumen IA obtenido desde cache para documento %d.", documento_id)
        return doc

    texto = _obtener_texto_documento(doc)
    client = _get_groq_client()

    # Delimitador ## Documento: separa claramente las instrucciones del contenido.
    # Reduce el riesgo de que el modelo confunda instrucciones con texto del documento.
    prompt = (
        "Resume el siguiente documento juridico en maximo 10 lineas.\n\n"
        "Instrucciones:\n"
        "- Lenguaje formal y profesional.\n"
        "- Extrae solo informacion presente en el documento.\n"
        "- Si el documento esta incompleto, resume unicamente lo disponible.\n"
        "- Sin titulos, encabezados ni listas. Solo parrafo continuo.\n\n"
        "## Documento:\n"
        f"{texto}"
    )

    resumen = _llamar_groq(client, prompt, max_tokens=500)
    doc.resumen_ia = resumen
    _marcar_timestamp_ia(db, doc)

    logger.info("Resumen IA generado y guardado para documento %d.", documento_id)
    return doc


# -----------------------------------------------------------------------------
# 2. GENERAR FICHA IA
# -----------------------------------------------------------------------------

def _parsear_y_validar_ficha(raw: str) -> dict:
    """Parsea la respuesta JSON y valida con Pydantic."""
    limpio = _limpiar_json_raw(raw)

    try:
        data = json.loads(limpio)
    except json.JSONDecodeError as exc:
        logger.error("El modelo devolvio JSON invalido: %s", exc)
        raise HTTPException(
            status_code=502,
            detail=(
                "La IA devolvio una respuesta con formato invalido. "
                "Intenta nuevamente o verifica que el documento tenga texto legible."
            ),
        )

    # Validacion semantica con Pydantic: corrige tipos incorrectos sin fallar
    try:
        ficha = _FichaValidada(**data)
    except ValidationError:
        # Si la validacion falla, construir con lo que sea valido campo por campo
        ficha = _FichaValidada(
            tipo_documento=data.get("tipo_documento"),
            partes_involucradas=(
                data.get("partes_involucradas")
                if isinstance(data.get("partes_involucradas"), list) else []
            ),
            fechas_importantes=(
                data.get("fechas_importantes")
                if isinstance(data.get("fechas_importantes"), list) else []
            ),
            montos_detectados=(
                data.get("montos_detectados")
                if isinstance(data.get("montos_detectados"), list) else []
            ),
            resumen_corto=data.get("resumen_corto"),
        )

    return ficha.model_dump()


def generar_ficha(db: Session, documento_id: int, forzar: bool = False) -> Documento:
    """
    Genera y persiste una ficha estructurada del documento usando Groq.
    Usa json_mode=True para forzar salida JSON estricta desde el modelo.
    Si forzar=False y ya existe ficha en BD, la devuelve desde cache.
    """
    doc = _obtener_documento_activo_o_404(db, documento_id)

    if doc.ficha_ia and not forzar:
        logger.info("Ficha IA obtenida desde cache para documento %d.", documento_id)
        return doc

    texto = _obtener_texto_documento(doc)
    client = _get_groq_client()

    # El prompt describe cada campo en lugar de mostrar el schema JSON completo.
    # Esto funciona mejor con json_mode=True porque el modelo ya sabe que debe
    # devolver JSON; las instrucciones en prosa son mas robustas que un schema literal.
    prompt = (
        "Analiza el siguiente documento juridico y extrae los datos solicitados.\n\n"
        "Devuelve un objeto JSON con exactamente estas claves:\n"
        "- tipo_documento: string con el tipo de documento (contrato, escritura, resolucion, etc.), "
        "o null si no se puede determinar.\n"
        "- partes_involucradas: lista de strings con nombres de personas o entidades mencionadas. "
        "Lista vacia [] si no hay.\n"
        "- fechas_importantes: lista de strings con fechas en formato YYYY-MM-DD. "
        "Lista vacia [] si no hay fechas.\n"
        "- montos_detectados: lista de strings con montos o valores economicos detectados "
        "(ejemplo: '$1.000.000'). Lista vacia [] si no hay.\n"
        "- resumen_corto: string de maximo 2 oraciones resumiendo el proposito del documento, "
        "o null si no hay suficiente informacion.\n\n"
        "Reglas estrictas:\n"
        "- Extrae SOLO informacion que aparezca explicitamente en el documento.\n"
        "- No inventes datos. Si un campo no existe, usa null o [].\n"
        "- Las listas deben contener unicamente strings.\n\n"
        "## Documento:\n"
        f"{texto}"
    )

    raw = _llamar_groq(client, prompt, max_tokens=700, json_mode=True)
    ficha = _parsear_y_validar_ficha(raw)

    doc.ficha_ia = ficha
    _marcar_timestamp_ia(db, doc)

    logger.info("Ficha IA generada y guardada para documento %d.", documento_id)
    return doc


# -----------------------------------------------------------------------------
# 3. PREGUNTA AL DOCUMENTO
# -----------------------------------------------------------------------------

def preguntar_documento(db: Session, documento_id: int, pregunta: str) -> str:
    """
    Responde una pregunta basandose UNICAMENTE en el contenido del documento.
    No utiliza conocimiento externo del modelo. Respuestas no se cachean.
    """
    if not pregunta or not pregunta.strip():
        raise HTTPException(
            status_code=400,
            detail="La pregunta no puede estar vacia.",
        )

    doc = _obtener_documento_activo_o_404(db, documento_id)
    texto = _obtener_texto_documento(doc)
    client = _get_groq_client()

    # Los delimitadores ## Pregunta: y ## Documento: evitan que el modelo
    # mezcle la pregunta con el contenido del documento al procesar el contexto.
    prompt = (
        "Responde la siguiente pregunta usando UNICAMENTE la informacion "
        "presente en el documento.\n\n"
        "Si la respuesta no se encuentra en el documento, responde exactamente: "
        "'La informacion no aparece en el documento.'\n\n"
        "No uses conocimiento externo. No hagas suposiciones.\n\n"
        "## Pregunta:\n"
        f"{pregunta.strip()}\n\n"
        "## Documento:\n"
        f"{texto}"
    )

    respuesta = _llamar_groq(client, prompt, max_tokens=300)
    logger.info("Pregunta respondida para documento %d.", documento_id)
    return respuesta
