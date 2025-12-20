from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import asyncio
import json
import os

from config import CONFIG
from models import ChatRequest, ChatResponse
from api.chat import process_chat_message, set_agent
from api.websocket import ConnectionManager
from agent.conversational import MinecraftAgent
from shared import (logger, initialize_logger, set_minecraft_agent, 
                   set_connection_manager, get_connection_manager)

async def startup_event():
    """启动时初始化Agent"""
    # logger.info("初始化Agent")
    try:
        # 初始化logger配置
        initialize_logger()
        
        # 创建并设置Agent实例
        agent = MinecraftAgent()
        set_minecraft_agent(agent)
        set_agent(agent)
        
        # 创建并设置WebSocket连接管理器
        connection_manager = ConnectionManager()
        set_connection_manager(connection_manager)
        
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
    await startup_event()
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
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/config")
async def save_config(config: dict):
    """写配置文件"""
    try:
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        return {"success": True, "message": "配置已保存"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket连接端点"""
    from api.websocket import handle_websocket_data
    
    # 获取连接管理器
    connection_manager = get_connection_manager()
    if not connection_manager:
        logger.error("WebSocket连接管理器未初始化")
        return
        
    await connection_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            await handle_websocket_data(data, websocket)
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
    uvicorn.run(app, host=host, port=port)
