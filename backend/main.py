import sys
import asyncio

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
from contextlib import asynccontextmanager
from typing import Any, Dict
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import json
import os
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from api.WebSockekProtocol import WebSockekProtocol
from config import CONFIG, DB_URL
from api.connectionManager import get_connection_manager
from agent.Agent import MinecraftAgent, get_minecraft_agent, set_minecraft_agent
from logger import logger

# main.py（最顶部！）


async def handle_websocket_data(data: Dict[str, Any], currentWebSocket: WebSocket):
    """处理来自前端的消息
    约定前端使用格式
    {
        "type": "chat",
        "data": {...
        }
    }
    """
    logger.info(f"接收到的数据: {json.dumps(data)}")
    data_type = data.get("type") or WebSockekProtocol.DEFAULT.value
    data_data = data.get("data") or {}
    manager = get_connection_manager()

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
    elif data_type == WebSockekProtocol.ACTION.value:
        '''
        {
            "action_id": action_id,
            "action": action_name,
            "message": "hello world",
        }
        '''
        action_name = data_data.get("action") or ""
        message = data_data.get("message") or ""
        action_id = data_data.get("action_id") or ""
        logger.info(f"工具 {action_name}执行结果 {message}")
        future = manager.action_future.pop(action_id)
        future.set_result({"message": message})
    elif data_type == WebSockekProtocol.STATE.value:
        '''
        {
            "weather": "晴朗",
        }
        '''
        weather = data_data.get("weather") or "null"
        action_id = data_data.get("action_id") or ""
        future = manager.action_future.pop(action_id)
        future.set_result({"weather": weather})

    elif data_type == WebSockekProtocol.DEFAULT.value:
        print("未知消息类型")
        pass

async def startup_event(checkpointer: AsyncPostgresSaver):
    """启动时初始化Agent"""
    # logger.info("初始化Agent")
    try:
        
        # 创建并设置Agent实例
        agent = MinecraftAgent(checkpointer=checkpointer)
        set_minecraft_agent(agent)
        
        logger.info("Minecraft Agent初始化成功！")
    except Exception as e:
        logger.error(f"Agent初始化失败: {e}")
        import traceback
        traceback.print_exc()

async def close_event():
    """启动时初始化Agent"""
    logger.info("服务关闭")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时要做的事情
    async with AsyncPostgresSaver.from_conn_string(DB_URL) as checkpointer:
        await startup_event(checkpointer)
        yield
        # 结束时要做的事情
        await close_event()

# 创建FastAPI应用
app = FastAPI(title="Minecraft Bot Backend", version="1.0.0", lifespan=lifespan)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/config")
async def get_config():
    """读配置文件"""
    try:
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'configdev.json')
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/config")
async def save_config(config: dict):
    """写配置文件"""
    try:
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'configdev.json')
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        return {"success": True, "message": "配置已保存"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    connection_manager = get_connection_manager()
    if not connection_manager:
        logger.error("WebSocket连接管理器未初始化")
        return
        
    await connection_manager.connect(websocket)
    try:
        while True:
            # 1. 接收数据
            data = await websocket.receive_json()
            
            # 2. 【核心修复】使用 create_task 异步处理
            # 这样 handle_websocket_data 不会阻塞当前的循环
            # 循环会立即回到上面的 receive_json() 等待前端的回执
            asyncio.create_task(handle_websocket_data(data, websocket))
            
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket错误: {e}")
        connection_manager.disconnect(websocket)

web_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'web')
if os.path.exists(web_path):
    app.mount("/", StaticFiles(directory=web_path, html=True), name="web")

if __name__ == "__main__":
    port = CONFIG['backend']['port']
    host = CONFIG['backend']['host']
    logger.info(f"启动服务器: {host}:{port}")
    logger.info(f"WebSocket地址: ws://{host}:{port}/ws")
    logger.info(f"API地址: http://{host}:{port}/api/chat")
    uvicorn.run("main:app" , host=host, port=port, loop="asyncio", reload=True)
