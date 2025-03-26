# Dockerfile для пользователей  
FROM python:3.9-slim  

# Установите рабочую директорию  
WORKDIR /app  

# Скопируйте зависимости  
COPY ./user/requirements.txt ./  
RUN pip install --no-cache-dir -r requirements.txt  

# Скопируйте исходный код пользователей  
COPY ./user ./user
COPY ./project ./project  

# Установите переменную окружения для Python  
ENV PYTHONPATH=/app  

# Запуск приложения  
CMD ["python", "-m", "user.Lab2_user"] 