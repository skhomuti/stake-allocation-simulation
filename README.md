
# Stake Allocation Simulation

This project visualizes stake allocation mechanisms for Lido Staking Modules.
It fetches the current state of the network, displays the up-to-date stake distribution,
and allows users to simulate stake allocation across different modules.

There are two types of modules supported:
- Curated (Node Operators Registry): stake is allocated using min first allocation strategy.
- CSM (Community Staking Module): stake is allocated using the FIFO queue.

Every module's stake share is set on the Staking Router contract, and the stake is allocated
to the modules based on the share. Small modules are getting stake first until their stake share is filled,
then the next module is getting stake, and so on. Modules are getting deposits with batches of 30 * 32 ETH (or less)

## Setup

- Using `uv` (recommended):
  - Install project dependencies: `uv sync`
  - For tests/dev tools: `uv sync --extra dev`

- Optional (pip alternative):
  - `python -m venv .venv && source .venv/bin/activate`
  - `pip install -U pip`
  - `pip install fastapi "uvicorn[standard]" jinja2 pytest httpx`

## Run

- With uv (reload): `uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
- Or via script: `uv run ./scripts/dev.sh`

Open http://localhost:8000 to view the single frontend page.

API docs: http://localhost:8000/docs

