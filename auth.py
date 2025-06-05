import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import ValidationError # Good to catch this
from dotenv import load_dotenv
from sqlalchemy.orm import Session

# Import from your new central security.py
import security # Assuming security.py is in the same directory
import schemas, crud, models
from database import get_db

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

if not SECRET_KEY:
    raise ValueError("No SECRET_KEY set for JWT generation")
if not ALGORITHM: # Good to check ALGORITHM too
    raise ValueError("No ALGORITHM set for JWT generation")


# OAuth2 Scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token") 
# --- JWT Utilities ---
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "sub": to_encode.get("sub")}) # Ensure 'sub' is consistently used for username/id
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- Authentication Logic ---
def authenticate_user(db: Session, username: str, password: str) -> Optional[models.User]:
    user = crud.get_user_by_username(db, email=username)
    if not user:
        return None
    # Use verify_password from the security module
    if not security.verify_password(password, user.hashed_password):
        return None
    if not user.is_active: # Good check!
         return None
    return user

# --- Dependency for getting current user ---
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: Optional[str] = payload.get("sub")
        if username is None:
            raise credentials_exception
        # Validate payload against a Pydantic schema for robustness
        token_data = schemas.TokenData(email=username)
    except (JWTError, ValidationError): # Catch JWT errors and Pydantic validation errors
        raise credentials_exception

    user = crud.get_user_by_username(db, email=token_data.email)
 
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: models.User = Depends(get_current_user)
) -> models.User:
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user