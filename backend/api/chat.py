from models import ChatRequest, ChatResponse

# 全局agent实例（将在main.py中初始化）
agent = None

def set_agent(agent_instance):
    """设置agent实例"""
    global agent
    agent = agent_instance

async def process_chat_message(request: ChatRequest, websocket_manager) -> ChatResponse:
    """处理聊天消息"""
    global agent
    
    # 如果agent未初始化，返回简单回复
    if agent is None:
        return ChatResponse(
            reply="AI系统正在初始化中，请稍候..."
        )
    
    try:
        # 使用agent处理消息
        reply = await agent.process_message(request.message, request.context)
        
        return ChatResponse(reply=reply)
    except Exception as e:
        print(f"处理聊天消息失败: {e}")
        return ChatResponse(
            reply=f"抱歉，处理请求时出错: {str(e)}"
        )
