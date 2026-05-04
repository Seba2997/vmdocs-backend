from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base, SessionLocal
from app.models.usuario import Usuario, RolUsuario
from app.utils.security import hash_password
from app.models import cliente_model, caso_model, caso_usuario_model
from app.routes import usuarios, auth, cliente_routes, caso_routes

app = FastAPI()

# Orígenes permitidos — agregar la URL de producción del frontend cuando se despliegue
ORIGINES_PERMITIDOS = [
    "http://localhost:5173",  # Vite dev server
    "http://localhost:8000",  # Swagger local
    "http://127.0.0.1:8000",  # Swagger local alternativo
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINES_PERMITIDOS,
    allow_credentials=True,  # necesario para enviar el header Authorization con el JWT
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

#Usuario ADMIN temporal para pruebas
@app.on_event("startup")
def create_admin_user():
    db = SessionLocal()
    try:
        admin_email = "admin@email.com"
        admin_user = db.query(Usuario).filter(Usuario.email == admin_email).first()
        if not admin_user:
            nuevo_admin = Usuario(
                nombre="Admin",
                apellido="Maestro",
                email=admin_email,
                password=hash_password("Admin123*"),
                rol=RolUsuario.ADMIN,
                estado=True
            )
            db.add(nuevo_admin)
            db.commit()
    finally:
        db.close()

app.include_router(usuarios.router)
app.include_router(auth.router)
app.include_router(cliente_routes.router)
app.include_router(caso_routes.router)

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")