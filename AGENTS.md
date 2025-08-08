# Repository Guidelines

## Project Structure & Module Organization
```
app/            # FastAPI app (entry: main.py)
templates/      # Jinja2 HTML templates (index.html)
static/         # Static assets (mounted at /static)
scripts/        # Helper scripts (dev.sh)
tests/          # Pytest test suite
pyproject.toml  # Project config and dependencies
README.md       # Setup and usage
AGENTS.md       # Contributor guide (this file)
```
- Application entrypoint: `app/main.py` exposes `app`.
- Keep new routes in `app/` modules; templates in `templates/`.

## Build, Test, and Development Commands
- Install deps (uv): `uv sync` (add dev tools: `uv sync --extra dev`)
- Run dev server (reload): `uv run uvicorn app.main:app --reload`
- Or via script: `uv run ./scripts/dev.sh`
- Run tests: `uv run pytest -q`
- Optional pip alternative: create venv and install `fastapi "uvicorn[standard]" jinja2 pytest httpx`, then run `uvicorn ...` or `pytest`.

## Coding Style & Naming Conventions
- Python: PEP 8, 4-space indentation, limit lines to ~100 chars.
- Names: modules/files `snake_case.py`, classes `CamelCase`, functions/vars `snake_case`.
- Type hints encouraged; add concise docstrings for public functions.
- Templates: prefer small, composable templates; keep inline CSS minimal.

## Testing Guidelines
- Framework: `pytest` with FastAPI `TestClient`.
- Location: all tests in `tests/`; files named `test_*.py`.
- Aim: cover new routes, response codes, and basic rendering.
- Run locally: `pytest -q`. Add fixtures when tests share setup.

## Commit & Pull Request Guidelines
- Commits: imperative, concise subject (≤72 chars), e.g., "Add health check endpoint".
- Include context in body when helpful; reference issues with `#123`.
- PRs: clear description of changes, rationale, and testing notes; include screenshots for UI changes.
- Keep PRs focused and reasonably small.

## Security & Configuration Tips
- Do not commit secrets. Use environment variables for configuration.
- Be cautious with CORS and headers if exposing new APIs.
- Static files are publicly served from `/static`; avoid placing sensitive files there.
- Lockfiles: this repo uses `uv.lock` when working with `uv`.
