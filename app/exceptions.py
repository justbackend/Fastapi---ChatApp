from typing import Any, Optional, Dict, Annotated

from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder


class CustomException(HTTPException):
    def __init__(self, detail: Any,  status_code: int = 400, **kwargs: Dict):

        super().__init__(detail=detail, status_code=status_code, **kwargs)


class NotFoundException(CustomException):
    def __init__(self, detail: Any, status_code: int = 404, **kwargs: Dict):

        super().__init__(detail=detail, status_code=status_code, **kwargs)
