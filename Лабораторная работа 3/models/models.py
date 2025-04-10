from sqlalchemy import (Column,
                        Integer,
                        String,
                        DateTime,
                        Index,
                        Text,
                        ForeignKey)
from sqlalchemy.orm import relationship
from datetime import datetime
from database.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    first_name = Column(String, index=True)  # Индекс для ускорения поиска
    last_name = Column(String, index=True)   # Индекс для ускорения поиск
    username = Column(String, nullable=False)
    email = Column(String, nullable=False)
    password_hashed = Column(String)
    tasks = relationship("Task", back_populates="assignee")
    # Составной индекс для поиска по имени и фамилии одновременно
    __table_args__ = (
        Index("ix_user_first_last_name", "first_name", "last_name"),
    )


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True)
    name = Column(String, index=True)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    tasks = relationship("Task", back_populates="project")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True, index=True)
    title = Column(String(100))
    description = Column(Text)
    project_id = Column(Integer, ForeignKey("projects.id"))
    assignee_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="tasks")
    assignee = relationship("User", back_populates="tasks")


