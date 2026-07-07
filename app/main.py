from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.api.routes import router
from app.core.exceptions import AppError
from app.core.logging import logger

app = FastAPI(title="SkillPath Recommendation API")


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
    return JSONResponse(status_code=422, content={
        "success": False,
        "message": "Validation failed",
        "data": exc.errors(),
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


app.include_router(router)
