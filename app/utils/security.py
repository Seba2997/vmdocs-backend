import bcrypt

def _normalize_password(password: str) -> bytes:
    """
    Convierte el password a bytes y aplica el límite de 72 bytes de bcrypt.
    """
    pwd_bytes = password.encode("utf-8")
    return pwd_bytes[:72]


def hash_password(password: str) -> str:
    pwd_bytes = _normalize_password(password)
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    pwd_bytes = _normalize_password(plain_password)
    hash_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(pwd_bytes, hash_bytes)