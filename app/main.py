from fastapi import FastAPI, Depends, Query, Response, HTTPException, status

from typing import Annotated, List
from sqlalchemy.ext.asyncio import AsyncSession

from .service.points import auth_router
from .service.dependencies import get_current_user, get_current_admin_user, get_current_manager_user
from .models_shemas.models import User, UserRole
from .models_shemas.shemas import UserShow, UserUpdate, UserManagerShow, UserOwnUpdate
from .settings.data_base import get_session
from .service.helpers import verify_password, logout_func
from .service.UsersService import UserService

app = FastAPI()

app.include_router(auth_router)

@app.get("/user/profile", response_model=UserShow, tags=["For All"])
async def get_profile_me(current_user : Annotated[User, Depends(get_current_user)]):
    return current_user

@app.put("/user/profile/update", tags=["For All"])
async def update_profile_me(update_data : UserOwnUpdate,
                         current_user : Annotated[User, Depends(get_current_user)],
                         session : Annotated[AsyncSession, Depends(get_session)],
                         password: str = Query(
                             json_schema_extra={"format": "password"},
                             description="Enter your password to change email",
                             default=None
                         )
                         ):
    print()
    response = {"User" : UserShow(**current_user.__dict__), "details" : []}

    update_fields = update_data.model_dump(exclude_defaults=True)

    if not update_fields:
        print("There were no changes\n")

        response["details"].append("There were no changes")
        return response

    has_email = update_fields.get("email", None)
    if has_email is not None and current_user.email != has_email:
        if password is not None:
            if await verify_password(password, current_user.hashed_password):
                usEmail = await UserService.get_user_by_email(session, current_user.email)

                if usEmail is not None:
                    response["details"].append("The email address you entered is already in use")
                    update_fields.pop("email")
            else:
                response["details"].append("Password you entered is incorrect to change email")
                update_fields.pop("email")
        else:
            response["details"].append("Enter your password to change email")
            update_fields.pop("email")

    if update_fields:
        await UserService.update_user_data(session, current_user.id, update_fields)
        response["details"].append("successfully updated")

    response["User"] = UserShow(**current_user.__dict__)

    return response

@app.delete("/user/delete", tags=["For All"])
async def delete_me(current_user : Annotated[User, Depends(get_current_user)], session : Annotated[AsyncSession, Depends(get_session)], response: Response):
    await UserService.soft_removal(session, current_user)
    await logout_func(response)

    return {"message" : "successfully deleted"}

@app.get("/users/get", response_model=List[UserManagerShow], tags = ["For Managers"])
async def get_users(current_user : Annotated[User, Depends(get_current_manager_user)], session : Annotated[AsyncSession, Depends(get_session)]):
    result = await UserService.get_all_users(session = session)
    return result

@app.put("/user/update/{user_id}", tags = ["For Managers"])
async def update_user_info(current_user : Annotated[User, Depends(get_current_manager_user)], session : Annotated[AsyncSession, Depends(get_session)],
                           user_id : int, update_user_data : UserUpdate):
    update_fields = update_user_data.model_dump(exclude_defaults=True)


    updated_user = await UserService.get_user_by_id(session, user_id=user_id)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} was not found"
        )

    if not current_user.role <= updated_user.role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action"
        )

    if not update_fields:
        return {"message" : "There were no changes"}

    response = await UserService.update_user_data(session, updated_user.id, update_fields)
    return response


@app.get("/user/get/{user_id}", response_model=UserManagerShow, tags = ["For Managers"])
async def get_user(current_user : Annotated[User, Depends(get_current_manager_user)], session : Annotated[AsyncSession, Depends(get_session)],
                   user_id : int):
    result = await UserService.get_user_by_id(session, user_id=user_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="user not found"
        )
    return result

@app.put("/user/put/{user_id}", tags = ["For Admins Only"])
async def set_role_to_user(current_user : Annotated[User, Depends(get_current_admin_user)], session : Annotated[AsyncSession, Depends(get_session)], user_id : int, role : UserRole):
    updated_user = await UserService.get_user_by_id(session, user_id=user_id)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} was not found"
        )

    if role == UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only set user or manager roles"
        )

    if current_user.role == updated_user.role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can not demote other admins"
        )

    response = await UserService.update_user_data(session, user_id=user_id, update_fields={"role" : role})

    return response

@app.delete("/user/delete/{user_id}", tags = ["For Admins Only"])
async def delete_user(current_user : Annotated[User, Depends(get_current_admin_user)], session : Annotated[AsyncSession, Depends(get_session)],
                      user_id : int):
    deleted_user = await UserService.get_user_by_id(session, user_id=user_id)
    if not deleted_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} was not found"
        )

    if current_user.role == deleted_user.role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can not delete other admins"
        )

    response = await UserService.soft_removal(session, user=deleted_user)

    return response

@app.get("/admin-check", tags=["Check Roles"])
async def check_admin(current_user : Annotated[User, Depends(get_current_admin_user)]):
    return {"MSG" : f"Hello {current_user.role} {current_user.name}"}

@app.get("/manager-check", tags=["Check Roles"])
async def check_manager(current_user : Annotated[User, Depends(get_current_manager_user)]):
    return {"MSG" : f"Hello {current_user.role} {current_user.name}"}

"""
@app.get("/all-user")
async def all_user(session : Annotated[AsyncSession, Depends(get_session)]):
    res = await UserService.get_all_users(session)

    return res
"""