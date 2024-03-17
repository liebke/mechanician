import bcrypt
bcrypt.__about__ = type("", (), {"__version__": bcrypt.__version__})

from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
from passlib.context import CryptContext
from mechanician_ui.secrets import SecretsManager
from zoneinfo import ZoneInfo


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_user(users_secrets: SecretsManager, username: str):
    user = users_secrets.get_secret(username)
    return user


def authenticate_user(users_secrets: SecretsManager, username: str, password: str):
    user = get_user(users_secrets, username)
    if not user:
        return False
    if not verify_password(password, user['hashed_password']):
        return False
    return user


def create_access_token(secrets_manager: SecretsManager, data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    # Get the current time in UTC
    current_time_utc = datetime.now(ZoneInfo("UTC"))
    # Calculate expiration time
    ACCESS_TOKEN_EXPIRE_MINUTES = int(secrets_manager.get_secret("ACCESS_TOKEN_EXPIRE_MINUTES"))
    expire = current_time_utc + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    SECRET_KEY = secrets_manager.get_secret("SECRET_KEY")
    ALGORITHM = secrets_manager.get_secret("ALGORITHM")
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt