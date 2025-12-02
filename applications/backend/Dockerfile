FROM python:3.11-slim

WORKDIR /app

# Install OS dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy only backend app
COPY app ./app

ENV COSMOS_DB_NAME=cloudmart

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
