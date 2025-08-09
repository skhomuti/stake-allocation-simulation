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
- Install deps (uv): `uv sync --extra dev`
- Run dev server (reload): `uv run uvicorn app.main:app --reload`
- Or via script: `uv run ./scripts/dev.sh`
- Run tests: `uv run pytest -q`

## Coding Style & Naming Conventions
- Python: PEP 8, 4-space indentation, limit lines to ~100 chars.
- Names: modules/files `snake_case.py`, classes `CamelCase`, functions/vars `snake_case`.
- Type hints encouraged; add concise docstrings for public functions.
- Templates: prefer small, composable templates; keep inline CSS minimal.

## Error Handling
- Avoid broad `except Exception:` that hides errors.
- If exceptions are unlikely, let them surface and fail fast.
- When fallbacks are intended (e.g., ABI variants), catch and log with context (use `logging` with `exc_info=True`).

## Testing Guidelines
- Framework: `pytest` with FastAPI `TestClient`.
- Location: all tests in `tests/`
- Tests: `uv run pytest -q`.
- Do not skip any tests.
- Use fixtures for setup; keep tests isolated.
- 

## Commit & Pull Request Guidelines
- Commits: imperative, concise subject (≤72 chars), e.g., "Add health check endpoint".
- Include context in body when helpful; reference issues with `#123`.
- PRs: clear description of changes, rationale, and testing notes; include screenshots for UI changes.
- Keep PRs focused and reasonably small.

## Security & Configuration Tips
- Do not commit secrets. Use `.env` (copy from `.env.example`).
- Required env: `ETH_RPC_URL`; prefer `LIDO_LOCATOR_ADDRESS`; optional `STAKING_ROUTER_ADDRESS`.
- ABIs: place JSON files under `abi/` (e.g., `locator.json`, `staking_router.json`). Fetch from Etherscan.
- Be cautious with CORS if exposing new APIs.
- Static files are public via `/static`.
- Lockfiles: `uv.lock` is used with `uv`.
