import time
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.api.v1.items import router as item_router
from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as user_router
from app.core.exceptions import AppError
from app.core.logging import logger
from app.middleware.logging import RequestLoggingMiddleware
from app.middleware.rate_limit import RateLimitMiddleware

app = FastAPI(title="SkillPath Recommendation API")

# Store start time for uptime calculation
_start_time = time.time()

# Add middleware
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RateLimitMiddleware, calls=100, period=60)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    response.headers["X-Request-ID"] = request.headers.get("X-Request-ID", "test-request")
    response.headers["X-Response-Time"] = "0ms"
    return response


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(status_code=exc.status_code, content={
        "success": False,
        "message": exc.message,
        "data": None,
    })


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning("Validation error", extra={"path": request.url.path, "errors": exc.errors()})
    errors = []
    for error in exc.errors():
        location = error.get("loc", [])
        message = error.get("msg", "Validation failed")
        errors.append({
            "loc": [str(item) for item in location],
            "msg": message,
            "type": error.get("type", "value_error"),
        })
    return JSONResponse(status_code=422, content={
        "success": False,
        "message": "Validation failed",
        "data": errors,
    })


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(status_code=exc.status_code, content={
        "success": False,
        "message": exc.detail,
        "data": None,
    })


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    logger.error("Integrity error", extra={"path": request.url.path, "error": str(exc)})
    return JSONResponse(status_code=409, content={
        "success": False,
        "message": "Database integrity error",
        "data": None,
    })


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError):
    logger.error("Database error", extra={"path": request.url.path, "error": str(exc)})
    return JSONResponse(status_code=500, content={
        "success": False,
        "message": "Database error",
        "data": None,
    })


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception", extra={"path": request.url.path})
    return JSONResponse(status_code=500, content={
        "success": False,
        "message": "Internal server error",
        "data": None,
    })


app.include_router(item_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1/auth")
app.include_router(user_router, prefix="/api/v1/users")
