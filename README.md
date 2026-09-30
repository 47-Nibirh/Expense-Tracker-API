# Expense Tracker API

A Personal Expense Tracker API built according to the Module 24 requirements.

## Stack

- FastAPI
- SQLAlchemy ORM
- PostgreSQL for application persistence
- JWT authentication
- Pydantic validation
- Pytest
- Render deployment configuration

## Features

- User registration with password hashing
- JWT login
- Protected transaction CRUD
- Per-user transaction ownership checks
- Transaction filtering by type, category, minimum amount and maximum amount
- Automated API tests

## Project structure

```text
expense_tracker_api/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   ├── dependencies.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── security.py
│   └── routers/
│       ├── __init__.py
│       ├── auth.py
│       └── transactions.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_security_and_filtering.py
│   └── test_transactions.py
├── .env.example
├── .gitignore
├── render.yaml
├── requirements.txt
└── README.md
```

## Local setup

1. Create a PostgreSQL database named `expense_tracker`.
2. Create and activate a virtual environment.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set environment variables. On Windows PowerShell:

```powershell
$env:DATABASE_URL="postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/expense_tracker"
$env:SECRET_KEY="your-long-random-secret"
```

5. Start the API:

```bash
uvicorn app.main:app --reload
```

6. Open Swagger UI at `/docs`.

## Test

```bash
pytest -q
```

The automated tests override the database dependency with an isolated SQLite database. The actual application configuration remains PostgreSQL-based.

## Main endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/auth/register` | Register user |
| POST | `/auth/login` | Login and receive JWT |
| POST | `/transactions` | Create transaction |
| GET | `/transactions` | Get current user's transactions |
| GET | `/transactions/{transaction_id}` | Get one owned transaction |
| PUT | `/transactions/{transaction_id}` | Update one owned transaction |
| DELETE | `/transactions/{transaction_id}` | Delete one owned transaction |
| GET | `/transactions/filter` | Filter current user's transactions |

## Render deployment

Set these environment variables on Render:

- `DATABASE_URL`: your Render PostgreSQL connection string
- `SECRET_KEY`: a strong secret (Render can generate one)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: `60`

Build command:

```text
pip install -r requirements.txt
```

Start command:

```text
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```
