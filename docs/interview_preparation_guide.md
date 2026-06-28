# Interview Preparation Guide

This guide prepares you to confidently discuss the E-commerce Growth Intelligence Platform project in a technical interview.

## 1. FastAPI & Architecture
**Q: Why did you choose FastAPI over Flask or Django?**
**Ideal Answer:** I chose FastAPI because it is incredibly fast, natively supports asynchronous programming, and automatically generates interactive API documentation (Swagger/OpenAPI). Django would have been too heavy for a simple data-serving API, and FastAPI offers better type-hinting support than Flask out of the box using Pydantic.
**Common Mistake:** Saying "because it's the best" without providing technical context like async support or Pydantic validation.

## 2. SQL & Database Design
**Q: You mentioned writing 12 advanced SQL queries. Can you explain how you approached cohort analysis or retention logic?**
**Ideal Answer:** For the cohort analysis, I used Common Table Expressions (CTEs). First, I created a CTE to determine the absolute first purchase month for each customer. Then, I joined that CTE against their subsequent orders to calculate the month-offset (the difference in months between the first purchase and the current order). Grouping by the cohort month and the offset allowed me to track retention degradation over time.
**Follow-up:** How did you optimize this? (Answer: By ensuring indexes on `customer_id` and `order_purchase_timestamp` and pushing the aggregations to the DB instead of doing it in Python).

## 3. Docker & Containerization
**Q: Explain your Docker setup. What is a multi-stage build and why did you use it?**
**Ideal Answer:** I used Docker to ensure the API runs consistently regardless of the host environment. I utilized a multi-stage build in my `Dockerfile` to keep the final image size small. The first stage (the 'builder') installs the system dependencies and compiles the Python packages, and the second stage only copies the compiled binaries and application code over, leaving behind the heavy build tools.

## 4. Pytest & CI/CD
**Q: Your resume states you engineered 20+ Pytest cases and set up GitHub Actions. Walk me through your CI/CD pipeline.**
**Ideal Answer:** The GitHub Actions pipeline is triggered on every push or Pull Request to the main branch. The first job checks out the code, sets up Python, installs dependencies, and runs the Pytest suite (which tests API responses, database connections, and edge cases like invalid endpoints). If the tests pass, the second job builds the Docker image and performs a health check to ensure the container starts correctly.

## 5. System Design & Future Improvements
**Q: How would you scale this application if the data grew to 50 million records?**
**Ideal Answer:** Since SQLite is file-based, it would become a bottleneck under high concurrency or massive data volume. I would migrate the database to a dedicated PostgreSQL instance on AWS RDS. I would also introduce Redis for caching the most frequently requested KPI endpoints, and put the FastAPI instances behind a load balancer to handle incoming traffic horizontally.
