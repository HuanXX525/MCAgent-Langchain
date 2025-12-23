import asyncio
from dataclasses import dataclass
from typing import Annotated
import uuid
from fastapi import WebSocket
from langchain.tools import tool, ToolRuntime
from langgraph.config import get_stream_writer
from pydantic import BaseModel, Field


from api.connectionManager import get_connection_manager
from api.WebSockekProtocol import WebSockekProtocol
from logger import logger

@dataclass
class Context():
    websocket : WebSocket
    player_name : str

async def send_tool_args(reply: str, tool_runtime:ToolRuntime[Context], args:dict, action_name:str):
    writer = get_stream_writer()
    writer(reply)
    websocket = tool_runtime.context.websocket
    action_id = str(uuid.uuid4())
    # 创建一个 Future 用于等待前端响应
    future = asyncio.Future()
    get_connection_manager().action_future[action_id] = future
    try:
        # 异步执行
        asyncio.create_task(
            websocket.send_json({
                "type": WebSockekProtocol.ACTION.value,
                "data":{
                    "action_id": action_id,
                    "action": action_name,
                    "args": args
                }
            })
        )
        # 等待前端执行完毕并回传确认
        '''
        {
            "message": "hello world",        
        }
        '''
        result = await asyncio.wait_for(future, timeout=120)
        # logger.info(f"工具返回结果：{result}")
        if result.get("message", False):
            return result.message
        else:
            return "工具反馈失败"
    except asyncio.TimeoutError:
        logger.error("游戏世界操作超时")
        return "游戏世界操作超时"

from langchain_core.tools import InjectedToolArg # 导入注入标记

############## 设置跟随玩家状态工具 ##############
class followPlayerOnceInput(BaseModel):
    replyToUserBeforeTool: str
    nearByDistance : int = Field(description="最终跟随到玩家附近的距离", default = 1)
@tool(args_schema=followPlayerOnceInput)
async def followPlayerOnce(tool_runtime: Annotated[ToolRuntime[Context], InjectedToolArg], replyToUserBeforeTool: str, nearByDistance: int = 1) -> str:
    '''
    控制你在游戏中是否跟随玩家
    '''
    args = {
        "nearByDistance" : nearByDistance,
        "playerName" : tool_runtime.context.player_name
    }
    data = await send_tool_args(replyToUserBeforeTool, tool_runtime, args, "follow_player")
    if isinstance(data, str):
        # print(data)
        return data
    else:
        # print(data.message)
        return data.message

############## 设置跟随玩家状态工具 ##############

# @tool
# def get_bag_items(runtime:ToolRuntime) -> list[str]:
#     '''获取你背包里的所有物品'''
#     writer = runtime.stream_writer
#     writer("访问了背包")
#     return ["apple"]

# @tool
# def throw_item(item: str, runtime:ToolRuntime):
#     '''扔出你选择的物品，前提是它在你的背包里'''
#     writer = runtime.stream_writer
#     writer(f"扔出了{item}")
#     return f"{item} was thrown"

# tools = [follow_player, get_bag_items, throw_item]
tools = [followPlayerOnce]

