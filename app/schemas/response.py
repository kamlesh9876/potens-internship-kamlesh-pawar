from pydantic import BaseModel, ConfigDict
from typing import Any, Optional


class ApiResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    success: bool
    message: str
    data: Optional[Any] = None


class ErrorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    success: bool = False
    message: str
    data: Optional[Any] = None
