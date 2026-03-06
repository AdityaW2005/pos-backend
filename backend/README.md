# Restaurant POS SaaS – Backend API

Production-grade **FastAPI** backend for a multi-tenant restaurant Point of Sale platform.

## Tech Stack

| Layer      | Technology                 |
| ---------- | -------------------------- |
| Framework  | FastAPI                    |
| ORM        | SQLAlchemy 2.0 (async)     |
| Database   | PostgreSQL (via asyncpg)   |
| Migrations | Alembic                    |
| Auth       | JWT (python-jose) + bcrypt |
| Validation | Pydantic v2                |

---

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Settings from env vars
│   ├── database.py          # Async engine & session
│   ├── models/              # SQLAlchemy ORM models
│   │   ├── users.py
│   │   ├── stores.py
│   │   ├── products.py
│   │   └── orders.py
│   ├── schemas/             # Pydantic request/response models
│   │   ├── user_schema.py
│   │   ├── product_schema.py
│   │   └── order_schema.py
│   ├── routers/             # FastAPI route handlers
│   │   ├── auth_routes.py
│   │   ├── store_routes.py
│   │   ├── employee_routes.py
│   │   ├── product_routes.py
│   │   ├── order_routes.py
│   │   └── analytics_routes.py
│   ├── services/            # Business logic
│   │   ├── order_service.py
│   │   └── sync_service.py
│   └── utils/               # Helpers (JWT, bcrypt)
│       ├── auth.py
│       └── security.py
├── alembic/                 # Migration scripts
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
├── alembic.ini
├── requirements.txt
├── .env.example
└── README.md
```

---

## Getting Started

### 1. Prerequisites

- Python 3.11+
- PostgreSQL 15+

### 2. Create the database

```bash
# Connect to PostgreSQL and run:
CREATE USER pos_user WITH PASSWORD 'pos_password';
CREATE DATABASE pos_db OWNER pos_user;
```

### 3. Set up environment

```bash
cd backend

# Create a virtual environment
python -m venv venv
source venv/bin/activate   # macOS/Linux
# venv\Scripts\activate    # Windows

# Install dependencies
pip install -r requirements.txt

# Configure env vars
cp .env.example .env
# Edit .env with your database credentials & a strong JWT secret
```

### 4. Run database migrations

```bash
# Generate the initial migration (first time only)
alembic revision --autogenerate -m "initial schema"

# Apply migrations
alembic upgrade head
```

> **Note:** On first startup the app also auto-creates tables via
> `Base.metadata.create_all` for convenience. Use Alembic for all
> subsequent schema changes.

### 5. Start the server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API is now live at **http://localhost:8000**.

---

## API Documentation

FastAPI auto-generates interactive docs:

| UI             | URL                         |
| -------------- | --------------------------- |
| **Swagger UI** | http://localhost:8000/docs  |
| **ReDoc**      | http://localhost:8000/redoc |

---

## Example API Requests

### Register a user

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Tejas Prasad",
    "email": "tejas@example.com",
    "phone": "+919876543210",
    "password": "Str0ngP@ss!"
  }'
```

### Login

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "tejas@example.com",
    "password": "Str0ngP@ss!"
  }'
# Response: { "access_token": "<JWT>", "token_type": "bearer" }
```

### Create a store

```bash
curl -X POST http://localhost:8000/stores \
  -H "Authorization: Bearer <JWT>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Downtown Bistro",
    "location": "123 MG Road, Bangalore"
  }'
```

### Create a category

```bash
curl -X POST http://localhost:8000/products/categories \
  -H "Authorization: Bearer <JWT>" \
  -H "Content-Type: application/json" \
  -d '{
    "store_id": "<STORE_UUID>",
    "name": "Beverages"
  }'
```

### Create a product

```bash
curl -X POST http://localhost:8000/products \
  -H "Authorization: Bearer <JWT>" \
  -H "Content-Type: application/json" \
  -d '{
    "store_id": "<STORE_UUID>",
    "category_id": "<CATEGORY_UUID>",
    "name": "Paneer Butter Masala",
    "price": 299.00,
    "tax_percent": 5.0
  }'
```

### Create an order

```bash
curl -X POST http://localhost:8000/orders \
  -H "Authorization: Bearer <JWT>" \
  -H "Content-Type: application/json" \
  -d '{
    "store_id": "<STORE_UUID>",
    "order_type": "dine_in",
    "discount_amount": 0,
    "items": [
      { "product_id": "<PRODUCT_UUID>", "quantity": 2, "price": 299.00 }
    ]
  }'
```

### Record a payment

```bash
curl -X POST http://localhost:8000/orders/payments \
  -H "Authorization: Bearer <JWT>" \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": "<ORDER_UUID>",
    "payment_method": "upi",
    "amount": 627.90
  }'
```

### Sync offline orders

```bash
curl -X POST http://localhost:8000/sync/orders \
  -H "Authorization: Bearer <JWT>" \
  -H "Content-Type: application/json" \
  -d '{
    "orders": [
      {
        "device_id": "IPAD-A1B2C3",
        "store_id": "<STORE_UUID>",
        "order_type": "takeaway",
        "discount_amount": 0,
        "items": [
          { "product_id": "<PRODUCT_UUID>", "quantity": 1, "price": 150.00 }
        ],
        "created_at": "2026-03-05T14:30:00Z"
      }
    ]
  }'
```

### Get analytics

```bash
curl "http://localhost:8000/analytics/summary?store_id=<STORE_UUID>&start_date=2026-03-01&end_date=2026-03-31" \
  -H "Authorization: Bearer <JWT>"
```

---

## Database Schema (ER Summary)

```
Users 1──* Stores 1──* POSTerminals
                  1──* Employees
                  1──* Categories 1──* Products
                  1──* DineInTables
                  1──* Orders 1──* OrderItems ──1 Product
                         1──* Payments
                  1──* Expenses
```

All primary keys are **UUID v4**. Foreign keys use `ON DELETE CASCADE` or `SET NULL` as appropriate.

---

## Production Checklist

- [ ] Set a strong random `JWT_SECRET_KEY`
- [ ] Restrict `CORS` origins to your domain(s)
- [ ] Use connection pooling (PgBouncer) if needed
- [ ] Run behind a reverse proxy (nginx / Caddy)
- [ ] Enable HTTPS
- [ ] Set `DEBUG=false`
- [ ] Configure log aggregation
