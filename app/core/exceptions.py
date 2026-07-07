class AppError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class DatabaseException(AppError):
    def __init__(self, message: str = "Database operation failed"):
        super().__init__(message, status_code=500)


class NotFoundException(AppError):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)


class ValidationException(AppError):
    def __init__(self, message: str = "Validation failed"):
        super().__init__(message, status_code=422)


class UnauthorizedException(AppError):
    def __init__(self, message: str = "Unauthorized access"):
        super().__init__(message, status_code=401)
