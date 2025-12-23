const { followPlayerOnce } = require('./action');
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

    async executeAction(actionName, actionID,args) {
        const actionFunction = this.actionMap.get(actionName);
        if (actionFunction) {
            message = await actionFunction(args);
            const ToolMessage = {
                type: "action",
                data: {
                    action_id: actionID,
                    message: message,
                    action: actionName,
                }
            }
            APIClient.instance.ws.send(JSON.stringify(ToolMessage));
        } else {
            throw new Error(`Action ${actionName} not found`);
        }
    }
}

new ActionManager();

ActionManager.instance.registeAction("followPlayerOnce", followPlayerOnce);

module.exports = ActionManager;
