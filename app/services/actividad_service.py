from sqlalchemy.orm import Session, joinedload
from app.models.actividad_model import Actividad, AccionActividad
from app.models.caso_usuario_model import CasoUsuario

def registrar_actividad(
    db: Session, 
    usuario_id: int, 
    accion: AccionActividad, 
    entidad_tipo: str, 
    entidad_id: int, 
    descripcion: str, 
    caso_id: int = None, 
    detalles: str = None
):
    """
    Registra una acción en el log de auditoría.
    """
    try:
        actividad = Actividad(
            usuario_id=usuario_id,
            accion=accion,
            entidad_tipo=entidad_tipo,
            entidad_id=entidad_id,
            caso_id=caso_id,
            descripcion=descripcion,
            detalles=detalles
        )
        db.add(actividad)
        db.commit()
        db.refresh(actividad)
        return actividad
    except Exception as e:
        db.rollback()
        # Fallback silencioso para no romper la app principal por un log fallido
        print(f"Error al registrar actividad: {e}")
        return None

def obtener_actividades(db: Session, usuario_id: int, es_admin: bool, skip: int = 0, limit: int = 20):
    """
    Retorna el historial de actividades.
    Filtra por RBAC: ADMIN ve todo, Usuario ve solo las suyas.
    """
    query = db.query(Actividad).options(joinedload(Actividad.usuario))
    
    if not es_admin:
        query = query.filter(Actividad.usuario_id == usuario_id)
        
    total = query.count()
    actividades = query.order_by(Actividad.fecha.desc()).offset(skip).limit(limit).all()
    
    return total, actividades
