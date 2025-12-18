from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class Position(BaseModel):
    """位置坐标"""
    x: float
    y: float
    z: float

class Weather(BaseModel):
    """天气信息"""
    isRaining: bool
    thunderState: int

class GameState(BaseModel):
    """游戏状态"""
    position: Position
    health: float
    food: float
    gameMode: str
    dimension: str
    time: int
    weather: Weather

class InventoryItem(BaseModel):
    """物品栏物品"""
    name: str
    count: int
    slot: int
    displayName: Optional[str] = None

class Entity(BaseModel):
    """实体信息"""
    type: str
    name: Optional[str] = None
    position: Position
    distance: float

class ChatRequest(BaseModel):
    """聊天请求"""
    username: str
    message: str
    context: Dict[str, Any]

class ChatResponse(BaseModel):
    """聊天响应"""
    reply: str
    actions: Optional[List[Dict[str, Any]]] = None

class Action(BaseModel):
    """行动指令"""
    skill: str
    method: str
    params: List[Any]

class ActionResult(BaseModel):
    """行动结果"""
    success: bool
    action: Action
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
