import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("¡Falta configurar DATABASE_URL en el archivo .env!")

# ── Supabase Storage ────────────────────────────────────────────────────────
SUPABASE_URL    = os.getenv("SUPABASE_URL")
SUPABASE_KEY    = os.getenv("SUPABASE_KEY")
# El bucket puede sobreescribirse via .env; si no está definido usa el valor por defecto.
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "vmdocs-documents")

# ── Módulo de documentos ─────────────────────────────────────────────────────
# Tamaño máximo permitido por archivo (por defecto 10 MB).
TAMANO_MAXIMO_BYTES: int = int(os.getenv("TAMANO_MAXIMO_MB", "10")) * 1024 * 1024

# MIME types aceptados → clave: extensión, valor: MIME type
TIPOS_MIME_PERMITIDOS: dict[str, str] = {
    ".pdf": "application/pdf",
    ".csv": "text/csv",
}

if not SUPABASE_URL or not SUPABASE_KEY:
    import warnings
    warnings.warn(
        "SUPABASE_URL o SUPABASE_KEY no están configurados. "
        "El módulo de documentos no estará disponible hasta que se definan en .env.",
        stacklevel=1,
    )