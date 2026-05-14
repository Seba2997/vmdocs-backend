from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routes import usuarios, auth, cliente_routes, caso_routes, documento_routes, ia_routes, actividad_routes, password_reset_routes, dashboard_routes, notificacion_routes

app = FastAPI()

# Orígenes permitidos (CORS)
ORIGINES_PERMITIDOS = [
    "http://localhost:5173",  # Vite dev server
    "http://localhost:8000",  # Swagger local
    "http://127.0.0.1:8000",  # Swagger local alternativo
    "https://vmdocs-frontend.vercel.app", # Despliegue en vercel
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINES_PERMITIDOS,
    allow_credentials=True,  # necesario para enviar el header Authorization con el JWT
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)



app.include_router(usuarios.router)
app.include_router(auth.router)
app.include_router(cliente_routes.router)
app.include_router(caso_routes.router)
app.include_router(documento_routes.router)
app.include_router(ia_routes.router)
app.include_router(actividad_routes.router)
app.include_router(password_reset_routes.router)
app.include_router(dashboard_routes.router)
app.include_router(notificacion_routes.router)


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")
