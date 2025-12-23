import asyncio
import selectors
import sys
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from config import DB_URL 

async def init_db():
    print(f"正在连接数据库: {DB_URL}")
    try:
        # 使用异步上下文管理器连接
        async with AsyncPostgresSaver.from_conn_string(DB_URL) as checkpointer:
            # 创建必要的表 (checkpoints, writes, etc.)
            await checkpointer.setup()
            print("✅ 数据库表初始化成功！")
    except Exception as e:
        print(f"❌ 初始化失败: {e}")


# ... 你的 init_db 定义 ...

if __name__ == "__main__":
    if sys.platform == "win32":
        # 方案 A：最标准写法，通过 lambda 传入工厂函数
        asyncio.run(
            init_db(), 
            loop_factory=lambda: asyncio.SelectorEventLoop(selectors.SelectSelector())
        )
    else:
        # 非 Windows 系统直接运行即可
        asyncio.run(init_db())