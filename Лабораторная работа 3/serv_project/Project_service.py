from sqlalchemy.orm import defer
from sqlalchemy.future import select
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from models import Project
from database import SessionLocal
from sqlalchemy.ext.asyncio import AsyncSession
from auth.jwt_token import decode_token
from datetime import datetime
from typing import Optional, List

router = APIRouter(
    prefix="/api/v1/Project",
    tags=["Project"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


async def get_db():
    async with SessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()

router = APIRouter(
    prefix="/api/v1/Project",
    tags=["Project"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


# Create (POST) - Создание нового проекта
@router.post("/project_create/")
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
@router.get("/get_project/{project_name}")
async def read_project(
                        project_name: str,
                        token: str = Depends(oauth2_scheme),
                        db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Project).filter(Project.name == project_name))
    project = result.scalars().first()
  
    if project is None:
        raise HTTPException(status_code=404, detail="Проект не найден")
    return project


@router.get("/all_project")
async def get_all_project(token: str = Depends(oauth2_scheme),
                          db: AsyncSession = Depends(get_db)):
    query = await db.execute(select(Project))
    projects = query.scalars().all()
    if projects is None:
        raise HTTPException(status_code=404, detail="Контракты не найдены")
    return {"contract_list": projects}


@router.put("/update_project/{project_id}")
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


@router.delete("/delete_project/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
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