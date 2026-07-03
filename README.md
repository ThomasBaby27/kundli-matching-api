# Kundli Matching API

A scalable RESTful API built with Django REST Framework that calculates matrimonial compatibility scores based on birth details.

## Tech Stack & Architecture
- **Backend Framework:** Django & Django REST Framework (DRF)
- **Database:** PostgreSQL 
- **Caching Layer:** Redis 
- **Authentication:** JWT via SimpleJWT

## Performance Optimization
To maximize throughput and minimize database load, a Redis caching layer caches identical request inputs. 
- **Raw Request Execution:** ~82ms
- **Cached Request Execution:** ~7ms (Up to **91.4% latency reduction**)

## Features
1. **JWT Authentication:** Secure endpoints requiring Bearer tokens.
2. **Data Validation:** Strict payload type-checking using DRF Serializers.
3. **Match History Endpoint:** A retrieval history log for tracking past calculations.
4. **Automated Testing:** 100% test coverage for authentication checkpoints, validation failures, and caching layers.

## Setup Instructions

### 1. Clone the Repository & Navigate
```bash
git clone [https://github.com/ThomasBaby27/kundli-matching-api.git](https://github.com/ThomasBaby27/kundli-matching-api.git)
cd kundli-matching-api

### 2. Environment Configuration

Create a .env file in the project root directory and define your database credentials, secret key, and Redis configuration:
SECRET_KEY=your_secret_key
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=127.0.0.1
DB_PORT=5432
REDIS_URL=redis://127.0.0.1:6379/1

### 3. Install Dependencies
Ensure your virtual environment is active, then run:
pip install -r requirements.txt

### 4. Database Migrations
python manage.py migrate

### 5. Run the Server
python manage.py runserver

API Documentation

### 1. Calculate Match
Endpoint: POST /api/match/
Headers: Authorization: Bearer < your_jwt_token >
Request Body:
{
  "male": {
    "name": "Thomas",
    "date_of_birth": "2004-03-27",
    "time_of_birth": "08:30:00",
    "latitude": 28.6139,
    "longitude": 77.2090
  },
  "female": {
    "name": "Priya",
    "date_of_birth": "2000-08-22",
    "time_of_birth": "14:15:00",
    "latitude": 19.0760,
    "longitude": 72.8777
  }
}

Response (Calculated):
{
  "source": "calculated",
  "data": {
    "compatibility_score": 26.5,
    "verdict": "Excellent",
    "breakdown": { ... },
    "calculated_at": "2026-07-03T04:49:54Z"
  }
}

### 2. Get Match History
Endpoint: GET /api/match/
Headers: Authorization: Bearer <your_jwt_token>
Response:
[
  {
    "id": 1,
    "male_name": "Thomas",
    "female_name": "Priya",
    "compatibility_score": 26.5,
    "verdict": "Excellent",
    "breakdown": { ... },
    "calculated_at": "2026-07-03T04:49:54Z"
  }
]

Running Automated Tests
Execute the testing suite to check API validation, authentication guardrails, and caching logic:
python manage.py test