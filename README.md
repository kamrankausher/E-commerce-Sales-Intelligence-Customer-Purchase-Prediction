# E-commerce Growth Intelligence Platform

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688.svg)
![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED.svg)
![GitHub Actions](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF.svg)
![Pytest](https://img.shields.io/badge/Pytest-20%2B%20Tests-0A9EDC.svg)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57.svg)

## Project Overview

The **E-commerce Growth Intelligence Platform** is a scalable, containerized backend API built with Python, FastAPI, and SQLite. It provides advanced analytical insights into e-commerce operations, encompassing revenue trends, cohort retention, delivery performance, and Customer Lifetime Value (CLV).

Designed with software engineering best practices, this project mimics a real-world data pipeline and API service. It features a fully automated CI/CD pipeline using GitHub Actions, comprehensive automated testing with Pytest, and is containerized via Docker for seamless deployment.

## Features

- **Scalable REST API**: Built with FastAPI for high performance and automatic interactive documentation (Swagger UI).
- **Advanced SQL Analytics**: Utilizes Common Table Expressions (CTEs), Window Functions, and aggregations to extract complex insights from 18,000+ records.
- **Robust Testing**: Engineered 20+ automated Pytest test cases covering API endpoints, database interactions, edge cases, and business logic.
- **Docker Containerization**: Includes a multi-stage `Dockerfile` and `docker-compose.yml` for isolated and reproducible builds.
- **Automated CI/CD**: Integrated GitHub Actions workflow for automated linting, testing, and Docker image validation on every push.
- **Clean Architecture**: Follows best practices with separated routing, services, database connection handling, and Pydantic schema validation.

## Architecture Diagram

```mermaid
graph TD;
    A[Client Request] --> B(FastAPI Server)
    B --> C{Routers (app/routers)}
    C --> D[Pydantic Validation (app/schemas)]
    D --> E[Analytics Service (app/services)]
    E --> F[Database Layer (app/database)]
    F --> G[(SQLite Database)]
    G --> F
    F --> E
    E --> C
    C --> B
    B --> A
```

## Folder Structure

```text
project/
├── app/
│   ├── database/       # Database connection handling
│   ├── routers/        # API route definitions
│   ├── schemas/        # Pydantic data validation models
│   ├── services/       # Business logic and SQL execution
│   └── main.py         # FastAPI application entry point
├── dashboard/          # Frontend HTML/JS/CSS assets
├── data/               # Raw datasets and SQLite database
├── docs/               # Project documentation and reports
├── sql/                # Advanced analytical SQL queries
├── tests/              # Pytest automated test cases
├── .github/workflows/  # CI/CD pipeline configuration
├── docker-compose.yml  # Docker Compose configuration
├── Dockerfile          # Multi-stage Docker image build
├── requirements.txt    # Python dependencies
├── setup.py            # Automated setup script
└── README.md           # Project documentation
```

## Installation and Setup

### Requirements
- Python 3.11+
- Docker (optional, but recommended)

### Running Locally (Without Docker)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/kamrankausher/ecommerce-intelligence.git
   cd ecommerce-intelligence
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the setup script (Generates Data & DB):**
   ```bash
   python setup.py
   ```

5. **Start the FastAPI Server:**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

### Running with Docker

1. **Build and run the container:**
   ```bash
   docker-compose up --build
   ```

2. **Access the API:**
   Navigate to `http://localhost:8000/docs` to view the interactive Swagger UI.

## API Endpoints

The API is versioned under `/api/v1` and includes the following endpoints:

- `GET /health` - API Health check.
- `GET /api/v1/revenue-by-state` - Top 10 states by revenue.
- `GET /api/v1/monthly-revenue-trend` - Month-over-month revenue growth.
- `GET /api/v1/cohort-analysis` - Monthly acquisition cohort retention.
- `GET /api/v1/repeat-purchase-rate` - Percentage of repeat customers.
- `GET /api/v1/top-sellers` - Highest revenue-generating sellers.
- `GET /api/v1/monthly-retention-rate` - Customer retention by month.
- `GET /api/v1/category-performance` - Top product categories by revenue.
- `GET /api/v1/delivery-performance` - On-time vs late delivery analysis.
- `GET /api/v1/rfm-segmentation` - Customer segmentation (Recency, Frequency, Monetary).
- `GET /api/v1/payment-method-analysis` - Revenue grouped by payment types.
- `GET /api/v1/clv-distribution` - Customer Lifetime Value distribution metrics.
- `GET /api/v1/review-sentiment` - Sentiment and score breakdown by product category.

## Testing

The project uses `pytest` for unit and integration testing, boasting a suite of 20+ comprehensive tests.

To run the tests with coverage:
```bash
pytest tests/ -v --cov=app
```

## CI/CD

The `.github/workflows/ci.yml` pipeline automates the following on every push to `main`:
1. Environment setup and dependency installation.
2. Database generation and initialization.
3. Execution of the Pytest suite.
4. Docker image build and container health check verification.

## Future Improvements

- Migrate SQLite database to PostgreSQL for production environments.
- Implement token-based authentication (OAuth2/JWT) to secure analytics endpoints.
- Enhance the dashboard with dynamic React/Vue.js components querying the API in real-time.
- Add Redis caching for expensive analytical queries.

## License

This project is licensed under the MIT License.
