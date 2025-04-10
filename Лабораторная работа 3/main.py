from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.models import User
from database.database import SessionLocal
from auth.hash_password import get_password_hash
from auth.jwt_token import create_access_token
from auth.auth_user import authenticate_user
from datetime import timedelta
import uvicorn

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

async def get_db():
    async with SessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()

app = FastAPI()

@app.post("/register/")
async def register_user(first_name: str,
                        last_name: str,
                        username: str,
                        email: str,
                        password: str,
                        db: AsyncSession = Depends(get_db)):
    query = select(User).filter(User.username == username)
    result = await db.execute(query)
    existing_user = result.scalars().first()

    if existing_user:
        raise HTTPException(status_code=400,
                            detail="Пользователь уже существует")

    hashed_password = await get_password_hash(password)
    new_user = User(first_name=first_name,
                    last_name=last_name,
                    username=username,
                    email=email,
                    password_hashed=hashed_password)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return {"msg": "Пользователь успешно зарегистрирован"}


@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(),
                db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = await create_access_token(data={"sub": user.username},
                                             expires_delta=timedelta(minutes=30))
    return {"access_token": access_token, "token_type": "bearer"}



if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)

