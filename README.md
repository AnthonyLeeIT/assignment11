## Running Tests Locally

This FastAPI application uses SQLAlchemy's 'User' model and includes password hashing. It requires a running PostGres database and pushes a Docker image to Docker Hub on success. 

This module extended the work from Module 10 (assignment 10) by adding a Calculation model, Pydantic validation schemas, an operation factory, along with unit and integration tests that exercise them.

### 1. Set up the environment

Create and activate a virtual environment, then install dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Install the Playwright browser used by the E2E tests:

```bash
playwright install chromium
```

### 2. Start the database

The integration and E2E tests connect to PostgreSQL. Start it with Docker Compose:

```bash
docker compose up
```

The app reads its connection string from the `DATABASE_URL` environment variable
(set in a `.env` file at the project root), for example:

```
DATABASE_URL=postgresql://user:password@localhost:5432/mytestdb
```

### 3. Run the tests

Run the full suite:

```bash
pytest
```

Run with a coverage report:

```bash
pytest --cov=app --cov-report=term-missing
```

Target a single layer if you prefer:

```bash
pytest tests/unit/           # fast, no database required
pytest tests/integration/    # requires PostgreSQL
pytest tests/e2e/            # requires PostgreSQL + Playwright
```

Slow tests are skipped by default; include them with `pytest --run-slow`.

A successful run looks like:

```
74 passed, 1 skipped
```

(The single skipped test is a bulk-insert test marked `slow`.)

## Docker Hub

The application image is built and pushed automatically by the CI/CD pipeline on
every successful push to `main`.

**Docker Hub repository:** https://hub.docker.com/r/ahl3389/assignment10

To pull the published image:

```bash
docker pull ahl3389/assignment10:latest
```

To run the full application (web app + database) locally:

```bash
docker compose up --build
```

Then open http://localhost:8000 in your browser.
Or http://localhost:5050 for viewing the Page Admin.