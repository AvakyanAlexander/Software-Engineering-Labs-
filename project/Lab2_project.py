from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

router = APIRouter(prefix="/api/v1/project", 
                tags=["Project"])

# Модель данных для проектов
class Project(BaseModel):  
    id: int
    name: str
    description: str
    created_at: datetime
    owner_id: int  

# Временное хранилище для пользователей
project_db = []

# Настройка OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.post("/create_project", response_model=Project)
def create_project(projects: Project, current_user: str = Depends(oauth2_scheme)):

    for pr in project_db:
        if pr.id == projects.id:
            raise HTTPException(status_code=404, detail="Project already exist")
    project_db.append(projects)
    return projects

@router.get("/all_projects", response_model=List[Project])
def get_projects(current_project: str = Depends(oauth2_scheme)):
    return project_db

# GET /users/{user_id} - Получить пользователя по ID (требует аутентификации)
@router.get("/list_projects/{project_name}", response_model=Project)
def get_user(project_name: str, current_user: str = Depends(oauth2_scheme)):
    for project in project_db:
        if project.name == project_name:
            return project
    raise HTTPException(status_code=404, detail="Project not found")

@router.delete("/delete_project/{project_id}", response_model=Project)
def delete_project(project_id: int, current_user: str = Depends(oauth2_scheme)):
    for index, project in enumerate(project_db):
        if project.id == project_id:
            deleted_project = project_db.pop(index)
            return deleted_project
    raise HTTPException(status_code=404, detail="User not found")


# Запуск сервера
# http://localhost:8000/openapi.json swagger
# http://localhost:8000/docs портал документации