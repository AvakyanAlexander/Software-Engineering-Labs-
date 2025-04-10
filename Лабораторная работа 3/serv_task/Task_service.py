from sqlalchemy.orm import defer
from sqlalchemy.future import select
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from models.models import Task, User
from database.database import SessionLocal
from sqlalchemy.ext.asyncio import AsyncSession
from auth.jwt_token import decode_token
from auth.jwt_token import create_access_token
from auth.auth_user import authenticate_user
from datetime import timedelta, datetime
from typing import Optional, List
import uvicorn

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


async def get_db():
    async with SessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()

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

@app.post("/api/v1/Task/task_create/")
async def create_task(
                        project_id: int,
                        code: str,
                        title: str = None,
                        description: str = None,
                        token: str = Depends(oauth2_scheme),
                        db: AsyncSession = Depends(get_db)
                        ):
    payload = await decode_token(token)
    if payload is None:
        raise HTTPException(status_code=401,
                            detail="Неверный токен или срок действия истёк")
    if payload["sub"] is None:
        raise HTTPException(status_code=401,
                            detail="Пользователь не найден в токене")
    id_user = await db.execute(select(User).filter(User.username == payload["sub"]))
    # Создаем новый проект
    task = Task(
        code=code,
        title=title,
        description=description,
        project_id=project_id,
        assignee_id=id_user.scalars().first().id,
        created_at=datetime.utcnow()
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


# Read (GET) - Получение проекта по ID
@app.get("/api/v1/Task/get_task/{code_task}")
async def get_task_code(
                        task_code: str,
                        token: str = Depends(oauth2_scheme),
                        db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Task).filter(Task.code == task_code))
    project = result.scalars().first()
  
    if project is None:
        raise HTTPException(status_code=404, detail="Проект не найден")
    return project


@app.get("/api/v1/Task/all_tasks")
async def get_all_task(token: str = Depends(oauth2_scheme),
                       db: AsyncSession = Depends(get_db)):
    query = await db.execute(select(Task))
    task = query.scalars().all()
    if task is None:
        raise HTTPException(status_code=404, detail="Контракты не найдены")
    return {"contract_list": task}


@app.put("/api/v1/Task/update_task/{task_id}")
async def update_task(
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    
    result = await db.execute(select(Task).filter(Task.id == task_id))
    task = result.scalars().first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задача не найдена"
        )
    
    # Обновляем только те поля, которые переданы
    if title is not None:
        task.title = title
    if description is not None:
        task.description = description
    await db.commit()
    await db.refresh(task)
    
    return {"message": "Задача успешно обновлена"}


@app.delete("/api/v1/Task/delete_task/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """
    Удаление пользователя
    """
    result = await db.execute(
        select(Task).filter(Task.id == task_id))
    task = result.scalars().first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задача не найдена"
        )
    
    await db.delete(task)
    await db.commit()
    
    return {"message": "Задача успешно удалена"}

if __name__ == "__main__":
    uvicorn.run("serv_task.Task_service:app", reload=True)