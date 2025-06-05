from passlib.context import CryptContext
import secrets
import hashlib
from datetime import datetime, timedelta

# --- Password Hashing ---
PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto") # Single PWD_CONTEXT

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against a hashed password."""
    return PWD_CONTEXT.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hashes a plain password."""
    return PWD_CONTEXT.hash(password)

# --- Password Reset Token Utilities ---
def generate_secure_token(length=40):
    """Generates a cryptographically secure URL-safe text string."""
    return secrets.token_urlsafe(length)

def hash_token(token: str) -> str:
    """Hashes a token for storage (e.g., password reset token)."""
    return hashlib.sha256(token.encode()).hexdigest()

def create_password_reset_token_data(expires_delta: timedelta = timedelta(hours=1)):
    """
    Generates a raw token, its hashed version, and its expiry time
    for password reset purposes.
    """
    raw_token = generate_secure_token()
    hashed = hash_token(raw_token)
    expire = datetime.utcnow() + expires_delta
    return raw_token, hashed, expire