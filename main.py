"""
MindT2I - AI-Powered Image Generation Application (FastAPI)
============================================================

Modern async web application for AI-powered text-to-image generation.

Version: 2.0.0
Author: lycosa9527
Made by: MindSpring Team
License: AGPLv3

Features:
- Full async/await support for high-performance image generation
- FastAPI with Pydantic models for type safety
- Uvicorn ASGI server (Windows + Ubuntu compatible)
- Auto-generated OpenAPI documentation at /docs
- DashScope MultiModal API integration (Qwen Image Plus)
- Comprehensive logging, middleware, and business logic

Status: Production Ready
"""

import os
import sys
import io
import logging
import time
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create logs directory
os.makedirs("logs", exist_ok=True)

# Import config early
from config.settings import config

# ============================================================================
# EARLY LOGGING SETUP
# ============================================================================

log_level_str = config.LOG_LEVEL
log_level = getattr(logging, log_level_str, logging.INFO)


class UnifiedFormatter(logging.Formatter):
    """Unified logging formatter with ANSI color support"""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARN': '\033[33m',     # Yellow
        'ERROR': '\033[31m',    # Red
        'CRIT': '\033[35m',     # Magenta
        'RESET': '\033[0m',     # Reset
        'BOLD': '\033[1m',      # Bold
    }
    
    def format(self, record):
        timestamp = self.formatTime(record, '%H:%M:%S')
        
        level_map = {
            'DEBUG': 'DEBUG',
            'INFO': 'INFO',
            'WARNING': 'WARN',
            'ERROR': 'ERROR',
            'CRITICAL': 'CRIT'
        }
        level_name = level_map.get(record.levelname, record.levelname)
        
        color = self.COLORS.get(level_name, '')
        reset = self.COLORS['RESET']
        
        if level_name == 'CRIT':
            colored_level = f"{self.COLORS['BOLD']}{color}{level_name.ljust(5)}{reset}"
        else:
            colored_level = f"{color}{level_name.ljust(5)}{reset}"
        
        # Source abbreviation
        source = record.name
        if source == '__main__':
            source = 'MAIN'
        elif source.startswith('routers'):
            source = 'API'
        elif source == 'settings':
            source = 'CONF'
        elif source.startswith('uvicorn'):
            source = 'SRVR'
        elif source.startswith('clients'):
            source = 'CLIE'
        elif source.startswith('services'):
            source = 'SERV'
        else:
            source = source[:4].upper()
        
        source = source.ljust(4)
        
        return f"[{timestamp}] {colored_level} | {source} | {record.getMessage()}"


# Configure logging
unified_formatter = UnifiedFormatter()

# Use UTF-8 encoding for console output
console_handler = logging.StreamHandler(
    io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
)
console_handler.setFormatter(unified_formatter)

file_handler = logging.FileHandler(
    os.path.join("logs", "app.log"),
    encoding="utf-8"
)
file_handler.setFormatter(unified_formatter)

logging.basicConfig(
    level=log_level,
    handlers=[console_handler, file_handler],
    force=True
)

# Configure Uvicorn's loggers
for uvicorn_logger_name in ['uvicorn', 'uvicorn.error', 'uvicorn.access']:
    uvicorn_logger = logging.getLogger(uvicorn_logger_name)
    uvicorn_logger.handlers = []
    uvicorn_logger.addHandler(console_handler)
    uvicorn_logger.addHandler(file_handler)
    uvicorn_logger.propagate = False

# Create main logger
logger = logging.getLogger(__name__)

# Only log from main process
if os.getenv('UVICORN_WORKER_ID') is None:
    logger.debug(f"Logging initialized: {log_level_str}")

# ============================================================================
# FASTAPI APPLICATION IMPORTS
# ============================================================================

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

# ============================================================================
# LIFESPAN CONTEXT (Startup/Shutdown Events)
# ============================================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    Handles application initialization and cleanup.
    """
    # Startup
    app.state.start_time = time.time()
    app.state.is_shutting_down = False
    
    # Only log startup banner from first worker
    worker_id = os.getenv('UVICORN_WORKER_ID', '0')
    if worker_id == '0' or not worker_id:
        logger.info("=" * 80)
        logger.info("MindT2I FastAPI Application Starting")
        logger.info("=" * 80)
    
    # Ensure temp folder exists
    temp_folder = config.TEMP_FOLDER
    os.makedirs(temp_folder, exist_ok=True)
    if worker_id == '0' or not worker_id:
        logger.info(f"Temp folder initialized: {temp_folder}")
    
    # Cleanup old images on startup
    try:
        from services.image_service import image_service
        image_service.cleanup_old_images(max_age_hours=24)
        if worker_id == '0' or not worker_id:
            logger.info("Old images cleaned up")
    except Exception as e:
        if worker_id == '0' or not worker_id:
            logger.warning(f"Failed to cleanup old images: {e}")
    
    # Yield control to application
    try:
        yield
    finally:
        # Shutdown
        app.state.is_shutting_down = True
        
        if worker_id == '0' or not worker_id:
            logger.info("MindT2I shutting down gracefully")


# ============================================================================
# FASTAPI APPLICATION INITIALIZATION
# ============================================================================

app = FastAPI(
    title="MindT2I API",
    description="AI-Powered Text-to-Image Generation with FastAPI + DashScope",
    version=config.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# ============================================================================
# MIDDLEWARE CONFIGURATION
# ============================================================================

# CORS Middleware
if config.DEBUG:
    # Development: Allow multiple origins
    allowed_origins = [
        "http://localhost:3000",
        "http://localhost:9528",
        "http://127.0.0.1:9528"
    ]
else:
    # Production: Restrict to specific origins
    allowed_origins = [config.SERVER_URL]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GZip Compression
app.add_middleware(GZipMiddleware, minimum_size=1000)


# Custom Request/Response Logging Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests and responses with timing information"""
    start_time = time.time()
    
    logger.debug(f"Request: {request.method} {request.url.path} from {request.client.host}")
    
    # Process request
    response = await call_next(request)
    
    # Log response
    response_time = time.time() - start_time
    logger.debug(f"Response: {response.status_code} in {response_time:.3f}s")
    
    # Monitor slow requests
    if response_time > 5:
        logger.warning(f"Slow request: {request.method} {request.url.path} took {response_time:.3f}s")
    
    return response


# ============================================================================
# STATIC FILES
# ============================================================================

# Mount temp folders for images and videos
app.mount("/temp_images", StaticFiles(directory=config.TEMP_FOLDER), name="temp_images")
app.mount("/temp_videos", StaticFiles(directory="temp_videos"), name="temp_videos")

# ============================================================================
# GLOBAL EXCEPTION HANDLERS
# ============================================================================


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    logger.warning(f"HTTP {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions"""
    logger.error(f"Unhandled exception: {type(exc).__name__}: {exc}", exc_info=True)
    
    error_response = {"error": "An unexpected error occurred. Please try again later."}
    
    # Add debug info in development mode
    if config.DEBUG:
        error_response["debug"] = str(exc)
    
    return JSONResponse(
        status_code=500,
        content=error_response
    )


# ============================================================================
# BASIC ROUTES
# ============================================================================


@app.get("/")
async def root():
    """Root endpoint with API info"""
    return {
        "service": "MindT2I",
        "version": config.VERSION,
        "description": "AI-Powered Text-to-Image Generation API",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/status")
async def get_status():
    """Application status endpoint with metrics"""
    try:
        import psutil
        memory = psutil.virtual_memory()
        memory_percent = round(memory.percent, 1)
    except:
        memory_percent = 0.0
    
    uptime = time.time() - app.state.start_time if hasattr(app.state, 'start_time') else 0
    
    return {
        "status": "running",
        "framework": "FastAPI",
        "version": config.VERSION,
        "uptime_seconds": round(uptime, 1),
        "memory_percent": memory_percent,
        "timestamp": time.time()
    }


# ============================================================================
# ROUTER REGISTRATION
# ============================================================================

from routers import api_router

# Register routers
app.include_router(api_router)

# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    from utils.banner import print_banner, print_startup_info
    
    # Print ASCII banner
    print_banner()
    
    # Print startup information
    print_startup_info(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG
    )
    
    # Print configuration summary
    config.print_config_summary()
    
    try:
        # Run Uvicorn server
        uvicorn.run(
            "main:app",
            host=config.HOST,
            port=config.PORT,
            reload=config.DEBUG,  # Auto-reload in debug mode
            log_level="info",
            log_config=None,  # Use our custom logging configuration
        )
    except KeyboardInterrupt:
        # Graceful shutdown on Ctrl+C
        logger.info("=" * 80)
        logger.info("Shutting down gracefully...")
        logger.info("=" * 80)

