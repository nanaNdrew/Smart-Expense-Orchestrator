# Smart Expense Orchestrator

A high-performance backend microservice designed to asynchronously process receipt uploads and extract structured financial data using OpenAI's GPT-4o.

## Features
- **Asynchronous Ingestion:** Upload endpoints immediately return a task ID, decoupling the ingestion phase from heavy LLM processing.
- **Robust Background Processing:** Built with Celery and Redis to handle concurrent task processing and retries.
- **AI Integration:** Leverages GPT-4o with structured output extraction for Merchants, Dates, Totals, Taxes, Currencies, and Line-Item breakdowns.
- **Strict Data Validation:** Utilizes Pydantic to ensure all data from the LLM is correctly structured before hitting the database.
- **Async Database:** Uses PostgreSQL with `asyncpg` and SQLAlchemy 2.0 for maximum non-blocking throughput.
- **Production Ready DX:** Fully containerized with Docker, complete with a `Makefile`, Ruff linting, MyPy static typing, and automated integration tests via Pytest.

## Tech Stack
- **Python 3.11+**
- **FastAPI**
- **PostgreSQL** (SQLAlchemy & Alembic)
- **Redis** & **Celery**
- **OpenAI API**
- **Docker Compose**

## Quick Start

### 1. Configuration
Create your environment file:
```bash
cp .env.example .env
```
Open `.env` and configure your `OPENAI_API_KEY`.

### 2. Run the Application
The easiest way to interact with the project is via the provided `Makefile`.

Spin up all services (Web, Worker, DB, Redis):
```bash
make up
```

### 3. Run Database Migrations
Generate and apply the initial database schema (if not already applied):
```bash
make migrate m="initial_migration"
make upgrade
```

### 4. API Usage

#### Upload a Receipt
```bash
curl -X POST -F "file=@/path/to/receipt.jpg" http://localhost:8000/api/v1/receipts/upload
```
**Response:**
```json
{
  "task_id": "abc-123",
  "status": "PENDING",
  "message": "Receipt uploaded and queued for processing"
}
```

#### Check Status & Fetch Data
```bash
curl http://localhost:8000/api/v1/receipts/abc-123
```
**Response:** *(Once Processed)*
```json
{
  "id": 1,
  "task_id": "abc-123",
  "status": "COMPLETED",
  "merchant_name": "Example Store",
  "total_amount": 42.50,
  "tax_amount": 3.10,
  "currency": "USD",
  "line_items": [
    {
      "id": 1,
      "description": "Coffee",
      "quantity": 1.0,
      "unit_price": 4.50
    }
  ]
}
```

## Developer Tools

Run linting (Ruff + MyPy):
```bash
make lint
```

Format code:
```bash
make format
```

Run tests:
```bash
make test
```

Tear down services:
```bash
make down
```
