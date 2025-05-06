FROM python:3.10-slim

WORKDIR /app

COPY script_db/ /app/script_db/
COPY database/ /app/database/
COPY models/ /app/models/
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "-m", "script_db.init_db"]