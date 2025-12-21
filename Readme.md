# 我的世界Agent伙伴

## 目的

开发一个能够根据用户聊天而作出相应行动的机器人

## 设计

使用mineflayer创建机器人并且连接我的世界客户端，相关配置由[配置文件](./config.json)读入；mineflayer的API文档在[API](./frontend/mineflayerApi.md)。

frontend文件夹下为“前端”，用于连接backend文件夹下的“后端”（websocket通信）和我的世界客户端；需要在这里实现机器人的行为控制框架（根据API）该框架应该方便维护（方便添加新的行为控制），并且能和我的后端Agent工具函数通过websocket对接。

backend文件夹下为“后端”，用于使用最新Langchain V1.0框架，创建Agent并且处理我的世界玩家的输入（自然语言），过程中调用工具函数[后端工具函数](./backend/agent/AgentTools.py)，设计为这样，这个就比较方便后续的添加，一个工具函数对应前端的一个或者多个Action的控制。
