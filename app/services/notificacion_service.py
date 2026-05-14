from sqlalchemy.orm import Session
from app.models.notificacion_model import Notificacion, TipoNotificacion
from app.models.usuario import Usuario
from fastapi import HTTPException

def crear_notificacion(db: Session, usuario_id: int, tipo: TipoNotificacion, referencia_id: int, mensaje: str):
    """Crea una notificación para un usuario específico."""
    try:
        nueva_notificacion = Notificacion(
            usuario_id=usuario_id,
            tipo=tipo,
            referencia_id=referencia_id,
            mensaje=mensaje
        )
        db.add(nueva_notificacion)
        db.commit()
        db.refresh(nueva_notificacion)
        return nueva_notificacion
    except Exception as e:
        db.rollback()
        print(f"Error al crear notificación: {e}")
        return None

def notificar_a_administradores(db: Session, tipo: TipoNotificacion, referencia_id: int, mensaje: str):
    """Envía una notificación a todos los administradores activos."""
    admins = db.query(Usuario).filter(Usuario.rol == "ADMIN", Usuario.estado == True).all()
    for admin in admins:
        crear_notificacion(db, admin.id, tipo, referencia_id, mensaje)

def obtener_notificaciones(db: Session, usuario_id: int, limit: int = 50):
    """Obtiene las notificaciones de un usuario, ordenadas por fecha descendente."""
    total = db.query(Notificacion).filter(Notificacion.usuario_id == usuario_id).count()
    notificaciones = db.query(Notificacion)\
        .filter(Notificacion.usuario_id == usuario_id)\
        .order_by(Notificacion.fecha_creacion.desc())\
        .limit(limit)\
        .all()
    return total, notificaciones

def marcar_como_leida(db: Session, notificacion_id: int, usuario_id: int):
    """Marca una notificación específica como leída."""
    notificacion = db.query(Notificacion).filter(
        Notificacion.id == notificacion_id, 
        Notificacion.usuario_id == usuario_id
    ).first()
    
    if not notificacion:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")
    
    notificacion.leida = True
    db.commit()
    db.refresh(notificacion)
    return notificacion

def marcar_todas_como_leidas(db: Session, usuario_id: int):
    """Marca todas las notificaciones de un usuario como leídas."""
    db.query(Notificacion).filter(
        Notificacion.usuario_id == usuario_id, 
        Notificacion.leida == False
    ).update({"leida": True})
    db.commit()
    return {"mensaje": "Todas las notificaciones marcadas como leídas"}
