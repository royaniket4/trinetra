import asyncio
import json
from fastapi import WebSocket
from typing import Set, Dict, Any
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """WebSocket connection manager for real-time updates."""
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self._running = False
        self._task = None
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"Client connected. Active: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
        logger.info(f"Client disconnected. Active: {len(self.active_connections)}")
    
    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast a message to all connected clients."""
        disconnected = set()
        
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning(f"Failed to send to client: {e}")
                disconnected.add(connection)
        
        for conn in disconnected:
            self.active_connections.discard(conn)
    
    async def send_personal(self, websocket: WebSocket, message: Dict[str, Any]):
        """Send a message to a specific client."""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Failed to send personal message: {e}")
    
    async def websocket_endpoint(self, websocket: WebSocket):
        """Handle WebSocket connections."""
        await self.connect(websocket)
        try:
            while True:
                data = await websocket.receive_text()
                try:
                    message = json.loads(data)
                    if message.get("type") == "ping":
                        await self.send_personal(websocket, {"type": "pong"})
                except json.JSONDecodeError:
                    logger.warning("Invalid JSON received")
        except Exception as e:
            logger.info(f"WebSocket error: {e}")
        finally:
            self.disconnect(websocket)
    
    async def start_loop(self):
        """Start background broadcast loop."""
        while self._running:
            await asyncio.sleep(1)
    
    def start(self):
        """Start the WebSocket manager."""
        if not self._running:
            self._running = True
            logger.info("WebSocket manager started")
    
    def stop(self):
        """Stop the WebSocket manager."""
        self._running = False
        logger.info("WebSocket manager stopped")


ws_manager = ConnectionManager()


async def broadcast_alert(alert: Dict[str, Any]):
    """Broadcast an alert to all connected clients."""
    await ws_manager.broadcast({
        "type": "alert",
        "data": alert,
    })


async def broadcast_log(log: Dict[str, Any]):
    """Broadcast a log to all connected clients."""
    await ws_manager.broadcast({
        "type": "log",
        "data": log,
    })


async def broadcast_stats(stats: Dict[str, Any]):
    """Broadcast statistics to all connected clients."""
    await ws_manager.broadcast({
        "type": "stats",
        "data": stats,
    })