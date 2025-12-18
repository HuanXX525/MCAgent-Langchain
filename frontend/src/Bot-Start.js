const mineflayer = require("mineflayer");

// 启动配置
const options = {
// 服务器地址
    host: "localhost",
// 服务器端口号
    port: 12345,
// 用户名
    username: "Alice",
// 无密码只能离线登录
// password: "password"
};

const bot = mineflayer.createBot(options);

function processUserMessag(message) {
    return message
}


// 监听聊天事件
bot.on("chat", (username, message) => {
  // 忽略机器人自己的消息
  if (username === bot.username) return;

  // 检查消息中是否包含 @机器人用户名（不区分大小写）
  const mentionPattern = new RegExp(`@${bot.username}`, "i");
  if (mentionPattern.test(message)) {
    // 提取并回复 @ 后的内容（去除 @机器人名称 部分）
    const userMessage =
          message.replace(mentionPattern, "").trim() || "有人@了机器人但没有任何内容";
      
    reply = processUserMessag(userMessage)  
    
    bot.chat(`@${username} ${reply}`);
  }
});

// 错误处理
bot.on('error', (err) => {
  console.error('错误:', err);
});

// 登录事件
bot.on('login', () => {
  console.log('机器人已登录');
});

// 被踢出事件
bot.on('kicked', (reason) => {
  console.log('被踢出:', reason);
});

// 断开连接事件
bot.on('end', (reason) => {
  console.log('连接结束:', reason);
});

