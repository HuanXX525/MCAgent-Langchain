from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Any

class MineBlockInput(BaseModel):
    """挖掘方块的输入"""
    block_name: str = Field(description="要挖掘的方块名称，如'stone'、'diamond_ore'、'iron_ore'等")
    count: int = Field(default=1, description="要挖掘的数量，默认为1")

class MineBlockTool(BaseTool):
    name: str = "mine_block"
    description: str = "寻找并挖掘指定类型和数量的方块。会自动寻找附近的方块并挖掘。例如：挖掘3个钻石矿石"
    args_schema: type[BaseModel] = MineBlockInput
    websocket_manager: Any = Field(default=None)

    def _run(self, block_name: str, count: int = 1) -> str:
        return "请使用异步版本 _arun"
    
    async def _arun(self, block_name: str, count: int = 1) -> str:
        """异步执行挖掘"""
        action = {
            "skill": "mining",
            "method": "findAndMine",
            "params": [block_name, count]
        }
        await self.websocket_manager.send_action(action)
        result = await self.websocket_manager.wait_for_action_result(action)
        
        if result and result.get("success"):
            mined = result.get("result", {}).get("mined", count)
            return f"成功挖掘了 {mined} 个 {block_name}"
        else:
            error = result.get("error", "未知错误") if result else "执行超时"
            return f"挖掘失败: {error}"

class DigBlockAtInput(BaseModel):
    """挖掘指定坐标方块的输入"""
    x: float = Field(description="方块X坐标")
    y: float = Field(description="方块Y坐标")
    z: float = Field(description="方块Z坐标")

class DigBlockAtTool(BaseTool):
    name: str = "dig_block_at"
    description: str = "挖掘指定坐标位置的方块。需要提供准确的x, y, z坐标。"
    args_schema: type[BaseModel] = DigBlockAtInput
    websocket_manager: Any = Field(default=None)

    def _run(self, x: float, y: float, z: float) -> str:
        return "请使用异步版本 _arun"
    
    async def _arun(self, x: float, y: float, z: float) -> str:
        """异步执行挖掘指定坐标的方块"""
        action = {
            "skill": "mining",
            "method": "digBlock",
            "params": [x, y, z]
        }
        await self.websocket_manager.send_action(action)
        result = await self.websocket_manager.wait_for_action_result(action)
        
        if result and result.get("success"):
            block_name = result.get("result", {}).get("block", "方块")
            return f"成功挖掘了位于 ({x}, {y}, {z}) 的 {block_name}"
        else:
            error = result.get("error", "未知错误") if result else "执行超时"
            return f"挖掘失败: {error}"
