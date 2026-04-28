# Finance Tracker API

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
python run.py