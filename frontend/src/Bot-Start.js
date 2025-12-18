const mineflayer = require("mineflayer");
const { pathfinder, Movements } = require('mineflayer-pathfinder');
const { loadConfig } = require('./config');
const SkillManager = require('./skillManager');
const APIClient = require('./apiClient');

// 加载配置
const config = loadConfig();
console.log('配置已加载');

// 创建机器人
const bot = mineflayer.createBot(config.minecraft);

// 加载pathfinder插件
bot.loadPlugin(pathfinder);

let skillManager;
let apiClient;

// 处理用户消息
async function processUserMessage(username, message) {
  try {
    // 发送到后端处理
    const response = await apiClient.sendMessage(username, message);
    return response.reply || "我正在处理你的请求...";
  } catch (error) {
    console.error('处理消息失败:', error.message);
    return "抱歉，我遇到了一些问题，请稍后再试...";
  }
}

// 登录事件
bot.on('login', () => {
  console.log('机器人已登录');
  
  // 初始化pathfinder movements
  const mcData = require('minecraft-data')(bot.version);
  const defaultMove = new Movements(bot, mcData);
  bot.pathfinder.setMovements(defaultMove);
  
  // 初始化技能管理器
  skillManager = new SkillManager(bot);
  console.log('技能系统已加载');
  
  // 初始化API客户端
  apiClient = new APIClient(config, bot, skillManager);
  apiClient.connectWebSocket();
  console.log('正在连接后端...');
});

// 监听聊天事件
bot.on("chat", async (username, message) => {
  // 忽略机器人自己的消息
  if (username === bot.username) return;

  // 检查消息中是否包含 @机器人用户名（不区分大小写）
  const mentionPattern = new RegExp(`@${bot.username}`, "i");
  if (mentionPattern.test(message)) {
    // 提取用户消息
    const userMessage = message.replace(mentionPattern, "").trim() || "你好";
    
    console.log(`收到来自 ${username} 的消息: ${userMessage}`);
    
    // 处理消息
    const reply = await processUserMessage(username, userMessage);
    
    // 回复
    bot.chat(`@${username} ${reply}`);
  }
});

// 错误处理
bot.on('error', (err) => {
  console.error('错误:', err);
});

// 被踢出事件
bot.on('kicked', (reason) => {
  console.log('被踢出:', reason);
});

// 断开连接事件
bot.on('end', (reason) => {
  console.log('连接结束:', reason);
  if (apiClient) {
    apiClient.disconnect();
  }
});

