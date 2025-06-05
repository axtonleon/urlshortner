# routers.py
from fastapi import APIRouter, HTTPException, Depends, Request, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from sqlalchemy.orm import Session # Import Session
from typing import Optional

# Import schemas, ORM models, crud, auth, and db dependency
import schemas, models, crud, auth
from database import get_db # Import the DB session dependency
from auth import ACCESS_TOKEN_EXPIRE_MINUTES # Import config

# Create router instances
auth_router = APIRouter(
    tags=["Authentication & Users"] # Group endpoints in docs
)
url_router = APIRouter(
    tags=["URL Shortener & Management"] # Group endpoints in docs
)

# --- Authentication & User Endpoints ---

@auth_router.post("/register", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
async def register_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db) # Inject DB session
):
    """Registers a new user using synchronous ORM."""
    # Check username
    db_user = crud.get_user_by_username(db, email=user.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    try:
        # Call sync crud function, returns ORM model
        created_user = crud.create_user(db=db, user=user)
        # FastAPI automatically converts created_user (ORM model) to schemas.User
        return created_user
    except ValueError as e:
        if "Email already registered" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@auth_router.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db) # Inject DB session
):
    """Provides a JWT token for valid username and password using synchronous ORM."""
    # Authenticate user using sync auth function, returns ORM model or None
    user = auth.authenticate_user(db, username=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        # Use username from the authenticated ORM user model
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# get_current_active_user dependency now returns an ORM model (models.User)
# FastAPI will convert this ORM model to the schemas.User response_model
@auth_router.get("/users/me", response_model=schemas.User)
async def read_users_me(
    current_user: models.User = Depends(auth.get_current_active_user) # Dependency returns models.User
):
    """Gets the profile for the currently authenticated user."""
    return current_user


# --- URL Shortener & Management Endpoints ---

# get_current_active_user dependency returns models.User
@url_router.post("/url", response_model=schemas.URLInfo, status_code=status.HTTP_201_CREATED)
async def create_url(
    url: schemas.URLBase,
    current_user: models.User = Depends(auth.get_current_active_user), # Dependency returns models.User
    db: Session = Depends(get_db) # Inject DB session
):
    """Creates a short URL using synchronous ORM. Requires authentication."""
    # Call sync crud function, passing owner ID from ORM model
    db_url = crud.create_db_url(db=db, url=url, owner_id=current_user.id)
    # FastAPI automatically converts db_url (ORM model) to schemas.URLInfo
    return db_url


# Note: response_class handles the redirect directly
@url_router.get("/{short_key}", status_code=status.HTTP_307_TEMPORARY_REDIRECT, response_class=RedirectResponse)
async def forward_to_target_url(
    short_key: str,
    request: Request, # Keep request if needed for other purposes, otherwise optional
    db: Session = Depends(get_db) # Inject DB session
):
    """Redirects a short key to its original target URL using synchronous ORM."""
    # Use combined fetch and update function from crud
    db_url = crud.get_and_increment_clicks(db=db, key=short_key)

    if db_url:
        # Return the target URL string directly for RedirectResponse
        # Access target_url attribute from the ORM model
        return db_url.target_url
    else:
        # Handle cases where URL not found or is inactive (get_and_increment_clicks returns None)
        # Check if it exists but is inactive separately if needed for different message
        check_url = crud.get_db_url_by_key(db, key=short_key)
        if check_url and not check_url.is_active:
             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="URL is deactivated")
        else: # Not found at all
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Short URL not found")


# get_current_active_user dependency returns models.User
@url_router.get("/info/{secret_key}", response_model=schemas.URLInfo)
async def get_url_info(
    secret_key: str,
    current_user: models.User = Depends(auth.get_current_active_user), # Dependency returns models.User
    db: Session = Depends(get_db) # Inject DB session
):
    """Gets information and stats for a short URL using its secret key and sync ORM."""
    # Fetch URL using sync crud function
    db_url = crud.get_db_url_by_secret_key(db=db, secret_key=secret_key)

    if not db_url:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="URL not found")

    # Check ownership using ID from ORM models
    if db_url.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")

    # FastAPI automatically converts db_url (ORM model) to schemas.URLInfo
    return db_url


# get_current_active_user dependency returns models.User
@url_router.delete("/admin/{secret_key}", status_code=status.HTTP_200_OK)
async def deactivate_url(
    secret_key: str,
    current_user: models.User = Depends(auth.get_current_active_user), # Dependency returns models.User
    db: Session = Depends(get_db) # Inject DB session
):
    """Deactivates a short URL using its secret key and sync ORM."""
    # Use combined fetch, check owner, and deactivate function
    deactivated_url = crud.get_and_deactivate_url(db=db, secret_key=secret_key, owner_id=current_user.id)

    if not deactivated_url:
        # Check if URL exists at all to give specific error
        check_url = crud.get_db_url_by_secret_key(db, secret_key=secret_key)
        if not check_url:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="URL not found")
        else: # URL exists but owner doesn't match (should be caught by get_and_deactivate_url returning None)
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")

    return {"message": f"URL deactivated successfully"}


# Optional: Add delete endpoint using similar pattern
# @url_router.delete("/delete/{secret_key}", status_code=status.HTTP_200_OK)
# async def delete_url_permanently(
#     secret_key: str,
#     current_user: models.User = Depends(auth.get_current_active_user),
#     db: Session = Depends(get_db)
# ):
#     """Permanently deletes a short URL using its secret key and sync ORM."""
#     deleted_url = crud.get_and_delete_url(db=db, secret_key=secret_key, owner_id=current_user.id)
#     if not deleted_url:
#         # Add similar checks as deactivate_url for 404 vs 403
#         check_url = crud.get_db_url_by_secret_key(db, secret_key=secret_key)
#         if not check_url:
#              raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="URL not found")
#         else:
#             raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
#     return {"message": "URL deleted successfully"}

@url_router.get("/url/{short_key}", response_model=schemas.URLInfo)
async def get_url_details(
    short_key: str,
    db: Session = Depends(get_db)
):
    """Get full details of a shortened URL by its short key."""
    db_url = crud.get_db_url_by_key(db=db, key=short_key)
    if not db_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Short URL not found"
        )
    if not db_url.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="URL is deactivated"
        )
    return db_url

