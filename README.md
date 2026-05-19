# VMDocs Backend

API REST para la plataforma VMDocs, un sistema de gestion documental orientado a estudios juridicos. Permite administrar clientes, casos, documentos, usuarios y actividades, con soporte para asistencia por IA.

## Tecnologias

- Python 3.11+
- FastAPI
- SQLAlchemy 2.0 (ORM)
- PostgreSQL via Supabase
- Supabase Storage (almacenamiento de documentos)
- Groq API con modelo LLaMA 3.3 (asistencia por IA)
- Uvicorn (servidor ASGI)
- PyJWT + Passlib (autenticacion y hashing)



## Entorno Local con Docker Compose (Para Revisores/Profesores)

Para facilitar la evaluación del proyecto en un entorno local y autocontenido (sin depender de servicios externos), se ha configurado un entorno de Docker.

### Requisitos
- Docker y Docker Desktop / Compose instalados.
- Ambos repositorios (`vmdocs-backend` y `vmdocs-frontend`) clonados en la **misma carpeta padre**.

### Instrucciones paso a paso

1. Clonar ambos repositorios en la misma ubicación:
```bash
# Crear y entrar a una carpeta base
mkdir vmdocs-proyecto && cd vmdocs-proyecto

# Clonar repositorios (reemplaza 'tu-usuario' por tu usuario real de Github)
git clone https://github.com/tu-usuario/vmdocs-frontend.git
git clone https://github.com/tu-usuario/vmdocs-backend.git
```

2. Cambiar a la rama de pruebas (`testing`) en ambos repositorios:
```bash
cd vmdocs-backend && git checkout testing
cd ../vmdocs-frontend && git checkout testing
cd ../vmdocs-backend
```

3. Levantar los contenedores:
```bash
docker compose up --build -d
```

Una vez finalizado, la plataforma estará lista en:
- **Frontend (Web)**: http://localhost:5173
- **Backend (API Docs)**: http://localhost:8000/docs

La base de datos local (PostgreSQL) se inicializará automáticamente con usuarios y datos de demostración:
- **Admin**: `admin@vmdocs.com` / `admin1234`
- **Abogado**: `abogado@vmdocs.com` / `abogado1234`

## Estructura del proyecto

```
vmdocs-backend/
├── app/
│   ├── main.py              # Punto de entrada, registro de routers y middleware
│   ├── config.py            # Carga y validacion de variables de entorno
│   ├── database.py          # Configuracion de SQLAlchemy y sesion de base de datos
│   ├── auth_config.py       # Configuracion de autenticacion JWT
│   ├── models/              # Modelos ORM (tablas de la base de datos)
│   ├── schemas/             # Esquemas Pydantic (validacion de entrada y salida)
│   ├── routes/              # Routers de FastAPI por modulo
│   ├── services/            # Logica de negocio desacoplada de las rutas
│   └── utils/               # Funciones auxiliares reutilizables
├── requirements.txt
└── .env                     # No incluido en el repositorio
```

## Modulos de la API

| Prefijo        | Descripcion                                          |
|----------------|------------------------------------------------------|
| `/auth`        | Inicio de sesion y emision de tokens JWT             |
| `/usuarios`    | Gestion de usuarios y roles (admin / abogado)        |
| `/clientes`    | Alta, consulta y actualizacion de clientes           |
| `/casos`       | Gestion de casos y asignacion de usuarios            |
| `/documentos`  | Carga, descarga y eliminacion de documentos          |
| `/ia`          | Resumen, extraccion de ficha y preguntas sobre docs  |
| `/actividad`   | Registro de auditoria de acciones                    |
| `/dashboard`   | Metricas y estadisticas generales                    |
| `/notificaciones` | Consulta y marcado de notificaciones              |
| `/password-reset` | Solicitud y confirmacion de recuperacion de clave |

## Tipos de archivo permitidos

PDF, CSV, DOC, DOCX, XLSX, PNG, JPG/JPEG. El tamano maximo por archivo se controla con la variable `TAMANO_MAXIMO_MB` (por defecto 50 MB).

## Autenticacion

Todos los endpoints protegidos requieren un token JWT en el encabezado:

```
Authorization: Bearer <token>
```

El token se obtiene mediante `POST /auth/login` con las credenciales del usuario.

## Contribucion

1. Crear una rama a partir de `main` con un nombre descriptivo.
2. Hacer los cambios y verificar que el servidor inicie sin errores.
3. Abrir un pull request describiendo los cambios realizados.

No se deben commitear archivos `.env`, claves privadas ni secretos de ninguna clase. El archivo `.gitignore` ya esta configurado para excluirlos.
