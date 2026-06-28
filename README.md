# E-commerce Growth Intelligence Platform 🚀

A scalable, containerized Python FastAPI backend providing robust analytics and business intelligence on e-commerce transaction data.

## Project Overview
This project serves as a comprehensive backend analytics engine for an e-commerce platform. It leverages **FastAPI** to serve metrics, **SQLite** for data storage, and **Docker** for seamless deployment. The core of the platform is powered by **12 advanced SQL queries** that calculate crucial business KPIs such as Cohort Retention, RFM Segmentation, and Customer Lifetime Value (CLV).

## Features
- **FastAPI Backend:** High-performance, fully typed REST API with auto-generated Swagger UI.
- **Advanced SQL Analytics:** 12 complex queries utilizing CTEs and window functions for deep business insights.
- **Comprehensive Testing:** 20+ automated Pytest test cases covering positive, negative, and edge cases.
- **CI/CD Pipeline:** Fully automated GitHub Actions workflow for linting, testing, and building Docker images.
- **Dockerized:** Clean, multi-stage Docker build for easy environment replication.

## Folder Structure
```text
project/
├── app/                  # FastAPI application code
│   ├── main.py           # Application entry point
│   ├── database.py       # DB connection and query executor
│   ├── routers/          # API endpoint routes
│   └── utils/            # Shared utilities (logging)
├── data/                 # Raw datasets and SQLite database
├── docs/                 # Project documentation and reports
├── sql/                  # The 12 advanced analytics queries
├── tests/                # 20+ Pytest cases
├── .github/workflows/    # CI/CD configuration
├── docker-compose.yml    # Docker services config
├── Dockerfile            # Multi-stage image build instructions
├── requirements.txt      # Python dependencies
└── setup.py              # Initial environment setup script
```

## Quick Start

### 1. Run Locally (Python)
1. **Create Virtual Environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Initialize Database:**
   ```bash
   python setup.py
   ```
4. **Start the API:**
   ```bash
   uvicorn app.main:app --reload
   ```
5. **View Documentation:** Open `http://localhost:8000/docs` in your browser.

### 2. Run via Docker
```bash
docker-compose up --build
```
The API will be available at `http://localhost:8000`.

## Testing
To run the automated test suite:
```bash
python -m pytest tests/ -v
```

## Future Improvements
- Migrate from SQLite to PostgreSQL for better concurrency handling.
- Implement Redis caching for high-latency analytical endpoints.
- Add JWT-based authentication for secure API access.

## License
MIT License
