const mineflayer = require("mineflayer");
const { pathfinder, Movements, goals } = require("mineflayer-pathfinder");
const { loadConfig } = require("./config");
const APIClient = require("./apiClient");
const ActionManager = require("./action/actionManager");

// 1. 加载配置
const config = loadConfig();
console.log("配置已加载");

// 2. 创建机器人
const bot = mineflayer.createBot(config.minecraft);
console.log("伙伴已创建");
global.bot = bot;
// 3. 加载pathfinder插件
bot.loadPlugin(pathfinder);
console.log("插件加载完成");

// 4. 变量声明
const apiClient = new APIClient(config);


// 处理用户消息
async function processUserMessage(username, message) {
  try {
    const response = await apiClient.sendMessage(username, message);
  } catch (error) {
    console.error("处理消息失败:", error.message);
  }
}

// 登录事件
bot.on("login", () => {
  console.log("机器人已登录");
  // 初始化pathfinder movements
  const mcData = require("minecraft-data")(bot.version);
  const defaultMove = new Movements(bot, mcData);
  bot.pathfinder.setMovements(defaultMove);
  // 在这里定义勾子逻辑
  apiClient.on("onAction", async (data) => {
    console.log("钩子触发：准备执行工具", data.action);

    try {
      // 1. 调用执行逻辑并拿到结果字符串
      const resultMessage = await ActionManager.instance.executeAction(
        data.action,
        data.action_id,
        data.args
      );

      // 2. 构造回执消息
      const ToolMessage = {
        type: "action",
        data: {
          action_id: data.action_id,
          message: resultMessage,
          action: data.action,
        },
      };

      // 3. 通过 apiClient 实例发送
      console.log("准备发送回执到后端...");
      apiClient.send(ToolMessage);
    } catch (err) {
      console.error("执行工具出错:", err);
    }
  });
  apiClient.connectWebSocket();
  console.log("正在连接后端...");
});

// 监听聊天事件
bot.on("chat", async (username, message) => {
  // 忽略机器人自己的消息
  if (username === bot.username) return;
  // console.log(`收到来自 ${username} 的消息: "${message}"`);
  // 检查消息中是否包含 @机器人用户名（不区分大小写）
  const mentionPattern = new RegExp(`@${config.name}`, "i");
  if (mentionPattern.test(message)) {
    // 提取用户消息
    const userMessage = message.replace(mentionPattern, "").trim() || "你好";
    // 处理消息
    // console.log(`收到来自 ${username} 的消息: "${userMessage}"`);
    await processUserMessage(username, userMessage);
  }
});

// 错误处理
bot.on("error", (err) => {
  console.error("错误:", err);
});

// 被踢出事件
bot.on("kicked", (reason) => {
  console.log("被踢出:", reason);
});

// 断开连接事件
bot.on("end", (reason) => {
  console.log("连接结束:", reason);
  if (apiClient) {
    apiClient.disconnect();
  }
});
