import asyncio
import asyncpg
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from database.database import Base
from models.models import User, Project, Task  # Прямой импорт

async def wait_for_postgres():
    for i in range(10):
        try:
            print(f"Попытка подключения #{i+1} к postgres:5432...")
            conn = await asyncpg.connect(
                user="Alexs",
                password="root",
                database="Lab3",
                host="postgres",  # ← Важно!
                port=5432,
                timeout=5
            )
            await conn.close()
            print("Подключение успешно!")
            return True
        except Exception as e:
            print(f"Ошибка подключения: {str(e)}")
            await asyncio.sleep(5)
    return False

async def create_test_data(session: AsyncSession):
    # Создаем тестовых пользователей
    users = [
        User(
            first_name="Иван",
            last_name="Иванов",
            username="ivanov",
            email="ivanov@example.com",
            password_hashed="hashed_password_1"
        ),
        User(
            first_name="Петр",
            last_name="Петров",
            username="petrov",
            email="petrov@example.com",
            password_hashed="hashed_password_2"
        ),
        User(
            first_name="Сергей",
            last_name="Сидоров",
            username="sidorov",
            email="sidorov@example.com",
            password_hashed="hashed_password_3"
        ),
    ]
    
    session.add_all(users)
    await session.flush()  # Получаем ID пользователей
    
    # Создаем тестовые проекты
    projects = [
        Project(
            name="Веб-сайт компании",
            description="Разработка корпоративного веб-сайта"
        ),
        Project(
            name="Мобильное приложение",
            description="Разработка iOS и Android приложения"
        ),
    ]
    
    session.add_all(projects)
    await session.flush()  # Получаем ID проектов
    
    # Создаем тестовые задачи
    tasks = [
        Task(
            code="WEB-001",
            title="Дизайн главной страницы",
            description="Создать макет главной страницы",
            project_id=projects[0].id,
            assignee_id=users[0].id
        ),
        Task(
            code="WEB-002",
            title="Реализация API",
            description="Разработать backend API",
            project_id=projects[0].id,
            assignee_id=users[1].id
        ),
        Task(
            code="MOB-001",
            title="Прототип интерфейса",
            description="Создать прототипы экранов приложения",
            project_id=projects[1].id,
            assignee_id=users[2].id
        ),
        Task(
            code="MOB-002",
            title="Авторизация",
            description="Реализовать систему входа в приложение",
            project_id=projects[1].id,
            assignee_id=users[0].id
        ),
    ]
    
    session.add_all(tasks)
    await session.commit()
    
    # Выводим информацию о созданных данных
    print("Созданы тестовые данные:")
    print(f"- Пользователей: {len(users)}")
    print(f"- Проектов: {len(projects)}")
    print(f"- Задач: {len(tasks)}")


async def create_all():
    if not await wait_for_postgres():
        raise Exception("Не удалось подключиться к PostgreSQL")
    
    # Явно указываем URL подключения
    engine = create_async_engine("postgresql+asyncpg://Alexs:root@postgres:5432/Lab3")
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    # Создаем сессию для добавления тестовых данных
    async_session = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )
    
    async with async_session() as session:
        await create_test_data(session)

if __name__ == "__main__":
    asyncio.run(create_all())