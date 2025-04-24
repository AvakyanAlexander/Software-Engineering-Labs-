from fastapi import FastAPI, HTTPException, Depends, Query, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from models.models import User
from sqlalchemy.orm import defer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from auth.jwt_token import decode_token
from typing import Optional, List
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

@app.post("/api/v1/user/register/")
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

@app.get("/api/v1/user/Search_login/{user_login}")
async def get_user_login(user_login: str,
                       token: str = Depends(oauth2_scheme),
                       db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).filter(User.username == user_login))
    user = result.scalars().first()
  
    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    return user

@app.get("/api/v1/user/Search_mask/")
async def get_user_mask(
    first_name: Optional[str] = Query(None, min_length=1, description="Маска для поиска по имени"),
    last_name: Optional[str] = Query(None, min_length=1, description="Маска для поиска по фамилии"),
    db: AsyncSession = Depends(get_db)
):
    """
    Поиск пользователей по маске имени и/или фамилии.
    Возвращает список пользователей, у которых имя или фамилия содержат указанные строки.
    """
    query = select(User)
    
    if first_name:
        query = query.filter(User.first_name.ilike(f"%{first_name}%"))
    if last_name:
        query = query.filter(User.last_name.ilike(f"%{last_name}%"))
    
    result = await db.execute(query)
    users = result.scalars().all()
    
    return {
        "count": len(users),
        "users": [
            {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "username": user.username,
                "email": user.email
            }
            for user in users
        ]
    }

@app.put("/api/v1/user/update_user/{user_id}")
async def update_user(
    user_id: int,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    email: Optional[str] = None,
    password: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """
    Обновление информации о пользователе
    
    Параметры:
    - user_id: ID пользователя для обновления
    - first_name: Новое имя (опционально)
    - last_name: Новая фамилия (опционально)
    - email: Новый email (опционально)
    - password: Новый пароль (опционально)
    """
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    # Обновляем только те поля, которые переданы
    if first_name is not None:
        user.first_name = first_name
    if last_name is not None:
        user.last_name = last_name
    if email is not None:
        # Проверяем, что новый email не занят другим пользователем
        existing_email = await db.execute(
            select(User).filter(
                User.email == email,
                User.id != user_id
            )
        )
        if existing_email.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email уже используется другим пользователем"
            )
        user.email = email
    if password is not None:
        user.password_hashed = await get_password_hash(password)
    
    await db.commit()
    await db.refresh(user)
    
    return {"message": "Пользователь успешно обновлен"}

@app.delete("/api/v1/user/delete_user/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """
    Удаление пользователя
    """
    result = await db.execute(
        select(User).filter(User.id == user_id))
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    await db.delete(user)
    await db.commit()
    
    return {"message": "Пользователь успешно удален"}

if __name__ == "__main__":
    uvicorn.run("serv_user.user_service:app", host="0.0.0.0", port=8001)