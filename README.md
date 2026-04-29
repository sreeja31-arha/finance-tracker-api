<!-- # Finance Tracker API

A production-grade REST API built with Flask and PostgreSQL.

## Features
- JWT Authentication
- Full CRUD for transactions
- Spending Analytics
- Input Validation
- Error Handling
- Docker support

## Tech Stack
- Python 3.14
- Flask
- PostgreSQL
- SQLAlchemy
- JWT
- Docker

## API Endpoints

### Auth
- POST /auth/register - Register a new user
- POST /auth/login - Login and get JWT token

### Transactions
- GET /transactions - Get all transactions
- POST /transactions - Add a transaction
- PUT /transactions/<id> - Update a transaction
- DELETE /transactions/<id> - Delete a transaction

### Analytics
- GET /transactions/analytics - Get spending analytics

## Setup

### 1. Clone the repository
git clone https://github.com/sreeja31-arha/finance-tracker-api.git

### 2. Create virtual environment
python -m venv venv
venv\Scripts\activate

### 3. Install dependencies
pip install -r requirements.txt

### 4. Run the app
python run.py -->



#  Finance Tracker API

A RESTful API built with **Flask** and **PostgreSQL** for tracking personal finances — income, expenses, and analytics. Features JWT authentication, structured logging, database migrations, automated tests, and CI/CD with GitHub Actions.

---

##  Features

- **JWT Authentication** — Secure register and login with JSON Web Tokens
- **Transaction Management** — Create, read, update, and delete income/expense transactions
- **Analytics** — Total income, total expenses, net balance, and category breakdown
- **API Versioning** — All endpoints under `/api/v1/`
- **Structured Logging** — Terminal + rotating file logs with configurable log levels
- **Database Migrations** — Alembic/Flask-Migrate for safe schema changes
- **Automated Tests** — 17 pytest tests covering all endpoints
- **CI/CD** — GitHub Actions automatically runs tests on every push

---

##  Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11 |
| Framework | Flask |
| Database | PostgreSQL (production), SQLite (testing) |
| ORM | Flask-SQLAlchemy |
| Authentication | Flask-JWT-Extended |
| Validation | Marshmallow |
| Migrations | Flask-Migrate (Alembic) |
| Testing | pytest |
| CI/CD | GitHub Actions |
| Password Hashing | Werkzeug |

---

##  Project Structure

```
finance-tracker/
├── .github/
│   └── workflows/
│       └── tests.yml          # GitHub Actions CI workflow
├── app/
│   ├── __init__.py            # App factory, extensions, blueprints
│   ├── auth.py                # Register and login endpoints
│   ├── config.py              # Environment-based configuration
│   ├── logging_config.py      # Logging setup (terminal + file)
│   ├── models.py              # User and Transaction database models
│   ├── routes.py              # Transaction CRUD + analytics endpoints
│   └── schemas.py             # Marshmallow validation schemas
├── migrations/                # Alembic migration files
├── tests/
│   ├── conftest.py            # pytest fixtures (test client, auth client)
│   ├── test_auth.py           # Register and login tests
│   └── test_transactions.py   # Transaction endpoint tests
├── logs/                      # Auto-created, rotating log files
├── .env.example               # Environment variable template
├── .gitignore
├── app.py                     # App entry point
├── requirements.txt
└── run.py                     # Development server runner
```

---

##  Setup & Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/finance-tracker.git
cd finance-tracker
```

### 2. Create and activate virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

```env
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
SQLALCHEMY_DATABASE_URI=postgresql://username:password@localhost:5432/finance_tracker
LOG_LEVEL=DEBUG
```

### 5. Set up the database

```bash
flask db upgrade
```

### 6. Run the development server

```bash
python run.py
```

The API will be available at `http://localhost:5000`

---

##  API Endpoints

### Authentication

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| POST | `/api/v1/auth/register` | Register a new user | No |
| POST | `/api/v1/auth/login` | Login and receive JWT token | No |

### Transactions

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| GET | `/api/v1/transactions` | Get all transactions | ✅ Yes |
| POST | `/api/v1/transactions` | Create a new transaction | ✅ Yes |
| PUT | `/api/v1/transactions/<id>` | Update a transaction | ✅ Yes |
| DELETE | `/api/v1/transactions/<id>` | Delete a transaction | ✅ Yes |
| GET | `/api/v1/transactions/analytics` | Get income/expense summary | ✅ Yes |

---

##  Request & Response Examples

### Register

**Request:**
```json
POST /api/v1/auth/register
{
    "username": "john",
    "email": "john@example.com",
    "password": "password123"
}
```

**Response:** `201 Created`
```json
{
    "message": "User registered successfully!",
    "user": {
        "id": 1,
        "username": "john",
        "email": "john@example.com",
        "created_at": "2024-01-15 10:23:45"
    }
}
```

---

### Login

**Request:**
```json
POST /api/v1/auth/login
{
    "email": "john@example.com",
    "password": "password123"
}
```

**Response:** `200 OK`
```json
{
    "message": "Login successful!",
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
        "id": 1,
        "username": "john",
        "email": "john@example.com"
    }
}
```

---

### Add Transaction

**Request:**
```json
POST /api/v1/transactions
Authorization: Bearer <your_token>

{
    "title": "Monthly Salary",
    "amount": 5000.00,
    "type": "income",
    "category": "work"
}
```

**Response:** `201 Created`
```json
{
    "message": "Transaction added successfully!",
    "transaction": {
        "id": 1,
        "title": "Monthly Salary",
        "amount": 5000.0,
        "type": "income",
        "category": "work",
        "created_at": "2024-01-15 10:30:00"
    }
}
```

---

### Analytics

**Request:**
```
GET /api/v1/transactions/analytics
Authorization: Bearer <your_token>
```

**Response:** `200 OK`
```json
{
    "total_income": 5000.0,
    "total_expense": 2000.0,
    "net_balance": 3000.0,
    "categories": {
        "housing": 1500.0,
        "food": 500.0
    }
}
```

---

##  Running Tests

```bash
pytest tests/ -v
```

**Expected output:**
```
tests/test_auth.py::test_register_success                    PASSED
tests/test_auth.py::test_register_duplicate_email            PASSED
tests/test_auth.py::test_register_duplicate_username         PASSED
tests/test_auth.py::test_register_missing_fields             PASSED
tests/test_auth.py::test_register_missing_password           PASSED
tests/test_auth.py::test_login_success                       PASSED
tests/test_auth.py::test_login_wrong_password                PASSED
tests/test_auth.py::test_login_nonexistent_user              PASSED
tests/test_auth.py::test_login_missing_fields                PASSED
tests/test_transactions.py::test_add_transaction_without_token     PASSED
tests/test_transactions.py::test_get_transactions_without_token    PASSED
tests/test_transactions.py::test_add_transaction_success           PASSED
tests/test_transactions.py::test_add_transaction_missing_fields    PASSED
tests/test_transactions.py::test_add_transaction_without_category  PASSED
tests/test_transactions.py::test_get_transactions_empty            PASSED
tests/test_transactions.py::test_get_transactions_returns_correct_data PASSED
tests/test_transactions.py::test_update_transaction_success        PASSED
tests/test_transactions.py::test_update_nonexistent_transaction    PASSED
tests/test_transactions.py::test_delete_transaction_success        PASSED
tests/test_transactions.py::test_delete_nonexistent_transaction    PASSED
tests/test_transactions.py::test_analytics_correct_calculation     PASSED

17 passed in 2.31s
```

Tests use an **in-memory SQLite database** — no PostgreSQL required to run tests.

---

##  Database Migrations

When you change `models.py`, update the database with:

```bash
# Generate migration file
flask db migrate -m "describe your change"

# Apply migration to database
flask db upgrade
```

To roll back the last migration:
```bash
flask db downgrade
```

---

##  Logging

Logs are written to two places simultaneously:

| Destination | Level | Location |
|---|---|---|
| Terminal | INFO and above | Console output |
| File | DEBUG and above | `logs/app.log` |

Log files auto-rotate at 5MB and keep 3 backups. Configure the log level in `.env`:

```env
LOG_LEVEL=DEBUG    # Shows everything
LOG_LEVEL=INFO     # Shows normal operations
LOG_LEVEL=WARNING  # Shows only warnings and errors
```

---

##  CI/CD

GitHub Actions automatically runs all 17 tests on every push to `main` or `develop`.

**Workflow:** `.github/workflows/tests.yml`

```
git push → GitHub Actions triggers → Ubuntu machine created →
Python installed → Dependencies installed → pytest runs →
✅ Green checkmark (all pass) or ❌ Red X (something broke)
```

---

##  Environment Variables

| Variable | Description | Example |
|---|---|---|
| `FLASK_ENV` | Environment mode | `development` |
| `SECRET_KEY` | Flask secret key | `your-secret-key` |
| `JWT_SECRET_KEY` | JWT signing key | `your-jwt-key` |
| `SQLALCHEMY_DATABASE_URI` | PostgreSQL connection URL | `postgresql://user:pass@localhost/db` |
| `LOG_LEVEL` | Logging level | `DEBUG` |

---

##  Author

Built as a learning project covering Flask API development, PostgreSQL, JWT authentication, logging, database migrations, testing, and CI/CD.
