from fastapi import FastAPI
from app.database import engine, Base, SessionLocal
from app.models.usuario import Usuario
from app.routes import usuarios, auth
from app.utils.security import hash_password

app = FastAPI()

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
                apellido="Temporal",
                email=admin_email,
                password=hash_password("admin1234"),
                rol="ADMIN",
                estado=True
            )
            db.add(nuevo_admin)
            db.commit()
    finally:
        db.close()

app.include_router(usuarios.router)
app.include_router(auth.router)

@app.get("/")
def root():
    return {"message": "VMDocs API funcionando"}