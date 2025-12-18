from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Any

class MoveToInput(BaseModel):
    """移动到指定坐标的输入"""
    x: float = Field(description="目标X坐标")
    y: float = Field(description="目标Y坐标")
    z: float = Field(description="目标Z坐标")

class MoveToTool(BaseTool):
    name: str = "move_to"
    description: str = "移动机器人到指定的坐标位置。需要提供x, y, z三个坐标参数。例如：移动到(100, 64, 200)"
    args_schema: type[BaseModel] = MoveToInput
    websocket_manager: Any = Field(default=None)

    def _run(self, x: float, y: float, z: float) -> str:
        return "请使用异步版本 _arun"
    
    async def _arun(self, x: float, y: float, z: float) -> str:
        """异步执行移动"""
        action = {
            "skill": "movement",
            "method": "moveTo",
            "params": [x, y, z]
        }
        await self.websocket_manager.send_action(action)
        result = await self.websocket_manager.wait_for_action_result(action)
        
        if result and result.get("success"):
            return f"成功移动到坐标 ({x}, {y}, {z})"
        else:
            error = result.get("error", "未知错误") if result else "执行超时"
            return f"移动失败: {error}"

class FollowPlayerInput(BaseModel):
    """跟随玩家的输入"""
    playerName: str = Field(description="要跟随的玩家名称")
    distance: int = Field(default=3, description="跟随距离，默认3格")

class FollowPlayerTool(BaseTool):
    name: str = "follow_player"
    description: str = "跟随指定的玩家。需要提供玩家名称和可选的跟随距离。"
    args_schema: type[BaseModel] = FollowPlayerInput
    websocket_manager: Any = Field(default=None)

    def _run(self, playerName: str, distance: int = 3) -> str:
        return "请使用异步版本 _arun"
    
    async def _arun(self, playerName: str, distance: int = 3) -> str:
        """异步执行跟随"""
        action = {
            "skill": "movement",
            "method": "followPlayer",
            "params": [playerName, distance]
        }
        await self.websocket_manager.send_action(action)
        result = await self.websocket_manager.wait_for_action_result(action)
        
        if result and result.get("success"):
            return f"开始跟随玩家 {playerName}"
        else:
            error = result.get("error", "未知错误") if result else "执行超时"
            return f"跟随失败: {error}"
