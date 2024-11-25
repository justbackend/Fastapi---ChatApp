from typing import Any, Optional, Annotated
from annotated_types import MaxLen, MinLen
from pydantic import BaseModel, Field
from enum import Enum


class OAuth2PasswordRequestJSON(BaseModel):
    phone_number: str = Field(..., max_length=9, min_length=9)


class UserRole(str, Enum):
    DRIVER = "driver"
    CUSTOMER = "customer"
    DISPATCHER = "dispatcher"


class PhoneNumber(BaseModel):
    phone_number: str = Field(..., max_length=9, min_length=9)


class SmsCode(BaseModel):
    code: int = Field(gt=99999, lt=1000000)
    phone_number: Annotated[str, MaxLen(9), MinLen(9)]
    role: UserRole


class Token(BaseModel):
    access_token: str
    token_type: str


class PersonalInfoUpdate(BaseModel):
    phone_number2: Optional[str] = Field(None, max_length=9, min_length=9)
    telegram_username: Optional[str] = None


class LegalInfoCreate(BaseModel):
    accountant_name: Annotated[str, MaxLen(64)]
    accountant_number: Annotated[str, MaxLen(9), MinLen(9)]
    company_name: Annotated[str, MaxLen(255)]
    company_inn: int
    is_nds: bool = Field(default=False)


class ActivateSchema(BaseModel):
    code: str
    is_legal: bool