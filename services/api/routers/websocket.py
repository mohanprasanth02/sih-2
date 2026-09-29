"""
LabelGuard AI - WebSocket Real-Time Pipeline Streamer
Streams live pipeline events: IMAGE_RECEIVED -> QUALITY_CHECKED -> OCR_STARTED ->
OCR_COMPLETED -> EXTRACTION_STARTED -> RULE_VALIDATION -> EVIDENCE -> ANALYSIS_COMPLETED.
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List, Any
import json
import logging

logger = logging.getLogger("labelguard.ws")
router = APIRouter(tags=["WebSocket"])

class InspectionConnectionManager:
    def __init__(self):
        # Map inspection_id -> List[WebSocket]
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, inspection_id: str, websocket: WebSocket):
        await websocket.accept()
        if inspection_id not in self.active_connections:
            self.active_connections[inspection_id] = []
        self.active_connections[inspection_id].append(websocket)
        logger.info(f"WebSocket client connected to inspection {inspection_id}")

    def disconnect(self, inspection_id: str, websocket: WebSocket):
        if inspection_id in self.active_connections:
            if websocket in self.active_connections[inspection_id]:
                self.active_connections[inspection_id].remove(websocket)
            if not self.active_connections[inspection_id]:
                del self.active_connections[inspection_id]

    async def broadcast_event(self, inspection_id: str, event_data: Dict[str, Any]):
        if inspection_id in self.active_connections:
            msg_str = json.dumps(event_data)
            for connection in list(self.active_connections[inspection_id]):
                try:
                    await connection.send_text(msg_str)
                except Exception as e:
                    logger.warning(f"Error sending WS event to client: {e}")
                    self.disconnect(inspection_id, connection)

manager = InspectionConnectionManager()

@router.websocket("/ws/inspections/{inspection_id}")
async def websocket_inspection_endpoint(websocket: WebSocket, inspection_id: str):
    await manager.connect(inspection_id, websocket)
    try:
        while True:
            # Keep connection alive; clients can also send ping
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text(json.dumps({"event": "pong"}))
    except WebSocketDisconnect:
        manager.disconnect(inspection_id, websocket)
    except Exception:
        manager.disconnect(inspection_id, websocket)
