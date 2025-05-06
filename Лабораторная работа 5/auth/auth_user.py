from auth.hash_password import verify_password
from sqlalchemy.ext.asyncio import AsyncSession
from models.models import User
from sqlalchemy.future import select


async def get_user(db: AsyncSession, username: str):
    result = await db.execute(select(User).filter(User.username == username))
    return result.scalars().first()


async def authenticate_user(db: AsyncSession, username: str, password: str):
    user = await get_user(db, username)
    if not user or not await verify_password(password, user.password_hashed):
        return False
    return user
