# Web 配置界面

## 使用说明

### 1. 安装后端依赖

确保后端依赖已安装：

```bash
cd backend
conda activate MCBot
pip install -r requirements.txt
```

### 2. 启动后端服务

```bash
cd backend
conda activate MCBot
python main.py
```

### 3. 访问配置界面

在浏览器中打开：

```
http://localhost:8000
```

### 4. 配置说明

配置界面包含以下部分：

#### ⚙️ Minecraft 服务器配置
- **服务器地址**: Minecraft服务器的IP地址
- **端口**: 服务器端口（默认25565）
- **用户名/邮箱**: 机器人的用户名或微软账号邮箱
- **游戏版本**: Minecraft版本（如1.20.1）
- **认证方式**: 
  - `offline`: 离线模式
  - `microsoft`: 微软账号
  - `mojang`: Mojang账号
- **机器人名称**: 机器人的显示名称

#### 🤖 后端服务配置
- **后端地址**: 后端服务器地址（默认localhost）
- **后端端口**: 后端服务器端口（默认8000）

#### 🧠 GPT API 配置
- **API Key**: OpenAI或其他兼容服务的API密钥
- **API Base URL**: API服务地址
- **模型**: 使用的GPT模型（如gpt-4o-mini）
- **Temperature**: 生成文本的随机性（0-2）
- **Max Tokens**: 最大生成令牌数

#### 🔧 机器人设置
- **响应超时**: 等待响应的最长时间（秒）
- **最大重试次数**: 失败后的重试次数
- **调试模式**: 是否启用详细日志

### 5. 保存配置

点击"💾 保存配置"按钮后，配置会立即保存到 `config.json` 文件。

**注意**: 修改配置后需要重启前端和后端服务才能生效。

### 6. 重新加载配置

点击"🔄 重新加载"按钮可以从服务器重新加载当前配置。

## 技术实现

- **前端**: 纯HTML/CSS/JavaScript，无需额外依赖
- **后端**: FastAPI提供REST API和静态文件服务
- **通信**: 通过HTTP REST API读取和保存配置
- **存储**: 配置保存在项目根目录的 `config.json` 文件中

## 安全提示

⚠️ **重要**: 
- 不要在公网环境下暴露此配置界面
- API密钥等敏感信息会以明文形式保存在config.json中
- 建议仅在本地网络或受信任的环境中使用
