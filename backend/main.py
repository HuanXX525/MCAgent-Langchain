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

# 创建FastAPI应用
app = FastAPI(title="Minecraft Bot Backend", version="1.0.0")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket连接管理器
manager = ConnectionManager()

# 全局Agent实例
minecraft_agent = None

@app.on_event("startup")
async def startup_event():
    """启动时初始化Agent"""
    global minecraft_agent
    print("正在初始化Minecraft Agent...")
    try:
        minecraft_agent = MinecraftAgent(manager)
        set_agent(minecraft_agent)
        print("Minecraft Agent初始化成功！")
    except Exception as e:
        print(f"Agent初始化失败: {e}")
        import traceback
        traceback.print_exc()

@app.get("/api/config")
async def get_config():
    """获取当前配置"""
    try:
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/config")
async def save_config(config: dict):
    """保存配置"""
    try:
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        return {"success": True, "message": "配置已保存"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """处理聊天消息"""
    try:
        # 提取用户名
        username = request.username
        
        # 处理消息
        if minecraft_agent:
            reply = await minecraft_agent.process_message(
                request.message, 
                request.context,
                username
            )
        else:
            reply = "AI系统正在初始化中，请稍候..."
        
        return ChatResponse(reply=reply)
    except Exception as e:
        print(f"处理聊天请求失败: {e}")
        import traceback
        traceback.print_exc()
        return ChatResponse(reply=f"处理请求时出错: {str(e)}")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket连接端点"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            await manager.handle_message(data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket错误: {e}")
        manager.disconnect(websocket)

@app.get("/api/status")
async def status():
    """获取后端状态"""
    return {
        "status": "running",
        "agent_initialized": minecraft_agent is not None,
        "connections": len(manager.active_connections),
        "model": CONFIG['gpt']['model']
    }

web_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'web')
if os.path.exists(web_path):
    app.mount("/", StaticFiles(directory=web_path, html=True), name="web")

if __name__ == "__main__":
    port = CONFIG['backend']['port']
    host = CONFIG['backend']['host']
    print(f"启动服务器: {host}:{port}")
    print(f"WebSocket地址: ws://{host}:{port}/ws")
    print(f"API地址: http://{host}:{port}/api/chat")
    uvicorn.run(app, host=host, port=port)
