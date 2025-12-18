from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from typing import List, Dict, Any

from config import CONFIG
from tools.movement import MoveToTool, FollowPlayerTool
from tools.mining import MineBlockTool, DigBlockAtTool

class MinecraftAgent:
    """Minecraft游戏AI Agent"""
    
    def __init__(self, websocket_manager):
        self.websocket_manager = websocket_manager
        
        # 初始化LLM
        self.llm = ChatOpenAI(
            api_key=CONFIG['gpt']['api_key'],
            base_url=CONFIG['gpt']['base_url'],
            model=CONFIG['gpt']['model'],
            temperature=CONFIG['gpt']['temperature'],
            max_tokens=CONFIG['gpt']['max_tokens']
        )
        
        # 初始化工具
        self.tools = [
            MoveToTool(websocket_manager=websocket_manager),
            FollowPlayerTool(websocket_manager=websocket_manager),
            MineBlockTool(websocket_manager=websocket_manager),
            DigBlockAtTool(websocket_manager=websocket_manager)
        ]
        
        # 初始化记忆（每个用户一个）
        self.memories = {}
        
        # 创建prompt模板
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个Minecraft游戏中的AI助手机器人Alice。你可以帮助玩家完成各种任务。

你拥有以下能力：
- move_to: 移动到指定坐标位置
- follow_player: 跟随指定玩家
- mine_block: 寻找并挖掘指定类型的方块
- dig_block_at: 挖掘指定坐标的方块

请根据玩家的请求，选择合适的工具来完成任务。
- 如果任务需要多个步骤，请逐步执行
- 回复要友好、简洁
- 用中文回复
- 如果无法完成某个任务，请说明原因
- 玩家的请求会包含当前游戏状态信息，请仔细阅读
"""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # 创建agent
        self.agent = create_openai_tools_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt
        )
    
    def get_or_create_memory(self, username: str):
        """获取或创建用户的对话记忆"""
        if username not in self.memories:
            self.memories[username] = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True
            )
        return self.memories[username]
    
    async def process_message(self, message: str, context: Dict[str, Any], username: str = "Player") -> str:
        """处理用户消息"""
        try:
            # 获取用户记忆
            memory = self.get_or_create_memory(username)
            
            # 创建agent executor
            agent_executor = AgentExecutor(
                agent=self.agent,
                tools=self.tools,
                memory=memory,
                verbose=True,
                max_iterations=10,
                handle_parsing_errors=True
            )
            
            # 准备游戏状态信息
            game_state = context.get("gameState", {})
            position = game_state.get("position", {})
            position_str = f"({position.get('x', 0):.1f}, {position.get('y', 0):.1f}, {position.get('z', 0):.1f})"
            
            inventory = context.get("inventory", [])
            inventory_str = ", ".join([f"{item['name']}x{item['count']}" for item in inventory[:5]])
            if len(inventory) > 5:
                inventory_str += f" 等{len(inventory)}种物品"
            if not inventory_str:
                inventory_str = "空"
            
            nearby_players = context.get("nearbyPlayers", [])
            players_str = ", ".join([p['username'] for p in nearby_players[:3]])
            if not players_str:
                players_str = "无"
            
            # 将游戏状态整合到消息中
            context_info = f"""
[当前游戏状态]
位置：{position_str}
生命值：{game_state.get("health", 20)}/20
饥饿值：{game_state.get("food", 20)}/20
物品栏：{inventory_str}
附近玩家：{players_str}

[玩家请求]
{message}
"""
            
            # 准备输入（只有input一个键）
            input_data = {
                "input": context_info
            }
            
            # 执行agent
            result = await agent_executor.ainvoke(input_data)
            
            return result.get("output", "我已经处理了你的请求")
        except Exception as e:
            print(f"Agent处理失败: {e}")
            import traceback
            traceback.print_exc()
            return f"抱歉，处理请求时出错：{str(e)}"
