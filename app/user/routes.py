import json
from datetime import timedelta
from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, Request, Path
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.auth import create_access_token, SessionDep, CurrentUser, Superuser, ActiveUser, credentials_exception
from app.config import settings
from app.database import get_db
from app.user.models import User

from app.user.functions import register, verify_phone_number_f, verify_sms_code_f, get_personal_info_f, \
    update_personal_info_f, activate_user_f, create_legal_info_f, get_unactive_users_f, activate_legal_user_f, \
    my_status_f
from app.user.schemas import PhoneNumber, SmsCode, OAuth2PasswordRequestJSON, Token, PersonalInfoUpdate, \
    LegalInfoCreate, ActivateSchema
from fastapi import HTTPException


router = APIRouter(
    prefix='/user'
)


# @user_router.post("/register")
# def register_endpoint(form: UserCreate, db: SessionDep):
#     access_token = register(form, db)
#     return {"access_token": access_token, "token_type": "bearer"}


@router.post("/verify-phone-number")
async def verify_phone_number(request: Request, form: PhoneNumber, db: AsyncSession = Depends(get_db)):
    response = await verify_phone_number_f(form, request, db)
    return response


@router.post('/verify-sms-code')
async def verify_sms_code(request: Request, form: SmsCode, db: AsyncSession = Depends(get_db)):
    response = await verify_sms_code_f(db, form, request)
    return response


@router.post("/token")
async def login_for_access_token(form: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    token_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    result = await db.execute(select(User).where(User.phone_number == form.username))
    user = result.scalars().first()

    if not user:
        raise token_exception
    if form.password != settings.ADMIN_PASSWORD:
        raise token_exception

    access_token = await create_access_token(data={"sub": user.phone_number})

    return Token(access_token=access_token, token_type="bearer")


@router.post("/token_docs")
async def login_for_access_token(form: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    token_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    result = await db.execute(select(User).where(User.phone_number == form.username))
    user = result.scalars().first()

    if not user:
        raise token_exception

    access_token = await create_access_token(data={"sub": user.phone_number})

    return Token(access_token=access_token, token_type="bearer")


@router.post('/login')
async def login_for_access_token(form: OAuth2PasswordRequestJSON, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.phone_number == form.phone_number))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = await create_access_token(data={"sub": str(user.id)})

    return {"access_token": access_token, "token_type": "bearer"}







@router.get('/inactive-legal-users')
async def get_unactive_users(current_user: Superuser, db: SessionDep):
    legal_unactive_users = await get_unactive_users_f(db)
    return legal_unactive_users





@router.get('/am-i-active')
async def am_i_active(current_user: CurrentUser, db: AsyncSession = Depends(get_db)):
    user_info = await my_status_f(current_user, db)
    return user_info


