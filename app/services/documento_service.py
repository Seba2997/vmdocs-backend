import uuid

from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session
from supabase import create_client, Client

from app.config import SUPABASE_URL, SUPABASE_KEY, SUPABASE_BUCKET, TAMANO_MAXIMO_BYTES, TIPOS_MIME_PERMITIDOS
from app.models.documento_model import Documento
from app.models.caso_model import Caso
from app.models.caso_usuario_model import CasoUsuario


# ─────────────────────────────────────────────
# CLIENTE SUPABASE
# ─────────────────────────────────────────────

def _get_supabase() -> Client:
    """Instancia el cliente de Supabase Storage."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise HTTPException(
            status_code=503,
            detail="El módulo de almacenamiento no está configurado correctamente."
        )
    return create_client(SUPABASE_URL, SUPABASE_KEY)


# ─────────────────────────────────────────────
# VALIDACIONES
# ─────────────────────────────────────────────

def _validar_archivo(archivo: UploadFile, tamano: int) -> None:
    """
    Valida el tipo MIME, la extensión y el tamaño del archivo.
    Lanza HTTPException 400 si no cumple con los requisitos.
    """
    # Validar MIME type (comparar contra los valores del dict, no las claves)
    if archivo.content_type not in TIPOS_MIME_PERMITIDOS.values():
        raise HTTPException(
            status_code=400,
            detail=(
                f"Tipo de archivo no permitido: '{archivo.content_type}'. "
                f"Solo se aceptan: {', '.join(TIPOS_MIME_PERMITIDOS.values())}."
            )
        )

    # Validar extensión
    nombre = archivo.filename or ""
    extension = nombre.rsplit(".", 1)[-1].lower() if "." in nombre else ""
    extensiones_permitidas = {ext.lstrip(".") for ext in TIPOS_MIME_PERMITIDOS}
    if extension not in extensiones_permitidas:
        raise HTTPException(
            status_code=400,
            detail=f"Extensión de archivo no permitida: '.{extension}'."
        )

    # Validar tamaño
    if tamano > TAMANO_MAXIMO_BYTES:
        limite_mb = TAMANO_MAXIMO_BYTES / (1024 * 1024)
        raise HTTPException(
            status_code=413,
            detail=f"El archivo supera el tamaño máximo permitido de {limite_mb:.0f} MB."
        )


def _obtener_caso_activo_o_404(db: Session, caso_id: int) -> Caso:
    """Retorna el caso si existe y está activo, lanza 404 en caso contrario."""
    caso = db.query(Caso).filter(Caso.id == caso_id, Caso.activo == True).first()
    if not caso:
        raise HTTPException(status_code=404, detail="Caso no encontrado o inactivo.")
    return caso


def _obtener_documento_activo_o_404(db: Session, documento_id: int) -> Documento:
    """Retorna el documento si existe y está activo, lanza 404 en caso contrario."""
    doc = db.query(Documento).filter(Documento.id == documento_id, Documento.activo == True).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Documento no encontrado.")
    return doc


# ─────────────────────────────────────────────
# CONTROL DE ACCESO
# ─────────────────────────────────────────────

def usuario_tiene_acceso_a_caso(db: Session, usuario_id: int, caso_id: int) -> bool:
    """Verifica si el usuario está asignado al caso."""
    return (
        db.query(CasoUsuario)
        .filter(
            CasoUsuario.caso_id == caso_id,
            CasoUsuario.usuario_id == usuario_id,
        )
        .first()
    ) is not None


def verificar_acceso_a_caso_o_403(db: Session, usuario_id: int, caso_id: int) -> None:
    """Lanza 403 si el usuario no tiene acceso al caso."""
    if not usuario_tiene_acceso_a_caso(db, usuario_id, caso_id):
        raise HTTPException(
            status_code=403,
            detail="No tienes permiso para acceder a este caso."
        )


# ─────────────────────────────────────────────
# SUBIDA
# ─────────────────────────────────────────────

def subir_documento(
    db: Session,
    caso_id: int,
    usuario_id: int,
    archivo: UploadFile,
) -> Documento:
    """
    Valida el archivo, lo sube a Supabase Storage y persiste la metadata
    en PostgreSQL dentro de una sola operación cohesiva.
    Al ser una función síncrona (def en vez de async def), FastAPI la ejecuta
    en un thread pool, evitando bloquear el event loop principal durante la
    subida a Supabase.
    """
    # 1. Validar que el caso existe y está activo
    _obtener_caso_activo_o_404(db, caso_id)

    # 2. Leer contenido para conocer el tamaño real
    contenido = archivo.file.read()
    tamano = len(contenido)

    # 3. Validar archivo (MIME, extensión, tamaño)
    _validar_archivo(archivo, tamano)

    # 4. Generar nombre único en storage: casos/{caso_id}/{uuid}.{ext}
    nombre_original = archivo.filename or "archivo"
    extension = nombre_original.rsplit(".", 1)[-1].lower() if "." in nombre_original else "bin"
    nombre_storage = f"casos/{caso_id}/{uuid.uuid4()}.{extension}"

    # 5. Subir a Supabase Storage
    supabase = _get_supabase()
    try:
        supabase.storage.from_(SUPABASE_BUCKET).upload(
            path=nombre_storage,
            file=contenido,
            file_options={"content-type": archivo.content_type},
        )
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Error al subir el archivo al almacenamiento: {exc}"
        )

    # 6. Persistir metadata en PostgreSQL
    nuevo_doc = Documento(
        nombre_original=nombre_original,
        nombre_storage=nombre_storage,
        tipo_mime=archivo.content_type,
        tamano=tamano,
        caso_id=caso_id,
        usuario_id=usuario_id,
    )
    try:
        db.add(nuevo_doc)
        db.commit()
        db.refresh(nuevo_doc)
    except Exception:
        # Intentar eliminar el archivo de storage para no dejar huérfanos
        try:
            supabase.storage.from_(SUPABASE_BUCKET).remove([nombre_storage])
        except Exception:
            pass
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al guardar la metadata del documento.")

    return nuevo_doc


# ─────────────────────────────────────────────
# LISTADO Y OBTENCIÓN
# ─────────────────────────────────────────────

def obtener_documentos_por_caso(db: Session, caso_id: int) -> list[Documento]:
    """Retorna los documentos activos de un caso activo."""
    _obtener_caso_activo_o_404(db, caso_id)
    return (
        db.query(Documento)
        .filter(Documento.caso_id == caso_id, Documento.activo == True)
        .order_by(Documento.fecha_subida.desc())
        .all()
    )


def obtener_documentos_inactivos_por_caso(db: Session, caso_id: int) -> list[Documento]:
    """Retorna los documentos inactivos (eliminados logicamente) de un caso activo."""
    _obtener_caso_activo_o_404(db, caso_id)
    return (
        db.query(Documento)
        .filter(Documento.caso_id == caso_id, Documento.activo == False)
        .order_by(Documento.fecha_subida.desc())
        .all()
    )


def obtener_documento_por_id(db: Session, documento_id: int) -> Documento:
    """Retorna un documento activo por su ID."""
    return _obtener_documento_activo_o_404(db, documento_id)


# ─────────────────────────────────────────────
# SIGNED URL (descarga temporal)
# ─────────────────────────────────────────────

SIGNED_URL_EXPIRACION = 300  # segundos (5 minutos)


def generar_signed_url(db: Session, documento_id: int) -> dict:
    """
    Genera una URL temporal de Supabase para descargar el documento.
    NO usa URLs públicas permanentes.
    """
    doc = _obtener_documento_activo_o_404(db, documento_id)
    supabase = _get_supabase()

    try:
        respuesta = supabase.storage.from_(SUPABASE_BUCKET).create_signed_url(
            path=doc.nombre_storage,
            expires_in=SIGNED_URL_EXPIRACION,
        )
        signed_url = respuesta.get("signedURL") or respuesta.get("signedUrl")
        if not signed_url:
            raise ValueError("La respuesta de Supabase no contiene la URL firmada.")
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Error al generar la URL de descarga: {exc}"
        )

    return {"signed_url": signed_url, "expira_en": SIGNED_URL_EXPIRACION}


# ─────────────────────────────────────────────
# SOFT DELETE / PAPELERA
# ─────────────────────────────────────────────

def toggle_estado_documento(
    db: Session,
    documento_id: int,
    usuario_solicitante_id: int | None = None,
) -> dict:
    """
    Cambia el campo 'activo' del documento de forma alternada (toggle).
    Envía el documento a la papelera del caso (activo=False) o lo restaura (activo=True).

    Permisos:
      - ADMIN (usuario_solicitante_id=None): puede hacer toggle de cualquier documento.
      - USER  (usuario_solicitante_id=<id>): solo puede hacer toggle de documentos
        que él mismo haya subido (doc.usuario_id == usuario_solicitante_id).
    """
    doc = db.query(Documento).filter(Documento.id == documento_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Documento no encontrado.")

    # Verificar propiedad si es un usuario normal
    if usuario_solicitante_id is not None and doc.usuario_id != usuario_solicitante_id:
        raise HTTPException(
            status_code=403,
            detail="No tienes permiso para modificar este documento. Solo puedes gestionar los archivos que tú subiste.",
        )

    doc.activo = not doc.activo
    db.commit()
    db.refresh(doc)

    estado_texto = "restaurado" if doc.activo else "enviado a la papelera"
    return {"mensaje": f"Documento {estado_texto}.", "activo": doc.activo}


# ─────────────────────────────────────────────
# ELIMINACIÓN DEFINITIVA
# ─────────────────────────────────────────────

def eliminar_definitivamente(
    db: Session,
    documento_id: int,
    usuario_solicitante_id: int | None = None,
) -> dict:
    """
    Elimina de forma irreversible un documento que ya esté en la papelera
    (activo=False). Borra el archivo del bucket de Supabase y luego el
    registro de PostgreSQL.

    Permisos:
      - ADMIN (usuario_solicitante_id=None): puede eliminar cualquier documento.
      - USER  (usuario_solicitante_id=<id>): solo puede eliminar documentos
        que él mismo haya subido (doc.usuario_id == usuario_solicitante_id).

    Pasos:
      1. Verificar que el documento existe y está inactivo (en papelera).
      2. Si es USER, verificar que es el propietario del documento.
      3. Eliminar el archivo del bucket de Supabase.
      4. Eliminar el registro de la base de datos.
    """
    # 1. Verificar existencia e inactividad
    doc = db.query(Documento).filter(Documento.id == documento_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Documento no encontrado.")
    if doc.activo:
        raise HTTPException(
            status_code=409,
            detail="El documento está activo. Envíalo a la papelera antes de eliminarlo definitivamente.",
        )

    # 2. Verificar propiedad si es un usuario normal
    if usuario_solicitante_id is not None and doc.usuario_id != usuario_solicitante_id:
        raise HTTPException(
            status_code=403,
            detail="No tienes permiso para eliminar este documento. Solo puedes eliminar los archivos que tú subiste.",
        )

    nombre_storage = doc.nombre_storage

    # 3. Eliminar del bucket de Supabase
    supabase = _get_supabase()
    try:
        supabase.storage.from_(SUPABASE_BUCKET).remove([nombre_storage])
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Error al eliminar el archivo del almacenamiento: {exc}",
        )

    # 4. Eliminar el registro de PostgreSQL
    try:
        db.delete(doc)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="El archivo se eliminó del almacenamiento pero no se pudo borrar el registro. Contacte al administrador.",
        )

    return {"mensaje": f"Documento '{doc.nombre_original}' eliminado definitivamente."}
