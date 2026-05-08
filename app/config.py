import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("¡Falta configurar DATABASE_URL en el archivo .env!")

# Supabase
SUPABASE_URL    = os.getenv("SUPABASE_URL")
SUPABASE_KEY    = os.getenv("SUPABASE_KEY")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "vmdocs-documents")

# Documentos
TAMANO_MAXIMO_BYTES: int = int(os.getenv("TAMANO_MAXIMO_MB", "10")) * 1024 * 1024

TIPOS_MIME_PERMITIDOS: dict[str, str] = {
    ".pdf": "application/pdf",
    ".csv": "text/csv",
    ".doc": "application/msword",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
}

if not SUPABASE_URL or not SUPABASE_KEY:
    import warnings
    warnings.warn(
        "SUPABASE_URL o SUPABASE_KEY no están configurados. "
        "El módulo de documentos no estará disponible hasta que se definan en .env.",
        stacklevel=1,
    )

# Groq AI
GROQ_API_KEY:   str | None = os.getenv("GROQ_API_KEY")
GROQ_MODEL:     str        = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_MAX_CHARS: int = int(os.getenv("GROQ_MAX_CHARS", "15000"))

if not GROQ_API_KEY:
    import warnings
    warnings.warn(
        "GROQ_API_KEY no esta configurada. "
        "Los endpoints de IA (/ia/resumen, /ia/ficha, /ia/pregunta) no estaran disponibles.",
        stacklevel=1,
    )
