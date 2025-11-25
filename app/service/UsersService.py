from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update, select

from fastapi import HTTPException, status

from ..models_shemas.models import User


class UserService:
    @classmethod
    async def update_user_data(cls, session : AsyncSession, user_id : int, update_fields : dict):
        try:
            user = await cls.get_user_by_id(session, user_id=user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )

            await session.execute(update(User).where(User.id == user_id).values(**update_fields))
            await session.commit()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        return {"message": "successfully updated"}

    @classmethod
    async def get_user_by_email(cls, session : AsyncSession, email: str):
        user_res = await session.execute(select(User).where(User.email == email))
        user = user_res.scalar_one_or_none()

        return user

    @classmethod
    async def get_user_by_id(cls, session : AsyncSession, user_id: int):
        user_res = await session.get(User, user_id)

        return user_res

    @classmethod
    async def soft_removal(cls, session : AsyncSession, user: User):
        try:
            await session.execute(update(User).where(User.id == user.id).values(is_active=False))
            await session.commit()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
        return {"message": "successfully soft-removed"}

    @classmethod
    async def real_delete(cls, session : AsyncSession, user: User):
        await session.delete(user)
        await session.commit()

    @classmethod
    async def add_one(cls, session : AsyncSession, user: User):
        session.add(user)
        await session.commit()

    @classmethod
    async def get_all_users(cls, session : AsyncSession):
        users_res = await session.execute(select(User))
        users = users_res.scalars().all()

        return users