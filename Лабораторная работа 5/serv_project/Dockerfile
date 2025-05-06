FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY serv_project/ /app/serv_project/
COPY database/ /app/database/
COPY models/ /app/models/
COPY auth/ /app/auth/

CMD ["python", "-m", "serv_project.Project_service"]