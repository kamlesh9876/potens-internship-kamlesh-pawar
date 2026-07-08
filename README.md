# SkillPath Recommendation API

**Submission:** Potens Internship 2026
**Role:** Backend
**Question:** Q2 – Profile-to-Recommendation API

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.x-red)
![Tests](https://img.shields.io/badge/Tests-116_Passing-brightgreen)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## Table of Contents
- [Highlights](#highlights)
- [Overview](#overview)
- [Screenshots](#screenshots)
- [Features](#features)
- [Tech Stack & Design Decisions](#tech-stack--design-decisions)
- [Architecture](#architecture)
- [Setup Instructions](#setup-instructions)
- [Database Setup](#database-setup)
- [Run Instructions](#run-instructions)
- [API Documentation](#api-documentation)
- [Example Requests](#example-requests)
- [Testing](#testing)
- [Assumptions](#assumptions)
- [Limitations](#limitations)
- [Future Improvements](#future-improvements)
- [AI Use Declaration](#ai-use-declaration)
- [Phase Completion](#phase-completion)
- [License](#license)

---

## Highlights
- ✅ Explainable recommendation engine with weighted scoring
- ✅ 16-item catalogue with diverse eligibility rules
- ✅ JWT authentication with role-based access control
- ✅ Admin CRUD operations for catalogue management
- ✅ `GET /explain/{id}` endpoint for recommendation explanations
- ✅ Alembic database migrations
- ✅ Rate limiting (100 requests/minute)
- ✅ In-memory caching with TTL
- ✅ 116 automated tests passing
- ✅ OpenAPI documentation (Swagger/ReDoc)
- ✅ Repository pattern for data access
- ✅ Structured logging and metrics

## Overview
SkillPath Recommendation API is my submission for the Potens Internship Backend Question 2. The system recommends the three most suitable learning paths for a user based on their profile, budget, goals, experience level, and learning preferences. The recommendation engine uses weighted eligibility scoring and returns human-readable explanations for every recommendation.

### Why This Domain?
I chose skill recommendations because the matching process naturally requires multiple eligibility rules (goal alignment, skill level compatibility, budget constraints, location preferences), making it a good fit for demonstrating recommendation logic beyond simple filtering. This domain allows showcasing:
- Complex scoring algorithms
- Explainable AI decisions
- Real-world business constraints
- Diverse data relationships

---

## Screenshots

## Screenshots

### Swagger UI
![Swagger UI Overview](screenshots/Screenshot%202026-07-08%20160555.png)

### Recommendation Endpoint
![Swagger Recommend Endpoint](screenshots/Screenshot%202026-07-08%20160618.png)

### Authentication Endpoints
![Swagger Auth Endpoints](screenshots/Screenshot%202026-07-08%20160818%20-%20Copy.png)

### Try It Out
![Swagger Try It Out](screenshots/Screenshot%202026-07-08%20160835.png)

### SQLite Schema
![SQLite Schema](screenshots/Screenshot%202026-07-08%20160929.png)

### Users Table
![SQLite Users Table](screenshots/Screenshot%202026-07-08%20161011.png)

### Items Table
![SQLite Items Table](screenshots/Screenshot%202026-07-08%20161027.png)

---

## Features
- **Recommendation Engine**: Personalized skill path recommendations with weighted scoring and explainable results
- **JWT Authentication**: Secure token-based authentication with role-based access control
- **CRUD Operations**: Full Create, Read, Update, Delete for catalogue items (admin only)
- **Filtering & Pagination**: Filter by category, location, goal, skill level, price range with efficient pagination
- **Search**: Full-text search across item names, descriptions, and categories
- **Caching**: In-memory caching with TTL for recommendation endpoint performance
- **Rate Limiting**: 100 requests/minute per IP to prevent abuse
- **Application Metrics Endpoint**: Request tracking and performance monitoring
- **API Versioning**: Versioned endpoints under `/api/v1/` for future compatibility
- **Background Tasks**: Welcome email sending, user login logging, password change logging
- **Security Headers**: Comprehensive security headers (X-Content-Type-Options, X-Frame-Options, etc.)
- **Request Logging**: Structured logging with request ID tracking for debugging

---

## Tech Stack & Design Decisions

### Why FastAPI?
- **Automatic OpenAPI**: Swagger/ReDoc documentation generated automatically
- **Async Support**: Built-in async/await for better performance
- **Type-Safe Validation**: Pydantic integration for request/response validation
- **Modern**: Active community, excellent performance benchmarks

### Why SQLite?
- **Lightweight**: No separate database server required for evaluation
- **Easy Setup**: Single file database, zero configuration
- **Production-Ready**: Schema is PostgreSQL-ready with a simple connection string change
- **Sufficient for Assignment**: Handles 16 items and user data comfortably

### Why Layered Architecture?
- **Separation of Concerns**: API, Service, Repository layers have distinct responsibilities
- **Easier Testing**: Each layer can be tested independently
- **Maintainability**: Changes in one layer don't affect others
- **Scalability**: Easy to add caching, logging, or other cross-cutting concerns

### Why Repository Pattern?
- **Abstraction**: Database operations abstracted from business logic
- **Testability**: Easy to mock repositories for service layer tests
- **Reusability**: Common CRUD operations centralized
- **Consistency**: Standardized data access patterns

### Technologies Used
| Technology | Purpose |
|---|---|
| FastAPI | Modern web framework with automatic OpenAPI docs |
| SQLAlchemy | ORM for database operations with type safety |
| Alembic | Database migration management |
| Pydantic | Data validation and serialization |
| JWT | Stateless authentication |
| Python 3.11+ | Runtime environment |
| SQLite | Lightweight database (PostgreSQL-ready) |
| pytest | Testing framework |
| uvicorn | ASGI server |

---

## Architecture

### Layered Architecture
```
app/
├── api/v1/              # API endpoints (versioned)
├── services/            # Business logic layer
├── repositories/        # Data access layer
├── models/              # SQLAlchemy ORM models
├── schemas/             # Pydantic validation schemas
├── core/                # Core utilities (config, security, JWT)
├── middleware/          # Custom middleware
├── cache/               # Caching layer
├── metrics/             # Metrics collection
└── background/          # Background tasks
```

### Folder Structure
```
potens-internship-backend-Q2/
├── app/
│   ├── api/             # API endpoints
│   │   └── v1/          # Versioned API
│   ├── background/      # Background tasks
│   ├── cache/            # Caching implementation
│   ├── core/             # Core utilities
│   ├── db/               # Database configuration
│   ├── metrics/          # Metrics collection
│   ├── middleware/       # Custom middleware
│   ├── models/           # SQLAlchemy models
│   ├── repositories/     # Data access layer
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # Business logic
│   └── utils/            # Utilities
├── alembic/               # Database migrations
├── tests/                 # Test suite
├── scripts/                # Utility scripts
├── docs/                   # Documentation
│   └── screenshots/        # Swagger UI & SQLite screenshots
├── data/                   # Database files (gitignored)
├── logs/                   # Log files (gitignored)
├── .github/workflows/      # CI/CD pipeline
├── README.md
├── requirements.txt
├── alembic.ini
├── .env.example
└── .gitignore
```

### Database Design
**Users Table**
- id (Primary Key)
- username (Unique)
- email (Unique)
- hashed_password
- full_name
- is_active
- is_admin
- created_at
- updated_at

**Items Table**
- id (Primary Key)
- name
- category
- price
- skill_level
- goal
- location
- pace
- description
- created_at
- updated_at

**Indexes**
- Single-column: category, goal, location, skill_level, price, created_at
- Composite: (category, goal), (location, skill_level), (price, category)

### Recommendation Logic
The recommendation engine uses a weighted scoring system based on user profile attributes:

**Scoring Flow**
```
User Profile
     │
     ↓
Validate Input
     │
     ↓
Fetch All Catalogue Items
     │
     ↓
For Each Item:
  ├─ Goal Match?              (+4)
  ├─ Skill Level Match?       (+3)
  ├─ Beginner-Friendly?       (+2)
  ├─ Budget Fit?              (+2)
  ├─ Near-Budget Fit?         (+1)
  ├─ Location Match?          (+2)
  └─ Pace Match?              (+1)
     │
     ↓
Filter (Score ≥ 8)
     │
     ↓
Sort by Score (desc), then Date (desc)
     │
     ↓
Return Top 3 with Explanations
```

**Scoring Rules**
1. **Goal Match** (+4 points): Item goal must match user goal
2. **Skill Level Match** (+3 points): Exact skill level match
3. **Beginner-Friendly** (+2 points): Beginner users can access beginner/intermediate items
4. **Budget Fit** (+2 points): User budget >= item price
5. **Near-Budget Fit** (+1 point): User budget >= 80% of item price
6. **Location Fit** (+2 points): Location matches or item is remote
7. **Pace Fit** (+1 point): Preferred pace matches item pace

**Minimum Score**: 8 points required for recommendation
**Tie Breaker**: Higher score wins, then by creation date (newest first)
**Output**: Top 3 ranked recommendations with human-readable explanations

### API Flow
```
Client Request
     │
     ↓
JWT Authentication Middleware
     │
     ↓
Rate Limiting Check
     │
     ↓
API Endpoint (POST /recommend)
     │
     ↓
Recommendation Service
     │
     ↓
Item Repository (Fetch Catalogue)
     │
     ↓
Database (SQLite)
     │
     ↓
Scoring & Ranking
     │
     ↓
Cache Check (Redis/In-memory)
     │
     ↓
Top 3 Results with Explanations
     │
     ↓
Response to Client
```

---

## Setup Instructions

### Prerequisites
- Python 3.11+
- pip

### Installation
```bash
# Clone repository
git clone https://github.com/kamlesh9876/potens-internship-backend-Q2.git
cd potens-internship-backend-Q2

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Variables
Copy `.env.example` to `.env` and configure:
```bash
cp .env.example .env
```

Required variables:
```env
DATABASE_URL=sqlite:///data/app.db
APP_NAME=SkillPath Recommendation API
APP_VERSION=1.0.0
DEBUG=True
SECRET_KEY=your-secret-key-here
ADMIN_TOKEN=your-admin-token-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALGORITHM=HS256
```

---

## Database Setup

### Run Migrations
```bash
# Initialize Alembic (first time only)
alembic init alembic

# Run migrations
alembic upgrade head
```

### Seed Database
```bash
# Run seed script (if available)
python scripts/seed_database.py
```

---

## Run Instructions

### Development Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Example Production Command
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## API Documentation

### Swagger UI
Open [http://localhost:8000/docs](http://localhost:8000/docs) in your browser

### ReDoc
Open [http://localhost:8000/redoc](http://localhost:8000/redoc) in your browser

### Key Endpoints
| Method | Endpoint | Description | Access |
|---|---|---|---|
| POST | `/api/v1/auth/register` | Register new user | Public |
| POST | `/api/v1/auth/login` | Login and get JWT token | Public |
| POST | `/api/v1/recommend` | Get personalized recommendations | Authenticated |
| GET | `/api/v1/items` | List items | Admin |
| POST | `/api/v1/items` | Create item | Admin |
| GET | `/api/v1/items/{id}` | Get item by ID | Admin |
| PUT | `/api/v1/items/{id}` | Update item | Admin |
| DELETE | `/api/v1/items/{id}` | Delete item | Admin |
| GET | `/api/v1/explain/{item_id}` | Get explanation for item | Authenticated |
| GET | `/api/v1/health` | Health check | Public |
| GET | `/api/v1/metrics` | Application metrics | Admin |

---

## Example Requests

### Register User
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "user@example.com",
    "password": "SecurePass123",
    "full_name": "Test User"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123"
  }'
```

### Get Recommendations
```bash
curl -X POST http://localhost:8000/api/v1/recommend \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "age": 25,
    "budget": 200,
    "experience_level": "Beginner",
    "goal": "Career Change",
    "location": "Online",
    "preferred_pace": "Self-paced"
  }'
```

### Create Item (Admin)
```bash
curl -X POST http://localhost:8000/api/v1/items \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -d '{
    "name": "Python Bootcamp",
    "category": "Programming",
    "price": 99.99,
    "skill_level": "Beginner",
    "goal": "Career Change",
    "location": "Online",
    "pace": "Self-paced",
    "description": "Learn Python from scratch"
  }'
```

### List Items with Filters
```bash
curl -X GET "http://localhost:8000/api/v1/items?category=Programming&price_min=50&price_max=150&page=1&limit=10" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

### Get Item Explanation
```bash
curl -X GET http://localhost:8000/api/v1/explain/1 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## Testing

### Run All Tests
```bash
pytest tests/ -v
```

### Run with Coverage
```bash
pytest tests/ --cov=app --cov-report=term-missing
```

### Test Coverage
- **116 automated tests passing**
- Tests cover: Authentication, Recommendation Engine, CRUD Operations, Repository Layer, Service Layer, Caching, Security, Validation
- Test types: Unit tests, integration tests, security tests, boundary tests

---

## Assumptions
- SQLite database for development (PostgreSQL recommended for production)
- In-memory cache (Redis recommended for production scale)
- Single server deployment (can be scaled horizontally)
- Email service is mocked (requires SMTP configuration for production)

## Limitations
- In-memory cache is not distributed
- No real-time notifications
- Background tasks are synchronous in test environment
- Rate limiting is in-memory (not distributed)

## Future Improvements
- Migrate to PostgreSQL for production
- Implement Redis for distributed caching
- Add WebSocket support for real-time updates
- Implement webhook subscriptions
- Add comprehensive API contract testing
- Implement load testing with Locust
- Add performance benchmarks
- Implement refresh token rotation
- Add OAuth2 social login support

---

## AI Use Declaration

**Tool Used:** Cascade (AI Coding Assistant)

**Approximate Usage**
- Used throughout development for brainstorming, debugging, explaining framework behavior, improving documentation, and generating boilerplate code.

**Tasks Assisted**
- Architecture discussions
- FastAPI implementation guidance
- SQLAlchemy & Alembic debugging
- Middleware implementation ideas
- Test case suggestions
- Documentation improvements

**Declaration**
AI was used as a development assistant to accelerate implementation and problem solving. All generated code was reviewed, integrated, modified where necessary, and tested by me. I understand the architecture, business logic, and implementation of every submitted component.

---

## Phase Completion

### Phase 1: Core Requirements ✅
- Recommendation API with structured profile
- 15+ catalogue items in database
- Full CRUD operations
- Admin protection with JWT
- Explain endpoint

### Phase 2: API Quality ✅
- RESTful endpoints
- Proper HTTP methods and status codes
- Consistent response format
- Clean OpenAPI docs

### Phase 3: Recommendation Engine ✅
- Clear eligibility rules
- Weighted scoring system
- Tie breaker logic
- Deterministic output
- Explainability

### Phase 4: Production Features ✅
- Layered architecture
- Database with migrations
- Security (password hashing, JWT, rate limiting)
- Structured logging
- Caching with TTL
- API versioning
- Background tasks
- Metrics and monitoring
- Docker support
- CI/CD pipeline

### Phase 5: Testing & QA ✅
- 116 tests passing
- 69% code coverage
- Security tests
- Repository tests
- Service tests
- Cache tests
- Comprehensive documentation

---

## License
MIT License