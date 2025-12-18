const axios = require('axios');
const WebSocket = require('ws');

class APIClient {
  constructor(config, bot, skillManager) {
    this.config = config;
    this.bot = bot;
    this.skillManager = skillManager;
    this.apiUrl = config.backend.api_url;
    this.wsUrl = config.backend.ws_url;
    this.ws = null;
    this.reconnectInterval = 5000;
    this.isConnecting = false;
  }

  async sendMessage(username, message) {
    const perception = this.skillManager.skills.perception;
    const context = {
      gameState: perception.getGameState(),
      inventory: perception.getInventory(),
      nearbyEntities: perception.getNearbyEntities(16),
      nearbyPlayers: perception.getNearbyPlayers()
    };

    try {
      const response = await axios.post(`${this.apiUrl}/chat`, {
        username: username,
        message: message,
        context: context
      }, {
        timeout: this.config.bot.response_timeout * 1000
      });

      return response.data;
    } catch (error) {
      console.error('发送消息到后端失败:', error.message);
      throw error;
    }
  }

  connectWebSocket() {
    if (this.isConnecting) {
      return;
    }

    this.isConnecting = true;
    console.log('正在连接WebSocket...');

    try {
      this.ws = new WebSocket(this.wsUrl);

      this.ws.on('open', () => {
        console.log('WebSocket已连接到后端');
        this.isConnecting = false;
      });

      this.ws.on('message', async (data) => {
        try {
          const message = JSON.parse(data.toString());
          await this.handleWebSocketMessage(message);
        } catch (error) {
          console.error('处理WebSocket消息失败:', error);
        }
      });

      this.ws.on('error', (error) => {
        console.error('WebSocket错误:', error.message);
        this.isConnecting = false;
      });

      this.ws.on('close', () => {
        console.log('WebSocket连接已关闭，将在5秒后重连...');
        this.isConnecting = false;
        setTimeout(() => this.connectWebSocket(), this.reconnectInterval);
      });
    } catch (error) {
      console.error('创建WebSocket连接失败:', error);
      this.isConnecting = false;
      setTimeout(() => this.connectWebSocket(), this.reconnectInterval);
    }
  }

  async handleWebSocketMessage(message) {
    console.log('收到WebSocket消息:', message.type);

    switch (message.type) {
      case 'execute_action':
        await this.executeAction(message.data);
        break;
      case 'chat_response':
        this.bot.chat(message.data.text);
        break;
      case 'ping':
        this.sendPong();
        break;
      default:
        console.log('未知消息类型:', message.type);
    }
  }

  async executeAction(action) {
    console.log(`执行行动: ${action.skill}.${action.method}`, action.params);

    try {
      const result = await this.skillManager.executeSkill(
        action.skill,
        action.method,
        action.params
      );
      
      this.sendActionResult({
        success: true,
        action: action,
        result: result
      });
    } catch (error) {
      console.error('执行行动失败:', error);
      this.sendActionResult({
        success: false,
        action: action,
        error: error.message
      });
    }
  }

  sendActionResult(result) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'action_result',
        data: result
      }));
    }
  }

  sendPong() {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'pong'
      }));
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
