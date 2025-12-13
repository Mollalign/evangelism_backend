# Testing Authentication

## Quick Test Guide

### 1. Start the Server
```bash
source venv/bin/activate
uvicorn app.main:app --reload
```

### 2. Use Swagger UI (Recommended)
Open http://localhost:8000/docs in your browser and test endpoints interactively.

### 3. Manual Testing with curl

#### Register a User
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Test User",
    "email": "test@example.com",
    "password": "testpass123",
    "phone_number": "+1234567890"
  }'
```

#### Login
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123"
  }'
```

#### Get Current User (replace TOKEN with access_token from login)
```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### Refresh Token
```bash
curl -X POST "http://localhost:8000/api/v1/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "YOUR_REFRESH_TOKEN"
  }'
```

### 4. Automated Test (after installing httpx)
```bash
pip install httpx
python scripts/test_auth_endpoints.py
```

