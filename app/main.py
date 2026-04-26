from fastapi import FastAPI
from app.database import engine, Base
from app.models.usuario import Usuario
from app.routes import usuarios, auth

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(usuarios.router)
app.include_router(auth.router)

@app.get("/")
def root():
    return {"message": "VMDocs API funcionando"}