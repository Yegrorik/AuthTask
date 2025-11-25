from fastapi import Depends, HTTPException, status, Cookie
from jwt.exceptions import InvalidTokenError
import jwt

from typing import Annotated, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from ..settings.data_base import get_session
from ..settings.config import settings
from ..models_shemas.models import User, UserRole


async def get_current_user(session : Annotated[AsyncSession, Depends(get_session)], access_token: Optional[str] = Cookie(None)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = jwt.decode(access_token, settings.SECRET, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")

        if not user_id:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception

    user = await session.get(User, int(user_id))

    if not user:
        raise credentials_exception

    return user

async def get_current_admin_user(current_user : Annotated[User, Depends(get_current_user)]):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

async def get_current_manager_user(current_user : Annotated[User, Depends(get_current_user)]):
    if current_user.role not in (UserRole.MANAGER, UserRole.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager access required"
        )
    return current_user