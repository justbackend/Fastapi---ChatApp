import os
from datetime import datetime, timedelta
from typing import Any, Optional

from jose import jwt, JWTError
from sqladmin.authentication import AuthenticationBackend
from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from sqladmin import ModelView

from starlette.requests import Request

from app.auth import pwd_context, create_access_token, get_user_from_token
from app.config import settings
from app.exceptions import CustomException
from app.user.models import User
from .database import AsyncSessionFactory



# from schemas.tokens import TokenData


class UserAdmin(ModelView, model=User):
    column_list = "__all__"





def admin_panel_apply(admin):
    admin.add_view(UserAdmin)





class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        try:
            form = await request.form()
            phone_number, password = form["username"], form["password"]
            async with AsyncSessionFactory() as db:
                query = select(User).where(User.phone_number == phone_number)
                result = await db.execute(query)
                user = result.scalars().first()
                if user:

                    if settings.ADMIN_PASSWORD != password:
                        raise CustomException("Parol not'gori kiritilgan")
                else:
                    return False

            access_token_expires = timedelta(minutes=settings.JWT_EXPIRE)
            access_token = await create_access_token(
                data={"sub": user.phone_number}, expires_delta=access_token_expires
            )
            request.session.update({"token": access_token})
            return True
        except Exception as e:
            raise CustomException(e)

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")

        if not token:
            return False

        return True

authentication_backend = AdminAuth(secret_key="09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7")