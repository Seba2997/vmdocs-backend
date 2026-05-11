from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any
from datetime import datetime, timedelta

from app.database import get_db
from app.models.caso_model import Caso, FaseCaso
from app.models.cliente_model import Cliente
from app.models.documento_model import Documento
from app.models.usuario import Usuario
from app.services import caso_service
from app.routes.auth import obtener_usuario_actual_activo
from app.services import actividad_service

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/stats")
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obtener_usuario_actual_activo)
) -> Dict[str, Any]:
    
    # Obtener casos permitidos según el rol del usuario
    es_admin = current_user.rol == "ADMIN"
    casos_permitidos = caso_service.obtener_casos(db, usuario_id=current_user.id, es_admin=es_admin)
    casos_permitidos_ids = [c.id for c in casos_permitidos]
    
    # KPIs
    casos_activos = len(casos_permitidos)
    clientes_activos = db.query(Cliente).filter(Cliente.estado == True).count()
    casos_abiertos = sum(1 for c in casos_permitidos if c.estado == FaseCaso.abierto)
    casos_cerrados = sum(1 for c in casos_permitidos if c.estado == FaseCaso.cerrado)
    
    if casos_permitidos_ids:
        documentos_analizados = db.query(Documento).filter(
            Documento.resumen_ia.isnot(None),
            Documento.caso_id.in_(casos_permitidos_ids)
        ).count()
        
        # No buscamos documentos recientes aquí, lo haremos en la sección de actividad
    else:
        documentos_analizados = 0
    
    # Chart Data (Últimos 6 meses precisos)
    six_months_ago = datetime.now() - timedelta(days=180)
    
    chart_dict = {}
    meses_es = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
    
    today = datetime.now()
    for i in range(5, -1, -1):
        m = today.month - i
        y = today.year
        if m <= 0:
            m += 12
            y -= 1
        mes_str = meses_es[m - 1]
        key = f"{y}-{m:02d}"
        chart_dict[key] = {
            "mes": mes_str, 
            "abierto": 0, 
            "discusion": 0, 
            "conciliacion": 0, 
            "prueba": 0, 
            "impugnacion": 0, 
            "cerrado": 0
        }
            
    for c in casos_permitidos:
        # datetime needs to be naive or localized, assuming fecha_creacion is standard
        if c.fecha_creacion and c.fecha_creacion.replace(tzinfo=None) >= six_months_ago:
            key = f"{c.fecha_creacion.year}-{c.fecha_creacion.month:02d}"
            if key in chart_dict:
                estado_key = str(c.estado.value).lower()
                if estado_key in chart_dict[key]:
                    chart_dict[key][estado_key] += 1
                    
    chart_data = list(chart_dict.values())
    
    # ----------------------------------------------------
    # Actividad Reciente (desde la nueva tabla)
    # ----------------------------------------------------
    _, ultimas_actividades = actividad_service.obtener_actividades(db, current_user.id, es_admin, skip=0, limit=5)
    
    actividad = []
    for act in ultimas_actividades:
        fecha_str = act.fecha.strftime("%d/%m %H:%M")
        
        # Mapeo de estilos y enlaces según tipo de acción
        icon, bg, color, enlace = "info", "bg-gray-50", "text-gray-700", "/dashboard"
        
        if act.accion.value == "CREACION":
            if act.entidad_tipo == "Caso":
                icon, bg, color = "gavel", "bg-orange-50", "text-orange-700"
                enlace = f"/casos/{act.entidad_id}"
            elif act.entidad_tipo == "Cliente":
                icon, bg, color = "person_add", "bg-sky-50", "text-sky-700"
                enlace = "/clientes"
        elif act.accion.value == "SUBIDA":
            icon, bg, color = "upload_file", "bg-blue-50", "text-primary-container"
            enlace = f"/casos/{act.caso_id}?tab=docs" if act.caso_id else "/dashboard"
        elif act.accion.value == "ANALISIS_IA":
            icon, bg, color = "psychology", "bg-purple-50", "text-purple-700"
            enlace = f"/casos/{act.caso_id}?tab=docs" if act.caso_id else "/dashboard"
        elif act.accion.value == "ACTUALIZACION":
            icon, bg, color = "edit_document", "bg-emerald-50", "text-emerald-700"
            enlace = f"/casos/{act.caso_id}" if act.caso_id else "/dashboard"
        elif act.accion.value == "ELIMINACION":
            icon, bg, color = "delete", "bg-red-50", "text-red-700"
            enlace = f"/casos/{act.caso_id}?tab=docs" if act.caso_id else "/dashboard"
        elif act.accion.value == "ASIGNACION":
            icon, bg, color = "group_add", "bg-slate-50", "text-slate-700"
            enlace = f"/casos/{act.caso_id}?tab=usuarios" if act.caso_id else "/dashboard"
            
        # Nombre del usuario (solo lo incluimos si es admin para mayor privacidad o como meta de auditoría)
        usuario_nombre = f"{act.usuario.nombre} {act.usuario.apellido}" if act.usuario else "Sistema"
        
        actividad.append({
            "icon": icon,
            "iconBg": bg,
            "iconColor": color,
            "titulo": act.descripcion,
            "desc": f"{act.entidad_tipo} #{act.entidad_id}",
            "tiempo": fecha_str,
            "enlace": enlace,
            "usuario": usuario_nombre if es_admin else None
        })
        
    return {
        "kpis": {
            "casosActivos": casos_activos,
            "clientes": clientes_activos,
            "casosAbiertos": casos_abiertos,
            "casosCerrados": casos_cerrados,
            "documentosAnalizados": documentos_analizados
        },
        "chartData": chart_data,
        "actividadReciente": actividad
    }
