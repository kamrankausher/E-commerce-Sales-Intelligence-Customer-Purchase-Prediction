# Security Report

## 1. Overview
An evaluation of the platform's security posture, keeping in mind the expectations of a CS fresher project.

## 2. Threat Models & Mitigation

### A. SQL Injection (SQLi)
- **Risk:** Malicious users injecting code into database inputs.
- **Mitigation:** The application routes are currently `GET` endpoints executing hardcoded analytical queries. The database connection utility supports parameterized tuples `(?, ?)` for any future dynamic inputs.

### B. Cross-Origin Resource Sharing (CORS)
- **Risk:** Unintended web domains accessing the API.
- **Current State:** The `main.py` utilizes a wildcard `["*"]` for `allow_origins`.
- **Recommendation:** While perfectly acceptable for a local development project or a portfolio demo, a production environment should explicitly list frontend origins (e.g., `["https://mydomain.com"]`).

### C. Secrets Management
- **Risk:** Hardcoding credentials in Git.
- **Mitigation:** The project uses an `.env.example` file and pulls variables like `API_PORT` dynamically. Because it uses local SQLite, there are no sensitive database URI strings committed to the repository.

### D. Code Execution
- No unsafe `eval()` or `exec()` blocks exist in the codebase.
- Path traversal is avoided since the `SQL_DIR` absolute path is statically built using `os.path.dirname` inside `config.py`.

## 3. Conclusion
The project is structurally secure and follows standard backend security precautions.
