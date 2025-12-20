import enum
from fastapi import WebSocket
from typing import List, Dict, Any
import json
import asyncio
from shared import logger, get_minecraft_agent, get_connection_manager

class WebSockekProtocol(enum.Enum):
    CHAT = "chat"
    DEFAULT = "default"

class ConnectionManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        # self.active_connections: Dict[WebSocket] = {}  # key: user_id, value: WebSocket
        self.action_results = {}
        self.result_events = {}

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
        

    async def wait_for_action_result(self, action: Dict[str, Any], timeout: float = 30.0) -> Dict[str, Any]:
        """等待行动执行结果"""
        action_id = f"{action['skill']}.{action['method']}"
        
        try:
            # 等待结果事件
            await asyncio.wait_for(self.result_events[action_id].wait(), timeout=timeout)
            
            # 获取并清理结果
            result = self.action_results.pop(action_id, None)
            self.result_events.pop(action_id, None)
            
            return result
        except asyncio.TimeoutError:
            print(f"等待行动结果超时: {action_id}")
            self.result_events.pop(action_id, None)
            return {
                "success": False,
                "action": action,
                "error": "执行超时"
            }

    async def send_action(self, action: Dict[str, Any]):
            """发送行动指令到前端"""
            message = {
                "type": "execute_action",
                "data": action
            }
            
            # 为这个action创建一个等待事件
            action_id = f"{action['skill']}.{action['method']}"
            self.result_events[action_id] = asyncio.Event()
            
            for connection in self.active_connections:
                try:
                    await connection.send_json(message)
                    print(f"已发送行动指令: {action_id}")
                except Exception as e:
                    print(f"发送行动指令失败: {e}")
async def send_chat(text: str, webSocket: WebSocket):
    """发送聊天消息到前端"""
    message = {
        "type": WebSockekProtocol.CHAT.value,
        "data": {
            "message": text
        }
    }

    try:
        await webSocket.send_json(message)
    except Exception as e:
        logger.warning(f"发送聊天消息失败: {e}")

async def handle_websocket_data(data: Dict[str, Any], currentWebSocket: WebSocket):
    """处理来自前端的消息
    约定前端使用格式
    {
        "type": "chat",
        "data": {...
        }
    }
    """
    data_type = data.get("type") or WebSockekProtocol.DEFAULT.value
    data_data = data.get("data") or {}
    if data_type == WebSockekProtocol.CHAT.value:
        '''
        {
            "player": "playerName",
            "message": "hello world"
        }
        '''
        message = data_data.get("message") or ""
        player_name = data_data.get("player") or ""
        logger.info(f"收到玩家{player_name}消息: {message}")

        agent = get_minecraft_agent()
        if agent:
            _ = await agent.process_message(message, player_name, currentWebSocket)
        else:
            logger.warning("Minecraft Agent未初始化")

    elif data_type == WebSockekProtocol.DEFAULT.value:
        print("未知消息类型")
        pass