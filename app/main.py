from fastapi import FastAPI
from app.config import DATABASE_URL

app = FastAPI()

@app.get("/")
def root():
    return {
        "message": "VMDocs API funcionando",
        "database": DATABASE_URL
    }