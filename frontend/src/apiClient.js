const WebSocket = require('ws');
// const ActionManager = require('./action/actionManager')
const { EventEmitter } = require('events'); // 引入 Node.js 原生事件触发器
class APIClient extends EventEmitter {
  static instance = null;
  constructor(config) {
    super();
    if (APIClient.instance) {
      return APIClient.instance;
    }
    APIClient.instance = this;
    this.config = config;
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
        global.bot.chat(message.data.message);
        break;
      case "action":
        // 【关键改动】不再直接调用 ActionManager
        // 而是发出一个名为 'onAction' 的事件，把数据传出去
        this.emit("onAction", message.data);
        break;
      // 其他的行为控制信息获取请求等等，可以在这里处理
      default:
        console.log("未知消息类型:", message.type);
    }
  }

  // 统一的发送方法
  send(payload) {
    console.log("进入发送方法")
    console.log("WebSocket状态:", this.ws.readyState);
    console.log(this.ws.url);
    // console.log("WebSocket对象:", this.ws);
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      console.log("发送数据:", payload);
      this.ws.send(JSON.stringify(payload));
    } else {
      console.error("发送失败：WebSocket 未连接");
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
