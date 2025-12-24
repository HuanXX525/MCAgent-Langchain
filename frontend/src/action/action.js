const { sendMessage } = require("../utils");
const mineflayer = require("mineflayer");
const { pathfinder, Movements, goals } = require("mineflayer-pathfinder");
const GoalFollow = goals.GoalFollow;
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


module.exports = { followPlayerOnce };
