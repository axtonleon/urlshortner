# main.py
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import logging

# Import connection handlers and router instances
from routers import auth_router, url_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="URL Shortener API",
    description="A simple URL shortener service with authentication (Router Version).",
    version="0.2.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# --- Include Routers ---
app.include_router(auth_router)
app.include_router(url_router)

# --- Root Endpoint ---
@app.get("/", tags=["Root"])
async def read_root():
    return RedirectResponse("/docs")