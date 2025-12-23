const mineflayer = require("mineflayer");
const { pathfinder, Movements, goals } = require("mineflayer-pathfinder");
const GoalFollow = goals.GoalFollow;
const { loadConfig } = require('./config');

const config = loadConfig();
console.log('配置已加载');

const bot = mineflayer.createBot(config.minecraft);

bot.loadPlugin(pathfinder);

function followPlayer(nearByDistance = 1, continuouslyFollow=false) {
    const targetPlayer = bot.players["Huanxx"];
    if (!targetPlayer) {
        bot.chat("我找不到你了！")
        return
    }
    const mcData = require('minecraft-data')(bot.version);
    const movements = new Movements(bot, mcData);
    bot.pathfinder.setMovements(movements);

    const goal = new GoalFollow(targetPlayer.entity, nearByDistance);
    bot.pathfinder.setGoal(goal, false);
}

bot.once('spawn', followPlayer)


bot.on("path_update", () => {
  console.log("路径更新");
});
bot.on("goal_updated", () => {
  console.log("目标更新");
});
bot.on("path_reset", () => {
  console.log("路径重置");
});
bot.on("path_stop", () => {
  console.log("路径停止");
});



