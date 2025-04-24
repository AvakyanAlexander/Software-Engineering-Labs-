from sqlalchemy.orm import defer
from sqlalchemy.future import select
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from models.models import ProjectBase
from database.database import SessionLocal, get_project_collection
from sqlalchemy.ext.asyncio import AsyncSession
from auth.jwt_token import decode_token
from auth.jwt_token import create_access_token
from auth.auth_user import authenticate_user
from datetime import timedelta, datetime
from typing import Optional, List
import uvicorn

from pydantic import BaseModel, Field
from pymongo import MongoClient
from fastapi import FastAPI, Depends, HTTPException, status, Path
from motor.motor_asyncio import AsyncIOMotorClient
import os
import json


async def get_db():
    async with SessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()


app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


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


@app.post("/api/v1/Project/project_create/", response_model=ProjectBase)
async def create_project(
    project: ProjectBase,
    collection=Depends(get_project_collection)  # Добавляем dependency
):
    insert_result = await collection.insert_one(project.dict())  # Используем .dict() вместо .__dict__
    print(f"Project inserted with id: {insert_result.inserted_id}")
    return project

# Маршрут для получения проекта по имени
@app.get("/api/v1/Project/get_project/{project_name}", response_model=ProjectBase)
async def get_project(
    project_name: str = Path(..., description="Название проекта"),
    collection=Depends(get_project_collection)  # Добавляем dependency
):
    query = {"name": project_name}
    result = await collection.find_one(query)

    if result:
        return result
    raise HTTPException(status_code=404, detail="Проект не найден")

# Маршрут для получения всех проектов
@app.get("/api/v1/Project/all_project/", response_model=List[ProjectBase])
async def get_all_project(
    collection=Depends(get_project_collection)  # Добавляем dependency
):
    cursor = collection.find()
    projects = []
    async for document in cursor:
        projects.append(document)
    return projects

# Маршрут для обновления проекта (PUT)
@app.put("/api/v1/Project/update_project/{project_name}", response_model=ProjectBase)
async def update_project(
    project_name: str = Path(..., description="Название проекта для обновления"),
    updated_project: ProjectBase = ...,  # Новые данные проекта
    collection=Depends(get_project_collection)
):
    # Ищем проект по имени
    existing_project = await collection.find_one({"name": project_name})
    if not existing_project:
        raise HTTPException(status_code=404, detail="Проект не найден")
    
    # Обновляем проект
    update_data = updated_project.dict(exclude_unset=True)
    await collection.update_one(
        {"name": project_name},
        {"$set": update_data}
    )
    
    # Возвращаем обновленный проект
    updated = await collection.find_one({"name": update_data.get("name", project_name)})
    return updated

# Маршрут для удаления проекта (DELETE)
@app.delete("/api/v1/Project/delete_project/{project_name}", response_model=dict)
async def delete_project(
    project_name: str = Path(..., description="Название проекта для удаления"),
    collection=Depends(get_project_collection)
):
    # Проверяем существование проекта
    existing_project = await collection.find_one({"name": project_name})
    if not existing_project:
        raise HTTPException(status_code=404, detail="Проект не найден")
    
    # Удаляем проект
    delete_result = await collection.delete_one({"name": project_name})
    
    if delete_result.deleted_count == 1:
        return {"status": "success", "message": f"Проект '{project_name}' удален"}
    else:
        raise HTTPException(status_code=500, detail="Ошибка при удалении проекта")


if __name__ == "__main__":
    uvicorn.run("serv_project.Project_service:app", host="0.0.0.0", port=8002)