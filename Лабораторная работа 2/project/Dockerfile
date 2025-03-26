FROM python:3.9-slim  
  
WORKDIR /app  
  
COPY ./project/requirements.txt ./  
RUN pip install --no-cache-dir -r requirements.txt  
  
COPY ./project ./project  
  
ENV PYTHONPATH=/app  
  
CMD ["python", "-m", "project.Lab2_project"]  