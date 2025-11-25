from pydantic import BaseModel, Field
from typing import Optional

from .models import UserRole

class UserShow(BaseModel):
    name : str
    surname : str

    email : str

    role : UserRole

class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, examples=[None])
    surname: Optional[str] = Field(None, examples=[None])

class UserOwnUpdate(UserUpdate):
    email: Optional[str] = Field(None, examples=[None])

class UserLogin(BaseModel):
    email : str
    password : str

class UserManagerShow(UserShow):
    is_active : bool
    id : int