from typing import Annotated

from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.config import settings
from datetime import datetime, timedelta
from jose import JWTError, jwt

from app.database import get_db
from app.user.models import User


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/token_docs")

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.JWT_EXPIRE

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


async def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        phone_number: str = payload.get("sub")
        if phone_number is None:
            raise credentials_exception
        return phone_number
    except JWTError as e:
        raise credentials_exception


async def get_user_from_token(db: AsyncSession, token: str) -> User:
    phone_number = decode_access_token(token)
    result = await db.execute(select(User).where(User.phone_number == phone_number))
    user = result.scalars().first()
    if user is None:
        raise credentials_exception
    return user


async def current_user(db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
    return await get_user_from_token(db, token)


async def active_user(db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
    user = await get_user_from_token(db, token)
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Bu amaliyot uchun ruhsat mavjud emas")
    return user


async def superuser(db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
    user = await get_user_from_token(db, token)
    if not user.is_superuser:
        raise HTTPException(status_code=403, detail="Bu amaliyot uchun ruhsat mavjud emas")
    return user


SessionDep = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[User, Depends(current_user)]
ActiveUser = Annotated[User, Depends(active_user)]
Superuser = Annotated[User, Depends(superuser)]

