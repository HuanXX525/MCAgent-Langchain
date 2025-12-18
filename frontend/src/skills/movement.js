const { goals } = require('mineflayer-pathfinder');
const Vec3 = require('vec3');

class MovementSkill {
  constructor(bot) {
    this.bot = bot;
  }

  async moveTo(x, y, z) {
    try {
      const goal = new goals.GoalBlock(x, y, z);
      await this.bot.pathfinder.goto(goal);
      return { 
        success: true, 
        position: {
          x: this.bot.entity.position.x,
          y: this.bot.entity.position.y,
          z: this.bot.entity.position.z
        }
      };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  async followPlayer(playerName, distance = 3) {
    try {
      const player = this.bot.players[playerName]?.entity;
      if (!player) {
        throw new Error(`玩家 ${playerName} 未找到`);
      }
      
      const goal = new goals.GoalFollow(player, distance);
      this.bot.pathfinder.setGoal(goal, true);
      return { success: true, following: playerName };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  stop() {
    this.bot.pathfinder.setGoal(null);
    return { success: true, message: '已停止移动' };
  }

  async comeToMe(playerName) {
    try {
      const player = this.bot.players[playerName]?.entity;
      if (!player) {
        throw new Error(`玩家 ${playerName} 未找到`);
      }
      
      const goal = new goals.GoalNear(
        player.position.x,
        player.position.y,
        player.position.z,
        1
      );
      await this.bot.pathfinder.goto(goal);
      return { success: true, message: `已到达 ${playerName} 身边` };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }
}

module.exports = MovementSkill;
