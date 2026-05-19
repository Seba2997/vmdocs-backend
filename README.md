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

## Requisitos previos

- Python 3.11 o superior
- Una instancia de PostgreSQL accesible (se usa Supabase por defecto)
- Un bucket configurado en Supabase Storage
- Credenciales de Groq API para las funciones de IA (opcional)
- Credenciales SMTP para recuperacion de contrasena (opcional)

## Instalacion

1. Clonar el repositorio:

```
git clone <url-del-repositorio>
cd vmdocs-backend
```

2. Crear y activar un entorno virtual:

```
python -m venv venv
venv\Scripts\activate       # Windows
source venv/bin/activate    # Linux / macOS
```

3. Instalar dependencias:

```
pip install -r requirements.txt
```

4. Configurar las variables de entorno (ver seccion siguiente).

## Variables de entorno

Crear un archivo `.env` en la raiz del proyecto con los siguientes valores:

```
# Base de datos
DATABASE_URL=postgresql://<usuario>:<contrasena>@<host>:<puerto>/postgres

# Supabase
SUPABASE_URL=https://<proyecto>.supabase.co
SUPABASE_KEY=<service-role-key>
SUPABASE_BUCKET=vmdocs-documents

# JWT
SECRET_KEY=<clave-secreta-aleatoria>
ACCESS_TOKEN_EXPIRE_MINUTES=720

# Documentos
TAMANO_MAXIMO_MB=50

# Groq AI (opcional)
GROQ_API_KEY=<clave-groq>
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_MAX_CHARS=15000

# SMTP - Recuperacion de contrasena (opcional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=<correo>
SMTP_PASSWORD=<contrasena-de-aplicacion>
```

Si `GROQ_API_KEY` o las credenciales de Supabase no estan definidas, el servidor iniciara con advertencias y esos modulos quedaran deshabilitados.

## Ejecutar el servidor

```
uvicorn app.main:app --reload
```

El servidor queda disponible en `http://localhost:8000`.  
La documentacion interactiva (Swagger UI) se encuentra en `http://localhost:8000/docs`.

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
