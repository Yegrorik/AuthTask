import jwt
from pwdlib import PasswordHash
from fastapi import HTTPException, status, Response

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..settings.config import settings
from ..models_shemas.models import User

password_hash = PasswordHash.recommended()

async def get_password_hash(password):
    return password_hash.hash(password)

async def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)

async def authenticate_user(session : AsyncSession, **kwargs):
    user_res = await session.execute(select(User.id, User.hashed_password, User.is_active).where(User.email == kwargs['email']))
    user_row = user_res.first()

    if not user_row:
        return False

    id, hashed_password, active = user_row

    if not active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with this email was deleted"
        )
    condition = await verify_password(kwargs['password'], hashed_password)
    if not condition:
        return False

    return id


async def create_access_token(data : dict):
    encoded_jwt = jwt.encode(data.copy(), settings.SECRET, algorithm=settings.ALGORITHM)

    return encoded_jwt

async def logout_func(response : Response):
    response.delete_cookie("access_token")