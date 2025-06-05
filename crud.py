# crud.py
import secrets
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

# Import ORM models, Pydantic schemas, and auth helpers
import models, schemas, auth, security

# --- User CRUD ---

def get_user(db: Session, user_id: UUID) -> Optional[models.User]:
    """Retrieve a single user by ID."""
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, email: str) -> Optional[models.User]:
    """Retrieve a single user by username."""
    # Assuming your User model uses 'username' field
    return db.query(models.User).filter(models.User.email == email).first()

# Example if you wanted get_users (not strictly needed for the shortener)
# def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.User]:
#     """Retrieve a list of users with pagination."""
#     return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """Create a new user in the database."""
    # Check if email already exists
    existing_email = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_email:
        raise ValueError("Email already registered")
        
    hashed_password = security.get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user) # Refresh to get the generated ID and defaults
    return db_user

# --- URL CRUD ---

def generate_random_key(length: int = 6) -> str:
    """Generates a unique random key (helper function)."""
    return secrets.token_urlsafe(length)

def create_db_url(db: Session, url: schemas.URLBase, owner_id: int) -> models.URL:
    """Creates a short URL entry in the database."""
    # Ensure key uniqueness
    while True:
        key = generate_random_key()
        existing_key = db.query(models.URL).filter(models.URL.key == key).first()
        if not existing_key:
            break

    # Ensure secret_key uniqueness
    while True:
        secret_key = f"{key}_{generate_random_key(8)}"
        existing_secret = db.query(models.URL).filter(models.URL.secret_key == secret_key).first()
        if not existing_secret:
            break

    # Create the ORM model instance
    db_url = models.URL(
        target_url=str(url.target_url), # Store Pydantic HttpUrl as string
        key=key,
        secret_key=secret_key,
        owner_id=owner_id
        # clicks, is_active, date_created have defaults in the model/table
    )
    db.add(db_url)
    db.commit()
    db.refresh(db_url) # Refresh to get generated ID and defaults
    return db_url

def get_db_url_by_key(db: Session, key: str) -> Optional[models.URL]:
    """Fetch a URL by its short key."""
    return db.query(models.URL).filter(models.URL.key == key).first()

def get_db_url_by_secret_key(db: Session, secret_key: str) -> Optional[models.URL]:
    """Fetch a URL by its secret key."""
    return db.query(models.URL).filter(models.URL.secret_key == secret_key).first()

def update_db_clicks(db: Session, db_url: models.URL) -> models.URL:
    """Increment the click count for a URL object."""
    # Assumes db_url is a valid, tracked ORM object
    db_url.clicks += 1
    db.add(db_url) # Add to session (might already be tracked)
    db.commit()
    db.refresh(db_url)
    return db_url

def deactivate_db_url(db: Session, db_url: models.URL) -> models.URL:
    """Deactivate a URL object."""
    # Assumes db_url is a valid, tracked ORM object
    db_url.is_active = False
    db.add(db_url)
    db.commit()
    db.refresh(db_url)
    return db_url

def delete_db_url(db: Session, db_url: models.URL) -> models.URL:
    """Delete a URL object from the database."""
    # Assumes db_url is a valid, tracked ORM object fetched previously
    db.delete(db_url)
    db.commit()
    # The object is deleted, returning it might be useful for confirmation
    # but it's detached from the session after commit.
    return db_url

# --- Combined Operations (Optional but can be useful) ---

def get_and_increment_clicks(db: Session, key: str) -> Optional[models.URL]:
    """Fetch URL by key and increment clicks if found and active."""
    db_url = get_db_url_by_key(db, key=key)
    if db_url and db_url.is_active:
        return update_db_clicks(db, db_url=db_url)
    return None # Return None if not found or inactive

def get_and_deactivate_url(db: Session, secret_key: str, owner_id: int) -> Optional[models.URL]:
    """Fetch URL by secret key, verify owner, and deactivate."""
    db_url = get_db_url_by_secret_key(db, secret_key=secret_key)
    if db_url and db_url.owner_id == owner_id:
        return deactivate_db_url(db, db_url=db_url)
    return None # Return None if not found or owner doesn't match

def get_and_delete_url(db: Session, secret_key: str, owner_id: int) -> Optional[models.URL]:
    """Fetch URL by secret key, verify owner, and delete."""
    db_url = get_db_url_by_secret_key(db, secret_key=secret_key)
    if db_url and db_url.owner_id == owner_id:
        return delete_db_url(db, db_url=db_url)
    return None # Return None if not found or owner doesn't match