const axios = require('axios');
const WebSocket = require('ws');
const ActionManager = require('./action/actionManager')
class APIClient {
  static instance = null;
  constructor(config, bot) {
    if (APIClient.instance) {
      return APIClient.instance;
    }
    APIClient.instance = this;
    this.config = config;
    this.bot = bot;
    this.apiUrl = config.backend.api_url;
    this.wsUrl = config.backend.ws_url;
    this.ws = null;
    this.reconnectInterval = 5000;
    this.isConnecting = false;
  }

  async sendMessage(username, message) {
    // 向后端发送玩家消息，也就是玩家通过我的世界聊天框输入的文本
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.error("WebSocket 未连接，无法发送消息");
      throw new Error("WebSocket 连接未就绪");
    }

    // 构造符合后端协议的消息
    const chatMessage = {
      type: "chat",
      data: {
        player: username,
        message: message,
      },
    };
    // 发送消息（无需 await，因为是 fire-and-forget）
    // console.log("发送消息:", message);
    this.ws.send(JSON.stringify(chatMessage));
  }

  connectWebSocket() {
    if (this.isConnecting) {
      return;
    }

    this.isConnecting = true;
    console.log("正在连接WebSocket...");

    try {
      this.ws = new WebSocket(this.wsUrl);

      this.ws.on("open", () => {
        console.log("WebSocket已连接到后端");
        this.isConnecting = false;
      });

      this.ws.on("message", async (data) => {
        try {
          const message = JSON.parse(data.toString());
          await this.handleWebSocketMessage(message);
        } catch (error) {
          console.error("处理WebSocket消息失败:", error);
        }
      });

      this.ws.on("error", (error) => {
        console.error("WebSocket错误:", error.message);
        this.isConnecting = false;
      });

      this.ws.on("close", () => {
        console.log("WebSocket连接已关闭，将在5秒后重连...");
        this.isConnecting = false;
        setTimeout(() => this.connectWebSocket(), this.reconnectInterval);
      });
    } catch (error) {
      console.error("创建WebSocket连接失败:", error);
      this.isConnecting = false;
      setTimeout(() => this.connectWebSocket(), this.reconnectInterval);
    }
  }

  async handleWebSocketMessage(message) {
    // 在这里处理从后端接收到的消息
    console.log("收到WebSocket消息:", message.type);

    switch (message.type) {
      case "chat":
        // 聊天消息，转发给玩家，在我的世界聊天框显示出来
        this.bot.chat(message.data.message)
        break;
      case "action":
        const data = message.data;
        ActionManager.instance.executeAction(data.action, data.action_id, data.args);
      
      // 其他的行为控制信息获取请求等等，可以在这里处理
      default:
        console.log("未知消息类型:", message.type);
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}

module.exports = APIClient;
