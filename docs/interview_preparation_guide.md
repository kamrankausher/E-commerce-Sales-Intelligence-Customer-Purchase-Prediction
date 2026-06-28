# Interview Preparation Guide

This guide prepares you for technical interviews based on your E-commerce Growth Intelligence Platform project. 

---

## 1. FastAPI & Architecture

**Q: Why did you choose FastAPI over Flask or Django?**
- **Ideal Answer:** I chose FastAPI because it is modern, incredibly fast (built on Starlette), and natively supports asynchronous programming. It also automatically generates Swagger UI documentation, and its deep integration with Pydantic makes request/response validation seamless.
- **Follow-up:** How does Pydantic help?
- **Answer:** It enforces strict typing and schemas. If my API expects an integer and gets a string, Pydantic catches it immediately, returning a 422 error before it even hits my business logic.

**Q: Can you explain your folder structure?**
- **Ideal Answer:** I structured the project following separation of concerns. `routers/` handles HTTP traffic. `services/` contains the business logic (parsing SQL). `database/` manages SQLite connections. `schemas/` handles data validation. This makes the codebase maintainable and scalable.

---

## 2. SQL & Analytics

**Q: You mentioned using CTEs and Window Functions. Give an example from your project.**
- **Ideal Answer:** To calculate Month-over-Month revenue growth, I first used a CTE to group total revenue by month using `strftime`. Then, in the main query, I used the `LAG()` window function to pull the previous month's revenue into the current row, allowing me to easily calculate the percentage difference.
- **Follow-up:** What happens if the dataset gets much larger?
- **Answer:** SQLite is fine for small/medium local datasets. If it grew massively, I'd migrate to PostgreSQL. To optimize, I ensured all heavy JOIN columns in my SQLite database had explicit indexes created during setup.

---

## 3. Docker & CI/CD

**Q: Walk me through your Docker setup.**
- **Ideal Answer:** I wrote a multi-stage Dockerfile. Stage 1 installs dependencies and compiles them using a builder image. Stage 2 copies only the necessary files into a lightweight runtime image (`python:3.11-slim`), reducing image size and attack surface.
- **Follow-up:** What does your GitHub Actions pipeline do?
- **Answer:** It automates my testing. On every push to main, it spins up an Ubuntu runner, sets up Python, installs dependencies, builds the local SQLite database, runs my 20+ Pytest suite, and finally builds the Docker image to ensure there are no build-time errors.

---

## 4. Testing

**Q: What exactly do your 20+ Pytest tests cover?**
- **Ideal Answer:** I didn't just test the "happy path." I wrote tests for all 12 analytical endpoints to ensure data formatting. I also wrote negative tests: querying invalid endpoints (404), using wrong HTTP methods like POST (405), and intentionally requesting out-of-bounds data to ensure my exception handling returns a safe 500 error instead of crashing the app.

---

## 5. Potential Pitfalls / Mistakes to Avoid in Interviews
- **Don't** say "I used SQLite because it's the best database." Say "I used it because it's portable, serverless, and perfect for a demonstration project."
- **Don't** act like you wrote everything manually if you used ORMs. (Note: You wrote raw SQL here, so proudly emphasize that you know *raw SQL*, which many candidates lack!).
- **Be ready** to explain what a CTE is: It's essentially a temporary result set that you can reference within a `SELECT`, `INSERT`, `UPDATE`, or `DELETE` statement.
