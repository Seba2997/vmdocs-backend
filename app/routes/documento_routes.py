from typing import List

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.usuario import Usuario
from app.schemas.documento_schema import (
    DocumentoDetalleResponse,
    DocumentoDescargaResponse,
)
from app.services import documento_service
from app.utils.jwt_security import requerir_rol, obtener_usuario_actual_activo

router = APIRouter(prefix="/documentos", tags=["Documentos"])


# --------------------------------------------------
# SUBIDA
# --------------------------------------------------

@router.post(
    "/subir/{caso_id}",
    response_model=DocumentoDetalleResponse,
    operation_id="subir_documento",
    summary="Subir documento",
    description=(
        "Sube un archivo (PDF, CSV, Word, Excel, JPG, PNG) al almacenamiento de Supabase "
        "y persiste su metadata en PostgreSQL. El usuario queda registrado como quien subio el archivo. "
        "ADMIN: acceso total. USER: solo si esta asignado al caso."
    ),
    status_code=201,
)
def subir_documento(
    caso_id: int,
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obtener_usuario_actual_activo),
):
    if current_user.rol != "ADMIN":
        documento_service.verificar_acceso_a_caso_o_403(db, current_user.id, caso_id)

    return documento_service.subir_documento(
        db=db,
        caso_id=caso_id,
        usuario_id=current_user.id,
        archivo=archivo,
    )


# --------------------------------------------------
# LISTADO
# --------------------------------------------------

@router.get(
    "/caso/{caso_id}",
    response_model=List[DocumentoDetalleResponse],
    operation_id="listar_documentos_por_caso",
    summary="Listar documentos activos de un caso",
    description=(
        "Retorna los documentos activos de un caso activo, ordenados por fecha de subida. "
        "ADMIN: acceso total. USER: solo si esta asignado al caso."
    ),
)
def listar_documentos_por_caso(
    caso_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obtener_usuario_actual_activo),
):
    if current_user.rol != "ADMIN":
        documento_service.verificar_acceso_a_caso_o_403(db, current_user.id, caso_id)

    return documento_service.obtener_documentos_por_caso(db, caso_id)


@router.get(
    "/caso/{caso_id}/papelera",
    response_model=List[DocumentoDetalleResponse],
    operation_id="listar_documentos_inactivos_por_caso",
    summary="Listar documentos inactivos (papelera) de un caso",
    description=(
        "Retorna los documentos que fueron eliminados logicamente (inactivos) de un caso. "
        "La papelera es especifica por caso: solo muestra los documentos inactivos de ese caso. "
        "ADMIN: acceso total. USER: solo si esta asignado al caso."
    ),
)
def listar_documentos_inactivos_por_caso(
    caso_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obtener_usuario_actual_activo),
):
    if current_user.rol != "ADMIN":
        documento_service.verificar_acceso_a_caso_o_403(db, current_user.id, caso_id)

    return documento_service.obtener_documentos_inactivos_por_caso(db, caso_id)


# --------------------------------------------------
# OBTENER POR ID
# --------------------------------------------------

@router.get(
    "/{documento_id}",
    response_model=DocumentoDetalleResponse,
    operation_id="obtener_documento_por_id",
    summary="Obtener metadata de un documento",
    description=(
        "Retorna la metadata de un documento activo por ID. "
        "ADMIN: acceso total. USER: solo si esta asignado al caso del documento."
    ),
)
def obtener_documento(
    documento_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obtener_usuario_actual_activo),
):
    doc = documento_service.obtener_documento_por_id(db, documento_id)

    if current_user.rol != "ADMIN":
        documento_service.verificar_acceso_a_caso_o_403(db, current_user.id, doc.caso_id)

    return doc


# --------------------------------------------------
# DESCARGA (signed URL)
# --------------------------------------------------

@router.get(
    "/descargar/{documento_id}",
    response_model=DocumentoDescargaResponse,
    operation_id="descargar_documento",
    summary="Obtener URL temporal (ver/descargar)",
    description=(
        "Genera una signed URL temporal de Supabase Storage (valida 5 minutos). "
        "Acepta un query parameter ?modo=descargar (por defecto) o ?modo=ver. "
        "No expone URLs publicas permanentes. "
        "ADMIN: acceso total. USER: solo si esta asignado al caso del documento."
    ),
)
def descargar_documento(
    documento_id: int,
    modo: str = "descargar",
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obtener_usuario_actual_activo),
):
    doc = documento_service.obtener_documento_por_id(db, documento_id)

    if current_user.rol != "ADMIN":
        documento_service.verificar_acceso_a_caso_o_403(db, current_user.id, doc.caso_id)

    return documento_service.generar_signed_url(db, documento_id, modo)


# --------------------------------------------------
# SOFT DELETE / PAPELERA (toggle)
# --------------------------------------------------

@router.patch(
    "/switch/{documento_id}",
    status_code=200,
    operation_id="toggle_estado_documento",
    summary="Enviar a papelera / Restaurar documento",
    description=(
        "Cambia el campo 'activo' del documento de forma alternada (toggle). "
        "Si esta activo lo envia a la papelera del caso (activo=False); si esta en papelera lo restaura. "
        "ADMIN: puede hacer toggle de cualquier documento. "
        "USER: solo puede gestionar los documentos que el mismo subio y debe estar asignado al caso."
    ),
)
def toggle_estado_documento(
    documento_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obtener_usuario_actual_activo),
):
    # ADMIN sin restriccion de propiedad; USER solo puede gestionar sus propios archivos
    usuario_solicitante_id = None if current_user.rol == "ADMIN" else current_user.id

    # USER debe estar asignado al caso del documento (funciona aunque esté en papelera)
    if current_user.rol != "ADMIN":
        doc = documento_service.obtener_documento_cualquier_estado(db, documento_id)
        documento_service.verificar_acceso_a_caso_o_403(db, current_user.id, doc.caso_id)

    return documento_service.toggle_estado_documento(db, documento_id, usuario_solicitante_id)


# --------------------------------------------------
# ELIMINACION DEFINITIVA
# --------------------------------------------------

@router.delete(
    "/{documento_id}/permanente",
    status_code=200,
    operation_id="eliminar_documento_definitivamente",
    summary="Eliminar documento definitivamente",
    description=(
        "Elimina de forma IRREVERSIBLE un documento que ya se encuentre en la papelera "
        "(activo=False). Borra el archivo del bucket de Supabase y el registro de la base de datos. "
        "ADMIN: puede eliminar cualquier documento en papelera. "
        "USER: solo puede eliminar los documentos que el mismo subio (y que esten en papelera). "
        "Si el documento aun esta activo, devuelve 409."
    ),
)
def eliminar_documento_definitivamente(
    documento_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obtener_usuario_actual_activo),
):
    # ADMIN no tiene restriccion de propiedad; USER solo puede eliminar sus propios archivos
    usuario_solicitante_id = None if current_user.rol == "ADMIN" else current_user.id

    # USER debe estar asignado al caso del documento (funciona aunque esté en papelera)
    if current_user.rol != "ADMIN":
        doc = documento_service.obtener_documento_cualquier_estado(db, documento_id)
        documento_service.verificar_acceso_a_caso_o_403(db, current_user.id, doc.caso_id)

    return documento_service.eliminar_definitivamente(db, documento_id, usuario_solicitante_id)
