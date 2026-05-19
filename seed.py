"""
seed.py - Datos de demo para el entorno de testing.

Se ejecuta una sola vez al arrancar el contenedor.
Si los datos ya existen, no hace nada (idempotente).
"""

import os
import sys

# Asegurar que el path incluye /app para importar los modulos del proyecto
sys.path.insert(0, "/app")

from passlib.context import CryptContext
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.usuario import Usuario, RolUsuario
from app.models.cliente_model import Cliente, TipoCliente
from app.models.caso_model import Caso, FaseCaso
from app.models.caso_usuario_model import CasoUsuario
from app.models.documento_model import Documento
from app.models.notificacion_model import Notificacion
from app.models.actividad_model import Actividad

DATABASE_URL = os.environ["DATABASE_URL"]
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


def run():
    # Crear todas las tablas (SQLAlchemy las genera si no existen)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Si ya existe el admin, el seed ya se ejecuto antes
        if db.query(Usuario).filter(Usuario.email == "admin@vmdocs.com").first():
            print("[seed] Datos ya existentes, omitiendo.")
            return

        # ── Usuarios ────────────────────────────────────────────────────────
        admin = Usuario(
            nombre="Admin",
            apellido="Demo",
            email="admin@vmdocs.com",
            password=hash_password("admin1234"),
            rol=RolUsuario.ADMIN,
            estado=True,
        )
        abogado = Usuario(
            nombre="Ana",
            apellido="Abogada",
            email="abogado@vmdocs.com",
            password=hash_password("abogado1234"),
            rol=RolUsuario.USER,
            estado=True,
        )
        db.add_all([admin, abogado])
        db.flush()  # genera los IDs sin hacer commit aun

        # ── Clientes ────────────────────────────────────────────────────────
        cliente1 = Cliente(
            tipo=TipoCliente.PERSONA,
            nombre="Juan",
            apellido="Perez",
            rut="12345678-9",
            email="juan.perez@demo.com",
            telefono="+56 9 1234 5678",
            ciudad="Santiago",
            created_by=admin.id,
        )
        cliente2 = Cliente(
            tipo=TipoCliente.EMPRESA,
            nombre="Empresa",
            razon_social="Empresa Ejemplo SpA",
            rut="76543210-K",
            email="contacto@empresa-demo.com",
            telefono="+56 2 2222 3333",
            ciudad="Valparaiso",
            created_by=admin.id,
        )
        db.add_all([cliente1, cliente2])
        db.flush()

        # ── Casos ───────────────────────────────────────────────────────────
        caso1 = Caso(
            titulo="Juicio laboral - Juan Perez vs Empresa ABC",
            descripcion="Demanda por despido injustificado y cobro de prestaciones.",
            numero_rol="T-1234-2024",
            tribunal="Juzgado de Letras del Trabajo de Santiago",
            materia="Laboral",
            prioridad="ALTA",
            estado=FaseCaso.discusion,
            cliente_id=cliente1.id,
            created_by=admin.id,
        )
        caso2 = Caso(
            titulo="Contrato de arrendamiento - Empresa Ejemplo SpA",
            descripcion="Revision y redaccion de contrato de arrendamiento comercial.",
            numero_rol="C-5678-2024",
            tribunal="Tribunal Civil de Valparaiso",
            materia="Civil",
            prioridad="MEDIA",
            estado=FaseCaso.abierto,
            cliente_id=cliente2.id,
            created_by=abogado.id,
        )
        db.add_all([caso1, caso2])
        db.flush()

        # ── Asignaciones caso-usuario ────────────────────────────────────────
        db.add_all([
            CasoUsuario(caso_id=caso1.id, usuario_id=admin.id),
            CasoUsuario(caso_id=caso1.id, usuario_id=abogado.id),
            CasoUsuario(caso_id=caso2.id, usuario_id=abogado.id),
        ])

        db.commit()
        print("[seed] Datos de demo creados exitosamente.")
        print("[seed]   admin@vmdocs.com     / admin1234")
        print("[seed]   abogado@vmdocs.com   / abogado1234")

    except Exception as exc:
        db.rollback()
        print(f"[seed] ERROR: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run()
