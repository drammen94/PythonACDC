import asyncio
import websockets
import json
import logging
from datetime import datetime

class RealTimeStream:
    def __init__(self, websocket_url):
        self.websocket_url = websocket_url
        self.websocket = None
        self.connected = False
        
    async def connect(self):
        """Establish WebSocket connection"""
        try:
            self.websocket = await websockets.connect(self.websocket_url)
            self.connected = True
            logging.info("WebSocket connection established")
        except Exception as e:
            logging.error(f"WebSocket connection failed: {str(e)}")
            self.connected = False
            
    async def send_data(self, data):
        """Send data through WebSocket"""
        if not self.connected:
            await self.connect()
            
        try:
            message = {
                'timestamp': datetime.now().isoformat(),
                'data': data
            }
            await self.websocket.send(json.dumps(message))
            return True
        except Exception as e:
            logging.error(f"Error sending data: {str(e)}")
            self.connected = False
            return False
            
    async def close(self):
        """Close WebSocket connection"""
        if self.websocket:
            await self.websocket.close()
            self.connected = False 