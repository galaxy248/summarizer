# Summarizer

An AI-powered content summarization service.

## Features

- **REST API**: Written in FastAPI
- **User Authentication**: JWT-based authentication system
- **File Upload Support**: Supports PDF and text file
- **Architecture**: Dockerized services and app
- **File Storage**: MinIO-based object storage
- **Database**: PostgreSQL

## Prerequisites

- **Docker** and **Docker Compose** installed
- **Python 3.10+** (for local development)
- **AI Model API Key**

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/galaxy248/summarizer.git
cd summarizer
```

### 2. Create Docker Network

First, create a Docker network for all services:

```bash
docker network create summarizer_network
```

### 3. Configure Environment Variables

create a `.env` file in the root directory of the project:
```bash
touch .env
```

Edit `.env` file with your configuration:

```env
# Application (Required!)
MODEL_TOKEN=your_api_key_here

# Application (Optional)
LOG_LEVEL="DEBUG|INFO|WARNING|ERROR|CRITICAL"
LOG_FORMAT="text|json"

# Database (Optional)
DB_URL="..."
DB_URL="..."
DB_POOL_SIZE="..."
DB_MAX_OVERFLOW="..."
DB_POOL_TIMEOUT="..."
DB_POOL_RECYCLE="..."

# MinIO (Optional)
MINIO_ENDPOINT="..."
MINIO_ACCESS_KEY="..."
MINIO_SECRET_KEY="..."
MINIO_BUCKET_NAME="..."

# JWT (Optional)
JWT_ALGORITHM="..."
JWT_ACCESS_TOKEN_EXPIRE_MINUTES="..."
JWT_SECRET_KEY="..."
```

### 4. Start Main Services

Start the main services:

#### Database
```bash
cd services/database
docker-compose up -d
cd ../..
```

#### Storage
```bash
cd services/storage
docker-compose up -d
cd ../..
```

### 5. Start Main Application
```bash
docker-compose up -d
```

#### Note:
- if you want to run the application with pre-built images, you should change the `build: .` section in the `docker-compose.yml` file to `image: ghcr.io/galaxy248/summarizer:latest`.


### 6. Access the Application

- **Web Interface**: http://127.0.0.1:8000
- **API Documentation**: http://127.0.0.1:8000/docs
- **MinIO Console**: http://127.0.0.1:20901
- **Database**: http://127.0.0.1:20800

#### Note:
- the default ports [`8000`, `20800`, `20900`, `20901`] can be changed in the `docker-compose.yml` files.

## Development Setup

### 1. Install Python

Create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

### 2. Start Services

#### Database
```bash
cd services/database
docker-compose up -d
cd ../..
```

#### Storage
```bash
cd services/storage
docker-compose up -d
cd ../..
```

### 3. Configure Environment Variables

create a `.env` file in the root directory of the project:
```bash
touch .env
```

Edit `.env` file with your configuration:

```env
# Application (Required!)
MODEL_TOKEN=your_api_key_here

# Application (Optional)
LOG_LEVEL="DEBUG|INFO|WARNING|ERROR|CRITICAL"
LOG_FORMAT="text|json"

# Database (Optional)
DB_URL="..."
DB_URL="..."
DB_POOL_SIZE="..."
DB_MAX_OVERFLOW="..."
DB_POOL_TIMEOUT="..."
DB_POOL_RECYCLE="..."

# MinIO (Optional)
MINIO_ENDPOINT="..."
MINIO_ACCESS_KEY="..."
MINIO_SECRET_KEY="..."
MINIO_BUCKET_NAME="..."

# JWT (Optional)
JWT_ALGORITHM="..."
JWT_ACCESS_TOKEN_EXPIRE_MINUTES="..."
JWT_SECRET_KEY="..."
```

### 4. Run Application Locally

```bash
cd src/app

uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

**Made with ❤️ & ☕ by Amir Mohammad Anvari and Amir Mahdi Abooshahab**
