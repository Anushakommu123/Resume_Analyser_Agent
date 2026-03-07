"""
FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import uvicorn

from app.config import settings
from app.database import db
from app.routers import resume

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Agentic RAG Test Generator - Three-agent system for generating unit tests",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(resume.router)


@app.on_event("startup")
async def startup_event():
    """Initialize database connection on startup."""
    logger.info("=" * 60)
    logger.info("Starting Testing Agents API...")
    logger.info("=" * 60)
    
    # Attempt MongoDB connection
    connected = await db.connect(raise_on_error=False)
    
    if connected:
        logger.info("=" * 60)
        logger.info("✓ Application started successfully with MongoDB connection")
        logger.info("✓ RAG features are ENABLED")
        logger.info("=" * 60)
    else:
        logger.warning("=" * 60)
        logger.warning("⚠ Application started WITHOUT MongoDB connection")
        logger.warning("⚠ RAG features are DISABLED")
        logger.warning("⚠ To enable RAG:")
        logger.warning("   1. Ensure MongoDB is running")
        logger.warning("   2. Check MONGODB_URI in .env file")
        logger.warning("   3. Use POST /api/v1/mongodb/reconnect to retry connection")
        logger.warning("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown."""
    try:
        await db.disconnect()
        logger.info("Application shutdown complete")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Testing Agents API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/favicon.ico")
async def favicon():
    """Favicon endpoint to prevent 404 errors."""
    from fastapi.responses import Response
    return Response(status_code=204)  # No Content


if __name__ == "__main__":
    port = settings.port
    max_attempts = 10
    for attempt in range(max_attempts):
        try:
            uvicorn.run(
                "main:app",
                host="0.0.0.0",
                port=port,
                reload=settings.debug,
                log_level="info"
            )
            break
        except OSError as e:
            if e.errno == 10048 or (hasattr(e, "winerror") and e.winerror == 10048):
                if attempt < max_attempts - 1:
                    port += 1
                    logger.warning(f"Port {port - 1} in use, trying port {port}...")
                else:
                    logger.error(f"Could not bind to any port from {settings.port} to {port}. Stop other processes using these ports.")
                    raise
            else:
                raise

