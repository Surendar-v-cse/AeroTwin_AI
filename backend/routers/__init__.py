from backend.routers.telemetry_routes import router as telemetry_router
from backend.routers.twin_routes import router as twin_router
from backend.routers.ai_routes import router as ai_router
from backend.routers.simulation_routes import router as simulation_router
from backend.routers.websocket_routes import router as websocket_router

__all__ = [
    "telemetry_router",
    "twin_router",
    "ai_router",
    "simulation_router",
    "websocket_router",
]
