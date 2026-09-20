from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.engine_service import engine_service

router = APIRouter(tags=["WebSocket"])

@router.websocket("/ws/telemetry")
async def websocket_telemetry_endpoint(websocket: WebSocket):
    await websocket.accept()
    engine_service.active_websockets.add(websocket)

    # Immediately push current full state upon connection
    try:
        current_state = engine_service.latest_full_state
        if not current_state:
            telem = engine_service.telemetry_provider.get_current_telemetry()
            current_state = engine_service.compute_all(telem)
        await websocket.send_json(current_state)

        # Keep listening for incoming client pings or commands over the socket
        while True:
            data = await websocket.receive_text()
            # If client sends a ping or message
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        engine_service.active_websockets.discard(websocket)
    except Exception as e:
        engine_service.active_websockets.discard(websocket)
