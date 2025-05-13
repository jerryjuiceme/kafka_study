from typing import Callable, TypeAlias
import bcrypt
import jwt
from src.config import settings

from datetime import datetime, timedelta, timezone

Payload: TypeAlias = dict


def encode_jwt(
    payload: Payload,
    private_key: str = settings.authjwt.private_key_path.read_text(),
    algorithm: str = settings.authjwt.algorithm,
    expire_minutes: int = settings.authjwt.access_token_expire_minutes,
    expire_timedelta: timedelta | None = None,
) -> str | bytes:

    to_encode = payload.copy()
    now = datetime.now(timezone.utc)

    if expire_timedelta:
        expire = now + expire_timedelta
    else:
        expire = now + timedelta(minutes=expire_minutes)
    to_encode.update({"exp": expire, "iat": now})
    encoded = jwt.encode(payload=to_encode, key=private_key, algorithm=algorithm)
    return encoded


def decode_jwt(
    token: str | bytes,
    public_key: str = settings.authjwt.public_key_path.read_text(),
    algorithm: str = settings.authjwt.algorithm,
) -> Payload:
    decoded = jwt.decode(jwt=token, key=public_key, algorithms=[algorithm])
    return decoded


def hash_password(password: str) -> bytes:
    salt = bcrypt.gensalt()
    pwd_bytes: bytes = password.encode()
    return bcrypt.hashpw(pwd_bytes, salt)


def validate_password(password: str, hashed_password: bytes) -> bool:
    return bcrypt.checkpw(password=password.encode(), hashed_password=hashed_password)
