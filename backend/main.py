import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.database import init_db
from backend.engine_service import engine_service
from backend.routers import (
    telemetry_router,
    twin_router,
    ai_router,
    simulation_router,
    websocket_router
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup:
    init_db()
    # Pre-calculate initial state
    initial_telem = engine_service.telemetry_provider.get_current_telemetry()
    engine_service.compute_all(initial_telem)

    # Launch background simulation ticker loop
    sim_task = asyncio.create_task(engine_service.run_simulation_loop())
    print("[AeroTwin AI] Digital Twin Background Engine running.")

    yield

    # Shutdown:
    engine_service.running = False
    sim_task.cancel()
    print("[AeroTwin AI] Digital Twin Engine stopped.")

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="Digital Twin Platform for a MALE UAV Aero-Piston Engine (Rotax 914/915 Class)",
    lifespan=lifespan
)

# Enable CORS for frontend UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(telemetry_router)
app.include_router(twin_router)
app.include_router(ai_router)
app.include_router(simulation_router)
app.include_router(websocket_router)

@app.get("/", tags=["Root"])
def root():
    return {
        "platform": settings.app_name,
        "version": settings.version,
        "status": "OPERATIONAL",
        "docs_url": "/docs",
        "websocket_endpoint": "/ws/telemetry"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
