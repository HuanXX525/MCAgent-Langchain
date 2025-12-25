const { followPlayerOnce, followPlayerContinouslyToggle } = require('./action');
const APIClient = require('../apiClient');

class ActionManager {
  static instance = null;
  actionMap;
  constructor() {
    if (ActionManager.instance) {
      return ActionManager.instance; // 如果已有实例，直接返回旧的
    }
    this.actionMap = new Map();
    // 初始化逻辑
    ActionManager.instance = this; // 缓存实例
  }

  registeAction(actionName, actionFunction) {
    this.actionMap.set(actionName, actionFunction);
  }

  removeAction(actionName) {
    this.actionMap.delete(actionName);
  }

  async executeAction(actionName, actionID, args) {
    const actionFunction = this.actionMap.get(actionName);
    if (actionFunction) {
      const message = await actionFunction(args); // 执行动作（如：走路到某地）
      console.log(`[ActionManager] 执行结束: ${message}`);

      // 【关键】直接返回结果，不要在这里 send！
      return message;
    } else {
      throw new Error(`Action ${actionName} not found`);
    }
  }

  // async executeAction(actionName, actionID,args) {
  //     const actionFunction = this.actionMap.get(actionName);
  //     if (actionFunction) {
  //         const message = await actionFunction(args);
  //         const ToolMessage = {
  //             type: "action",
  //             data: {
  //                 action_id: actionID,
  //                 message: message,
  //                 action: actionName,
  //             }
  //         }
  //         console.log(`工具执行结束，发送${message}`);
  //         await APIClient.instance.send(ToolMessage);
  //     } else {
  //         throw new Error(`Action ${actionName} not found`);
  //     }
  // }
}

new ActionManager();

ActionManager.instance.registeAction("followPlayerOnce", followPlayerOnce);
ActionManager.instance.registeAction("followPlayerContinouslyToggle", followPlayerContinouslyToggle);

module.exports = ActionManager;
