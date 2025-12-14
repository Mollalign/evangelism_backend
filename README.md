# 🌟 Evangelism Backend API

A robust, scalable backend API for mission tracking, outreach management, and expense tracking built with **FastAPI** and **PostgreSQL**.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.124+-green.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
- [Configuration](#-configuration)
- [API Documentation](#-api-documentation)
- [Database Models](#-database-models)
- [Authentication](#-authentication)
- [Development](#-development)

---

## ✨ Features

- **🔐 Authentication & Authorization** - JWT-based authentication with access and refresh tokens
- **👥 Multi-Tenant Architecture** - SaaS-ready with account-based data isolation
- **🎯 Mission Management** - Create, track, and manage evangelism missions
- **📊 Outreach Tracking** - Record and analyze outreach activities and outcomes
- **💰 Expense Management** - Track mission-related expenses
- **👤 User & Role Management** - Role-based access control (Admin, Missionary, Evangelist)
- **🏥 Health Monitoring** - Built-in health check endpoints for Kubernetes/Docker

---

## 🛠 Tech Stack

| Category | Technology |
|----------|------------|
| **Framework** | FastAPI 0.124+ |
| **Language** | Python 3.10+ |
| **Database** | PostgreSQL with SQLAlchemy 2.0 |
| **Async Driver** | asyncpg |
| **Migrations** | Alembic |
| **Authentication** | JWT (python-jose) |
| **Password Hashing** | bcrypt / passlib |
| **Validation** | Pydantic v2 |
| **Server** | Uvicorn |

---

## 📁 Project Structure

```
evangelism_backend/
├── app/
│   ├── api/               # API route handlers
│   │   ├── router.py      # Main API router
│   │   └── v1/            # API version 1 endpoints
│   │       ├── auth.py    # Authentication endpoints
│   │       ├── users.py   # User management
│   │       ├── accounts.py# Account management
│   │       ├── missions.py# Mission management
│   │       ├── outreach.py# Outreach tracking
│   │       └── expenses.py# Expense management
│   ├── core/              # Core configurations
│   │   ├── config.py      # Application settings
│   │   ├── database.py    # Database connection
│   │   ├── security.py    # JWT & password utilities
│   │   └── dependencies.py# FastAPI dependencies
│   ├── middleware/        # Custom middleware
│   │   └── logging.py     # Request logging
│   ├── models/            # SQLAlchemy ORM models
│   │   ├── user.py        # User model
│   │   ├── account.py     # Account model
│   │   ├── mission.py     # Mission model
│   │   ├── outreach.py    # Outreach models
│   │   └── expense.py     # Expense model
│   ├── repositories/      # Data access layer
│   ├── schemas/           # Pydantic schemas
│   ├── services/          # Business logic layer
│   ├── utils/             # Utility functions
│   └── main.py            # Application entry point
├── alembic/               # Database migrations
├── scripts/               # Utility scripts
├── requirements.txt       # Python dependencies
└── alembic.ini            # Alembic configuration
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- PostgreSQL 13+
- pip or pipenv

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd evangelism_backend
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

6. **Start the development server**
   ```bash
   uvicorn app.main:app --reload
   ```

The API will be available at `http://localhost:8000`

---

## ⚙️ Configuration

Create a `.env` file in the project root with the following variables:

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/evangelism_db

# Security
SECRET_KEY=your-super-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# Application
PROJECT_NAME=Evangelism Backend API
DEBUG=True
LOG_LEVEL=INFO
TIMEZONE=UTC

# CORS (comma-separated origins)
CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# Optional: Email/SMTP
SMTP_EMAIL=your-email@example.com
SMTP_PASSWORD=your-smtp-password
SMTP_SERVER=smtp.example.com
SMTP_PORT=587
```

---

## 📚 API Documentation

When running in debug mode, interactive documentation is available at:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### API Endpoints Overview

| Category | Endpoint | Description |
|----------|----------|-------------|
| **Health** | `GET /` | API information |
| **Health** | `GET /health` | Health check |
| **Health** | `GET /health/live` | Liveness probe |
| **Health** | `GET /health/ready` | Readiness probe |
| **Auth** | `POST /api/v1/auth/register` | User registration |
| **Auth** | `POST /api/v1/auth/login` | User login |
| **Auth** | `POST /api/v1/auth/refresh` | Refresh token |
| **Users** | `GET /api/v1/users/me` | Current user info |
| **Accounts** | `GET /api/v1/accounts` | List accounts |
| **Missions** | `GET /api/v1/missions` | List missions |
| **Missions** | `POST /api/v1/missions` | Create mission |
| **Outreach** | `GET /api/v1/outreach` | List outreach data |
| **Outreach** | `POST /api/v1/outreach` | Record outreach |
| **Expenses** | `GET /api/v1/expenses` | List expenses |
| **Expenses** | `POST /api/v1/expenses` | Create expense |

---

## 🗃 Database Models

### Core Entities

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Account   │────▶│ AccountUser │◀────│    User     │
└─────────────┘     └─────────────┘     └─────────────┘
       │                   │                   │
       │                   ▼                   │
       │            ┌─────────────┐            │
       │            │    Role     │            │
       │            └─────────────┘            │
       │                                       │
       ▼                                       ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Mission   │────▶│ MissionUser │     │   Expense   │
└─────────────┘     └─────────────┘     └─────────────┘
       │
       ▼
┌─────────────────────┐
│    OutreachData     │
│   OutreachNumbers   │
└─────────────────────┘
```

---

## 🔐 Authentication

The API uses JWT (JSON Web Token) authentication with a dual-token strategy:

### Token Flow

1. **Access Token**: Short-lived (default 60 minutes), used for API requests
2. **Refresh Token**: Long-lived (default 7 days), used to obtain new access tokens

### Usage Example

```bash
# Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=yourpassword"

# Access protected endpoint
curl -X GET "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer <access_token>"

# Refresh token
curl -X POST "http://localhost:8000/api/v1/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "<refresh_token>"}'
```

---

## 🧑‍💻 Development

### Running Tests

```bash
pytest
```

### Running with Auto-Reload

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback one version
alembic downgrade -1
```

### Code Quality

```bash
# Format code
black app/

# Sort imports
isort app/

# Type checking
mypy app/
```

---

## 📄 License

This project is licensed under the MIT License.

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

<p align="center">
  Made with ❤️ for spreading the Gospel
</p>
