# Dockerfile для проекта  
FROM python:3.9-slim  

# Установите рабочую директорию  
WORKDIR /app  

# Скопируйте зависимости  
COPY ./project/requirements.txt ./  
RUN pip install --no-cache-dir -r requirements.txt  

# Скопируйте исходный код проекта  
COPY ./project ./project  

# Установите переменную окружения для Python  
ENV PYTHONPATH=/app  

# Запуск приложения  
CMD ["python", "-m", "project.Lab2_project"]  