from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from motor.motor_asyncio import AsyncIOMotorClient
import os

DATABASE_URL = 'postgresql+asyncpg://Alexs:root@postgres/Lab3'

MONGO_URL = "mongodb://mongodb:27017"
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "project_db")

engine = create_async_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession)
Base = declarative_base()

client = AsyncIOMotorClient(MONGO_URL)
db = client[MONGO_DB_NAME]


# Функция для получения коллекции проектов
async def get_project_collection():
    return db["project"]