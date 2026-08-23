from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette import status

from app.core.config import get_settings
from app.core.logging import setup_logging
from app.core.middleware import RequestContextMiddleware
from app.core.exceptions import (
    AppException,
    NotFoundError,
    AuthenticationError,
    AuthorizationError,
    ValidationError,
    ConflictError,
    ExternalServiceError
)

from app.api.health import router as health_router
from app.api.v1.router import api_v1_router

# Setup logging
setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Only start scheduler in non-serverless environments
    settings = get_settings()
    if settings.environment not in ("vercel",):
        try:
            from app.integrations.scheduler import start_scheduler, stop_scheduler
            start_scheduler()
            yield
            stop_scheduler()
        except ImportError:
            yield
    else:
        yield

# Create application
app = FastAPI(
    title="OmniTherm API",
    version="0.1.0",
    lifespan=lifespan
)

# Add Middlewares
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Add custom security headers middleware
app.add_middleware(RequestContextMiddleware)

# Include Routers
app.include_router(health_router)
app.include_router(api_v1_router)

# Exception Handlers
@app.exception_handler(NotFoundError)
async def not_found_error_handler(request: Request, exc: NotFoundError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"type": "about:blank", "title": "Not Found", "status": 404, "detail": str(exc)}
    )

@app.exception_handler(AuthenticationError)
async def authentication_error_handler(request: Request, exc: AuthenticationError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"type": "about:blank", "title": "Unauthorized", "status": 401, "detail": str(exc)}
    )

@app.exception_handler(AuthorizationError)
async def authorization_error_handler(request: Request, exc: AuthorizationError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"type": "about:blank", "title": "Forbidden", "status": 403, "detail": str(exc)}
    )

@app.exception_handler(ValidationError)
async def validation_error_handler(request: Request, exc: ValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"type": "about:blank", "title": "Unprocessable Entity", "status": 422, "detail": str(exc)}
    )

@app.exception_handler(ConflictError)
async def conflict_error_handler(request: Request, exc: ConflictError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"type": "about:blank", "title": "Conflict", "status": 409, "detail": str(exc)}
    )

@app.exception_handler(ExternalServiceError)
async def external_service_error_handler(request: Request, exc: ExternalServiceError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_502_BAD_GATEWAY,
        content={"type": "about:blank", "title": "Bad Gateway", "status": 502, "detail": str(exc)}
    )

@app.exception_handler(AppException)
async def app_error_handler(request: Request, exc: AppException) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"type": "about:blank", "title": "Internal Server Error", "status": 500, "detail": str(exc)}
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    import structlog
    logger = structlog.get_logger(__name__)
    logger.error("Unhandled server error", error=str(exc))
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"type": "about:blank", "title": "Internal Server Error", "status": 500, "detail": "An unexpected error occurred."}
    )
