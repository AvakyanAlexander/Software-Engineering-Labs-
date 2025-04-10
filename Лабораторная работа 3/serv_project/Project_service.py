from sqlalchemy.orm import defer
from sqlalchemy.future import select
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from models.models import Project, User
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


# Create (POST) - Создание нового проекта
@app.post("/api/v1/Project/project_create/")
async def create_project(
                        name: str,
                        description: str = None,
                        token: str = Depends(oauth2_scheme),
                        db: AsyncSession = Depends(get_db)
                        ):
    # Создаем новый проект
    project = Project(
        name=name,
        description=description,
        created_at=datetime.utcnow()
    )
    
    db.add(project)
    await db.commit()
    await db.refresh(project)
    
    return {
        "id": project.id,
        "name": project.name,
        "description": project.description,
        "created_at": project.created_at
    }


# Read (GET) - Получение проекта по ID
@app.get("/api/v1/Project/get_project/{project_name}")
async def read_project(
                        project_name: str,
                        token: str = Depends(oauth2_scheme),
                        db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Project).filter(Project.name == project_name))
    project = result.scalars().first()
  
    if project is None:
        raise HTTPException(status_code=404, detail="Проект не найден")
    return project


@app.get("/api/v1/Project/all_project")
async def get_all_project(token: str = Depends(oauth2_scheme),
                          db: AsyncSession = Depends(get_db)):
    query = await db.execute(select(Project))
    projects = query.scalars().all()
    if projects is None:
        raise HTTPException(status_code=404, detail="Контракты не найдены")
    return {"contract_list": projects}


@app.put("/api/v1/Project/update_project/{project_id}")
async def update_project(
    project_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    result = await db.execute(select(Project).filter(Project.id == project_id))
    project = result.scalars().first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    # Обновляем только те поля, которые переданы
    if name is not None:
        project.name = name
    if description is not None:
        project.description = description
    await db.commit()
    await db.refresh(project)
    
    return {"message": "Проект успешно обновлен"}


@app.delete("/api/v1/Project/delete_project/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """
    Удаление пользователя
    """
    result = await db.execute(
        select(Project).filter(Project.id == project_id))
    project = result.scalars().first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Проект не найден"
        )
    
    await db.delete(project)
    await db.commit()
    
    return {"message": "Проект успешно удален"}

if __name__ == "__main__":
    uvicorn.run("serv_project.Project_service:app", reload=True)