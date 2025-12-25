# 我的世界Agent伙伴

## 目的

开发一个能够根据用户聊天而作出相应行动的机器人

## 设计

使用mineflayer创建机器人并且连接我的世界客户端，相关配置由[配置文件](./config.json)读入；mineflayer的API文档在[API](./frontend/mineflayerApi.md)。

frontend文件夹下为“前端”，用于连接backend文件夹下的“后端”（websocket通信）和我的世界客户端；需要在这里实现机器人的行为控制框架（根据API）该框架应该方便维护（方便添加新的行为控制），并且能和我的后端Agent工具函数通过websocket对接。

backend文件夹下为“后端”，用于使用最新Langchain V1.0框架，创建Agent并且处理我的世界玩家的输入（自然语言），过程中调用工具函数[后端工具函数](./backend/agent/AgentTools.py)，设计为这样，这个就比较方便后续的添加，一个工具函数对应前端的一个或者多个Action的控制。

## 如何添加新的工具函数

在[伙伴能力定义文件](./frontend/src/action/action.js)中仿照已有的伙伴技能添加新的工具函数，并且在[伙伴能力管理文件](./frontend/src/action/actionManager.js)中注册。

在[后端工具函数](./backend/agent/AgentTools.py)中添加新的工具函数，并且文件加入文件最后的数组中，以传递给Agent使用。

### 定义能力

#### JS端

1. 进入[伙伴能力定义文件](./frontend/src/action/action.js)，写一个***异步***函数

2. 参数要求`{ nearByDistance = 1, playerName, follow }`，***Object***

3. 必须在所有分支中有`return`使用字符串向AI反馈执行结果

   有时候工具执行结果需要等待时间，可以这样返回

   ```js
     // 返回一个 Promise，直到到达目标才结束
     return new Promise((resolve) => {
       global.bot.pathfinder.setGoal(goal, false);
       // 使用 global.bot.once 监听单次事件，避免内存泄漏
       global.bot.once("goal_reached", () => {
         console.log("已到达目标");
         resolve("成功到达玩家附近"); // 只有调用了 resolve，外部的 await 才会继续执行
       });
     });
   ```

   

4. 导出你的函数`module.exports = { followPlayerOnce, followPlayerContinouslyToggle };`

5. 进入[伙伴能力管理文件](./frontend/src/action/actionManager.js)中注册，`ActionManager.instance.registeAction("followPlayerContinouslyToggle", followPlayerContinouslyToggle);`，第一个参数可以随意但必须和即将写的==Agent Tool==对应

   ```javascript
   /**
    * 控制是否持续跟随某个玩家
    */
   async function followPlayerContinouslyToggle({ nearByDistance = 1, playerName, follow }) {
     const targetPlayer = global.bot.players[playerName];
     if (!targetPlayer || !targetPlayer.entity) {
       return "玩家离你太远了，找不到玩家";
     }
   
     const mcData = require("minecraft-data")(global.bot.version);
     const movements = new Movements(global.bot, mcData);
     global.bot.pathfinder.setMovements(movements);
   
     // 设置持续跟随目标
     if (follow === true) {
       const goal = new GoalFollow(targetPlayer.entity, nearByDistance);
       global.bot.pathfinder.setGoal(goal, true); 
       return `开始持续跟随${playerName}`;
     } else {
       global.bot.pathfinder.setGoal(null);
       return `停止跟随${playerName}`;
     }
   }
   ```

#### Python端

1. 进入文件[后端工具函数](./backend/agent/AgentTools.py)添加Langchain使用的工具函数

2. 创建工具函数参数描述类（非必要），工具函数的参数不一定与JS端的行为一一对应，有工具函数上下文可以利用

   ```python
   class followPlayerContinouslyToggleInput(BaseModel): # 必须继承BaseModel
       replyToUserBeforeTool: str # 可以不使用描述，AI会根据变量名推断
       follow : bool = Field(description="是否持续跟随玩家")  # 使用描述
       nearByDistance : int = Field(description="最终跟随到玩家附近的距离", default = 1) # 使用描述和默认值
   ```

3. 创建***异步***工具函数，本质上是构造JS端所需要的参数

   ```python
   @tool(args_schema=followPlayerContinouslyToggleInput)# 使用此注解并且设置参数描述，使用此注解后，函数注释中的文本会被AI看见
   async def followPlayerContinouslyToggle(config: RunnableConfig, replyToUserBeforeTool: str,follow : bool, nearByDistance: int = 1) -> str:
       '''
       控制你在游戏中是否持续跟随玩家
       '''
       context = config.get("configurable", {}).get("context") # Langchain注入的上下文
       if (context and isinstance(context, Context)):
   		# 此处的args名称和类型必须与JS端一一对应
           args = {
               "nearByDistance" : nearByDistance,
               "playerName" : context.player_name,
               "follow" : follow
           }
           data = await send_tool_args(replyToUserBeforeTool, args, "followPlayerContinouslyToggle", context)# 使用通用的函数发送参数到JS端，此处的字符串必须和JS端注册时的能力一一对应
           # 直接复制即可，传递JS端的工具执行结果给AI，return就是告诉AI的消息
           if isinstance(data, str):
               return data
           else:
               # print(data.message)
               return data.message
       else:
           return "没有找到上下文信息，停止执行"
   ```

4. 添加到数组`tools = [followPlayerOnce, followPlayerContinouslyToggle]`

### 修改动态系统提示状态

在websocket端点处解析状态（文件[main.py:69](./backend/main.py)），并且在自定义的状态中间件构造系统提示（文件[agent\middleware.py:30](./backend/agent/middleware.py)）
