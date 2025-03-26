FROM python:3.9-slim  
  
WORKDIR /app  

COPY ./user/requirements.txt ./  
RUN pip install --no-cache-dir -r requirements.txt  
  
COPY ./user ./user
COPY ./project ./project  
  
ENV PYTHONPATH=/app  

CMD ["python", "-m", "user.Lab2_user"] 