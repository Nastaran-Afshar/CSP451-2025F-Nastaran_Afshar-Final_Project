FROM python:3.11-slim

WORKDIR /app

# Install OS dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY applications/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY applications/backend/app ./app

# Copy frontend static files (from applications/frontend/src)
COPY applications/frontend/src ./frontend_static

# Env vars (DB name default)
ENV COSMOS_DB_NAME=cloudmart

EXPOSE 80

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
