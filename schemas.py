# schemas.py
from pydantic import BaseModel, HttpUrl, Field, UUID4, EmailStr, constr, StringConstraints
from typing import Optional, Annotated
from datetime import datetime

# --- User Schemas ---
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr = Field(..., description="Valid email address")

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

    class Config:
        json_schema_extra = {
            "example": {
                "username": "johndoe",
                "email": "john@example.com",
                "password": "strongpassword123"
            }
        }

class User(UserBase):
    id: UUID4
    is_active: bool
    date_created: datetime

    class Config:
        orm_mode = True # Allows mapping from ORM objects

# --- Token Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# --- URL Schemas ---
class URLBase(BaseModel):
    target_url: HttpUrl # Ensures it's a valid URL

class URLCreate(URLBase):
    pass

class URL(URLBase):
    id: UUID4
    key: str
    is_active: bool
    clicks: int
    owner_id: UUID4
    date_created: datetime

    class Config:
        orm_mode = True

class URLInfo(URL): # Includes the secret_key for management
    secret_key: str