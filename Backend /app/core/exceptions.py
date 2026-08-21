from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import ValidationError
import structlog

logger = structlog.get_logger()


class AppException(Exception):
    def __init__(self, status_code: int, detail: str, errors: list = None):
        self.status_code = status_code
        self.detail = detail
        self.errors = errors or []
        super().__init__(detail)


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    logger.warning("app_exception", path=request.url.path, detail=exc.detail, errors=exc.errors)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "type": "https://tools.ietf.org/html/rfc7231#section-6.5.1",
            "title": "Application Error",
            "status": exc.status_code,
            "detail": exc.detail,
            "instance": str(request.url.path),
            "errors": exc.errors,
        },
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    logger.warning("http_exception", path=request.url.path, detail=exc.detail, status_code=exc.status_code)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "type": "https://tools.ietf.org/html/rfc7231#section-6.5.1",
            "title": "HTTP Error",
            "status": exc.status_code,
            "detail": exc.detail,
            "instance": str(request.url.path),
        },
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    errors = [
        {"field": ".".join(str(loc) for loc in e["loc"]), "message": e["msg"]}
        for e in exc.errors()
    ]
    logger.warning("validation_error", path=request.url.path, errors=errors)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "type": "https://tools.ietf.org/html/rfc7231#section-6.5.1",
            "title": "Validation Error",
            "status": 422,
            "detail": "Invalid input parameters",
            "instance": str(request.url.path),
            "errors": errors,
        },
    )


async def pydantic_validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
    errors = [
        {"field": ".".join(str(loc) for loc in e["loc"]), "message": e["msg"]}
        for e in exc.errors()
    ]
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "type": "https://tools.ietf.org/html/rfc7231#section-6.5.1",
            "title": "Validation Error",
            "status": 422,
            "detail": "Invalid input parameters",
            "instance": str(request.url.path),
            "errors": errors,
        },
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("unhandled_exception", path=request.url.path, error=str(exc))
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "type": "https://tools.ietf.org/html/rfc7231#section-6.6.1",
            "title": "Internal Server Error",
            "status": 500,
            "detail": "An unexpected error occurred",
            "instance": str(request.url.path),
        },
    )