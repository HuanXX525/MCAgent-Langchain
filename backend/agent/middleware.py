import asyncio
import uuid
from typing import Any
from langchain.agents.middleware import AgentMiddleware, AgentState, wrap_model_call, dynamic_prompt
from langgraph.runtime import Runtime
from langchain_core.messages import SystemMessage
from agent.AgentTools import Context
from api.connectionManager import get_connection_manager
from config import CHARACTER
from logger import logger
from api.WebSockekProtocol import WebSockekProtocol

class MinecraftStateMiddleware(AgentMiddleware):
    def __init__(self, timeout: float = 2.0):
        self.timeout = timeout

    async def awrap_model_call(
        self,
        request: Any, # 这里的类型通常是 ModelRequest
        handler: Any,
    ) -> Any:
        # 1. 获取最新状态 (逻辑不变)
        websocket = request.runtime.context.websocket
        action_id = str(uuid.uuid4())
        future = asyncio.Future()
        get_connection_manager().action_future[action_id] = future

        try:
            await websocket.send_json({
                "type": WebSockekProtocol.STATE.value,
                "data": {"action_id": action_id}
            })
            game_data = await asyncio.wait_for(future, timeout=self.timeout)
            
            status_prompt = f"当前天气: {game_data.get('weather')}\n"
            
            # 2. 构造完整的系统提示
            system_prompt_content = f"""
### 你的设定
你是我的世界中的一个玩家实体，作为玩家的伙伴，你需要根据玩家的输入做出合适的选择。如果必要，使用工具函数可以让你与游戏世界交互
### 角色描述
{CHARACTER}
### 当前的世界信息：
{status_prompt}
"""
            # 3. 使用 request.override 替换本次调用的系统消息
            # 这是官方推荐的动态修改 System Prompt 的方式
            new_system_message = SystemMessage(content=system_prompt_content)
            
            # 这里的 handler 是后续的执行流程（包含模型调用）
            # override 会创建一个新的 request 副本，不影响历史记录，只影响本次调用
            return await handler(request.override(system_message=new_system_message))

        except Exception as e:
            logger.error(f"中间件实时状态注入失败: {e}")
            return await handler(request)