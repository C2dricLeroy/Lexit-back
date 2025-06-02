from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def check_password(password: str, hashed_password: str) -> bool:
    """Check if a password matches its hashed version."""
    return pwd_context.verify(password, hashed_password)
