from langchain_core.tools import tool
from langgraph.config import get_stream_writer
from pydantic import BaseModel, Field



############## 设置跟随玩家状态工具 ##############
class FollowPlayerInput(BaseModel):
    reply: str = Field(description="执行工具前对玩家的回复")
    follow: bool = Field(description="True表示跟随玩家")
@tool
def follow_player(reply: str, follow: bool) -> str:
    '''
    控制你在游戏中是否跟随玩家
    '''
    writer = get_stream_writer()
    writer(reply)
    if follow:
        return "已跟随"
    else:
        return "已取消跟随"
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
tools = [follow_player]

