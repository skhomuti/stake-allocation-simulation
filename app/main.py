from dataclasses import asdict
from typing import List

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
    return [asdict(m) for m in modules]
