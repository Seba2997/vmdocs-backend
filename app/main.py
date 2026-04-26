from fastapi import FastAPI
from app.database import engine, Base
from app.models.usuario import Usuario
from app.models import cliente_model, caso_model
from app.routes import usuarios, cliente_routes, caso_routes

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(usuarios.router)
app.include_router(cliente_routes.router)
app.include_router(caso_routes.router)

@app.get("/")
def root():
    return {"message": "VMDocs API funcionando"}