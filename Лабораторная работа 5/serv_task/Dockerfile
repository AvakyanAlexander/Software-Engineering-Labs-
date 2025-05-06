FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY serv_task/ /app/serv_task/
COPY database/ /app/database/
COPY models/ /app/models/
COPY serv_redis/ /app/serv_redis/
COPY auth/ /app/auth/


CMD ["python", "-m", "serv_task.Task_service"]