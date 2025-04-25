#use python:3.10-slim image as base
FROM python:3.10-slim

#setup working directory
WORKDIR /app

#copy requirements.txt into the container
COPY requirements.txt .

#install dependencies
RUN pip install --no-cache-dir --upgrade -r requirements.txt

#copy FastAPI code to container
COPY src/ .

#expose 8000
EXPOSE 8000

#set database host environment variable
ENV DB_HOST="host.docker.internal"

#start fastapi app
CMD ["fastapi", "dev", "--host", "0.0.0.0", "--port", "8000", "main.py"]
