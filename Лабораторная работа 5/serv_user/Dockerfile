FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY serv_user/ /app/serv_user/
COPY database/ /app/database/
COPY models/ /app/models/
COPY auth/ /app/auth/

CMD ["python", "-m", "serv_user.user_service"]