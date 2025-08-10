from dataclasses import asdict
from typing import List, Dict, Any

from fastapi import Depends, FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import app.deps as deps
from app.services.router_service import RouterService

app = FastAPI(title="Stake Allocation Simulation")

# Mount static files (if any get added later)
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/healthz", tags=["health"])
async def healthz():
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse, tags=["ui"])
async def index(request: Request):
    return templates.TemplateResponse(request, "index.html", {"title": "Stake Allocation Simulation"})


@app.get("/api/modules", tags=["api"])
async def api_modules(service: RouterService = Depends(deps.get_router_service)) -> List[dict]:
    modules = service.list_modules()

    # Compute current allocation state based on active validators
    total_active = sum((m.active_validators or 0) for m in modules)

    enriched: List[Dict[str, Any]] = []
    for m in modules:
        d = asdict(m)
        active = m.active_validators or 0
        allocated_eth = active * 32
        depositable = getattr(m, 'depositable_validators', None) or 0
        depositable_eth = depositable * 32
        current_share_pct = (active / total_active * 100.0) if total_active > 0 else None
        d.update({
            "allocated_eth": allocated_eth,
            "depositable_eth": depositable_eth,
            "depositable_validators": depositable,
            "current_share_pct": current_share_pct,
        })
        enriched.append(d)
    return enriched
