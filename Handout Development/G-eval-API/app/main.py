"""
Main FastAPI application for Educator Feedback Quality Evaluation API.
This module creates and configures the FastAPI app instance.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

from .api import feedback
from .core import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage app startup and shutdown events.
    """
    logger.info("Starting Educator Feedback Quality API...")
    yield
    logger.info("Shutting down Educator Feedback Quality API...")


# Create FastAPI app with lifespan
app = FastAPI(
    title="Educator Feedback Quality Evaluation API",
    description="FastAPI service for evaluating the quality and effectiveness of educator feedback using LLM-based metrics",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Add CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Custom exception handler for validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """
    Handle Pydantic validation errors with detailed messages.
    """
    logger.error(f"Validation error: {exc}")
    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": exc.errors(),
            "message": "Request validation failed. Check the 'detail' field for specifics."
        },
    )


# Include routers
app.include_router(
    feedback.router,
    prefix="/api/v1/feedback",
    responses={
        400: {"description": "Bad Request"},
        422: {"description": "Validation Error"},
        500: {"description": "Internal Server Error"},
    },
)


@app.get("/", include_in_schema=False)
def root():
    """Root endpoint with API information."""
    return {
        "message": "Educator Feedback Quality Evaluation API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health")
def health_check():
    """
    Health check endpoint for monitoring.
    """
    logger.info("Health check requested")
    return {
        "status": "healthy",
        "service": "Educator Feedback Quality API",
        "version": "1.0.0",
    }


@app.get("/status")
def status_endpoint():
    """
    Detailed status endpoint.
    """
    return {
        "status": "online",
        "api_version": "1.0.0",
        "endpoints": [
            "/api/v1/feedback/evaluate-feedback",
            "/health",
            "/docs",
        ],
    }