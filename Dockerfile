# 1. Get python image
FROM python:3.12-slim

# 2. create working dir
WORKDIR /app

# 3. Set built time args
ARG APP_PORT=5005

# 4. Set environment variables
ENV PYTHONDONTWRITECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOST=0.0.0.0 \
    PORT=$APP_PORT

# 5. Install dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 6. Copy and install the requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 7. Copy the application
COPY . .

# 8. Expose the port for external use
EXPOSE ${PORT}

# 9. Run the app
CMD [ "python","run.py"]

