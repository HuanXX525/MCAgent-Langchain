from fastapi import WebSocket
from typing import List, Dict, Any
import json
import asyncio

class ConnectionManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.action_results = {}
        self.result_events = {}

    async def connect(self, websocket: WebSocket):
        """接受WebSocket连接"""
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"客户端已连接。总连接数: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """断开WebSocket连接"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        print(f"客户端已断开。总连接数: {len(self.active_connections)}")

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

    async def send_chat(self, text: str):
        """发送聊天消息到前端"""
        message = {
            "type": "chat_response",
            "data": {"text": text}
        }
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"发送聊天消息失败: {e}")

    async def handle_message(self, data: Dict[str, Any]):
        """处理来自前端的消息"""
        msg_type = data.get("type")
        
        if msg_type == "action_result":
            # 处理行动执行结果
            result = data.get("data")
            action = result.get("action", {})
            action_id = f"{action.get('skill')}.{action.get('method')}"
            
            # 保存结果
            self.action_results[action_id] = result
            
            # 触发等待事件
            if action_id in self.result_events:
                self.result_events[action_id].set()
            
            print(f"收到行动结果: {action_id} - 成功: {result.get('success')}")
        
        elif msg_type == "pong":
            print("收到pong")

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
