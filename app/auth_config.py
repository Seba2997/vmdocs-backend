import os
from dotenv import load_dotenv

load_dotenv()

# Variables obligatorias para JWT
SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    # Para desarrollo, si no hay SECRET_KEY, no dejamos que inicie para forzar seguridad
    raise ValueError("¡Falta configurar SECRET_KEY en el archivo .env!")

ALGORITHM = os.getenv("ALGORITHM", "HS256")

# Intentamos obtener el tiempo de expiración desde .env, si no, por defecto 60 minutos
try:
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
except ValueError:
    ACCESS_TOKEN_EXPIRE_MINUTES = 60
