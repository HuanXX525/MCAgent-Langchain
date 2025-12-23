from fastapi import WebSocket
from langchain_openai import ChatOpenAI
from typing import Any
# from api.websocket import send_chat
from langgraph.checkpoint.postgres import PostgresSaver 
from typing import Any
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain.messages import AIMessage, HumanMessage


from .AgentTools import Context, tools

from config import API_KEY, BASE_URL, BOTNAME, MODEL, SAVE_SLOT
from typing import Any
from fastapi import WebSocket

from api.WebSockekProtocol import WebSockekProtocol
from logger import logger



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



from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver


class MinecraftAgent:
    """Minecraft游戏AI Agent"""
    
    def __init__(self, checkpointer:AsyncPostgresSaver):
        # self.websocket_manager = websocket_manager
        self.model = ChatOpenAI(
            model=MODEL,
            base_url=BASE_URL,
            api_key=API_KEY
        )
        self.checkpointer = checkpointer
        # 初始化LLM
        prompt = "你是我的世界中的一个玩家实体，作为玩家的伙伴，你需要根据玩家的输入做出合适的选择。如果必要，使用工具函数可以让你与游戏世界交互"
        
        # 短期记忆、系统提示、工具集、模型
        self.agent = create_agent(self.model, tools, system_prompt=prompt, checkpointer=self.checkpointer)
    async def process_stream_chunk(self, stream_mode : str | Any, chunk : str | Any, web_socket:WebSocket):
        '''
        根据不同的流式回复模式处理流式回复的内容
        
        :param stream_mode: 顾名思义
        :type stream_mode: str | Any
        :param chunk: 顾名思义
        :type chunk: str | Any
        '''
        # from api.websocket import send_chat
        if stream_mode == "custom":
            _ = await send_chat(chunk, web_socket)
            # send_ai_message(chunk)
        if stream_mode == "updates":
            # print(type(chunk))
            if isinstance(chunk, dict):
                model = chunk.get('model')
                if model:
                    messages = model.get('messages')
                    if messages and isinstance(messages, list):
                        first_message = messages[0]
                        if(isinstance(first_message, AIMessage)):
                            _ = await send_chat(str(first_message.content), web_socket)


    async def process_message(self, message: str, username: str, websocket):
        """处理用户消息"""
        try:
            # 使用用户名作为thread_id来区分不同用户的对话
            config = {"configurable": {"thread_id": username}}
            async for stream_mode, chunk in self.agent.astream(
                {"messages": [HumanMessage(content=f"{username}: {message}")]}, 
                config={"configurable":{"thread_id": SAVE_SLOT + BOTNAME}},
                stream_mode=["custom", "updates"],
                context=Context(websocket=websocket, player_name=username)):
                _ = await self.process_stream_chunk(stream_mode, chunk, websocket)
        except Exception as e:
            print(f"Agent处理过程中出现错误: {e}")
            import traceback
            traceback.print_exc()
            return f"抱歉，处理请求时出错：{str(e)}"

minecraftAgent = None

def set_minecraft_agent(new_agent: MinecraftAgent):
    global minecraftAgent
    minecraftAgent = new_agent

def get_minecraft_agent():
    global minecraftAgent
    return minecraftAgent
