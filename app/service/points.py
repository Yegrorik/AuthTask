from fastapi import APIRouter, Depends, HTTPException, status, Response

from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import Field

from ..settings.data_base import get_session
from .helpers import authenticate_user, create_access_token, get_password_hash, logout_func
from ..models_shemas.models import User
from ..models_shemas.shemas import UserShow, UserLogin
from .dependencies import get_current_user
from .UsersService import UserService

auth_router = APIRouter(tags=["auth"])

@auth_router.post('/registration', response_model=UserShow)
async def user_registration(
    name: str,
    surname: str,
    email : str,
    password: Annotated[str, Field(
        min_length=3,
        json_schema_extra={"format": "password"}
    )],
    again_password: Annotated[str, Field(
        json_schema_extra={"format": "password"}
    )],
    session : Annotated[AsyncSession, Depends(get_session)]
):
    print("\n")

    cur_user = await UserService.get_user_by_email(session=session, email=email)

    if password != again_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )
    try:
        if cur_user is not None:
            if cur_user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered. Try to login."
                )
            else:
                await UserService.real_delete(session=session, user=cur_user)
                print("Inactive user was deleted")

        hashed_password = await get_password_hash(password)
        new_user = User(name = name, surname = surname, email = email, hashed_password = hashed_password)


        await UserService.add_one(session=session, user=new_user)
        print("New user created")

        print("\n")

        return new_user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@auth_router.post("/login")
async def login(form : UserLogin, session : Annotated[AsyncSession, Depends(get_session)], response: Response):
    user_id = await authenticate_user(session=session, **form.model_dump())

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    access_token = await create_access_token(data = {"sub" : str(user_id)})

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=24 * 60 * 60,
        secure=True
    )

    return {"message": "Login successful"}

@auth_router.post("/logout")
async def system_logout(current_user : Annotated[User, Depends(get_current_user)], response: Response):
    await logout_func(response)

    return {"message": "Successfully logged out"}