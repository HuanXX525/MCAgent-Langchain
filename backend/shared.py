"""
共享模块 - 存放全局状态和通用依赖
解决循环导入问题
"""
import logging

# 全局logger实例
logger = logging.getLogger(__name__)

# 全局变量
minecraft_agent = None

# 全局WebSocket管理器实例
manager = None

def initialize_logger():
    """初始化logger配置"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

def set_minecraft_agent(agent):
    """设置全局Agent实例"""
    global minecraft_agent
    minecraft_agent = agent

def set_connection_manager(conn_manager):
    """设置全局WebSocket连接管理器"""
    global manager
    manager = conn_manager

def get_minecraft_agent():
    """获取全局Agent实例"""
    return minecraft_agent

def get_connection_manager():
    """获取全局WebSocket连接管理器"""
    return manager