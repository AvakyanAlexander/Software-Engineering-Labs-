from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def get_password_hash(password):
    return pwd_context.hash(password)


async def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

async def huy():
    cringe = await get_password_hash("role")
    printe(cringe)