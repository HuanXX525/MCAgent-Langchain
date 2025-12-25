/**
 * 在此文件定义所有伙伴的技能，便于管理。
 * 导出后，在actionManager.js 中注册
 * ！！！ 注册时的名称应该与“ws后端对应”
 * 
 * 
 * 
 */

const { sendMessage } = require("../utils");
const mineflayer = require("mineflayer");
const { pathfinder, Movements, goals } = require("mineflayer-pathfinder");
const GoalFollow = goals.GoalFollow;


// 把伙伴所有的技能写在这里，便于管理


/**
 * 单次走到玩家附近
 */
async function followPlayerOnce({ nearByDistance=1, playerName }) {
  const targetPlayer = global.bot.players[playerName];
  if (!targetPlayer || !targetPlayer.entity) {
    return "玩家离你太远了，找不到玩家";
  }

  const mcData = require("minecraft-data")(global.bot.version);
  const movements = new Movements(global.bot, mcData);
  global.bot.pathfinder.setMovements(movements);

  const goal = new GoalFollow(targetPlayer.entity, nearByDistance);

  // 返回一个 Promise，直到到达目标才结束
  return new Promise((resolve) => {
    global.bot.pathfinder.setGoal(goal, false);
    // 使用 global.bot.once 监听单次事件，避免内存泄漏
    global.bot.once("goal_reached", () => {
      console.log("已到达目标");
      resolve("成功到达玩家附近"); // 只有调用了 resolve，外部的 await 才会继续执行
    });
  });
}

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




// 把伙伴所有的技能写在这里，便于管理


module.exports = { followPlayerOnce, followPlayerContinouslyToggle };
