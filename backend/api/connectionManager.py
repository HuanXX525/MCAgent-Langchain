import enum
from fastapi import WebSocket
from typing import List, Dict, Any
import asyncio


from logger import logger

class ConnectionManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        # self.active_connections: Dict[WebSocket] = {}  # key: user_id, value: WebSocket
        self.action_results = {}
        self.result_events = {}
        self.action_future : dict[str, asyncio.Future] = {}

    async def connect(self, websocket: WebSocket):
        """接受WebSocket连接"""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"有新的客户端连接-当前总连接数: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """断开WebSocket连接"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"有客户端断开连接-当前总连接数: {len(self.active_connections)}")
        
# 👇 模块级单例实例
connection_manager = ConnectionManager()

# 可选：提供一个函数方便导入
def get_connection_manager() -> ConnectionManager:
    return connection_manager