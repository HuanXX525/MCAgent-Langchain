const MovementSkill = require('./skills/movement');
const MiningSkill = require('./skills/mining');
const PerceptionSkill = require('./skills/perception');

class SkillManager {
  constructor(bot) {
    this.bot = bot;
    this.skills = {
      movement: new MovementSkill(bot),
      mining: new MiningSkill(bot),
      perception: new PerceptionSkill(bot)
    };
  }

  async executeSkill(skillName, method, params) {
    try {
      const skill = this.skills[skillName];
      if (!skill) {
        throw new Error(`技能 ${skillName} 未找到`);
      }

      if (typeof skill[method] !== 'function') {
        throw new Error(`方法 ${method} 在技能 ${skillName} 中未找到`);
      }

      const result = await skill[method](...params);
      return result;
    } catch (error) {
      console.error(`执行技能失败: ${skillName}.${method}`, error);
      return { success: false, error: error.message };
    }
  }

  getAvailableSkills() {
    return Object.keys(this.skills).map(skillName => {
      const skill = this.skills[skillName];
      const methods = Object.getOwnPropertyNames(Object.getPrototypeOf(skill))
        .filter(m => m !== 'constructor' && typeof skill[m] === 'function');
      
      return {
        name: skillName,
        methods: methods
      };
    });
  }

  getSkillInfo() {
    const skillsInfo = {
      movement: {
        description: '移动相关技能',
        methods: {
          moveTo: '移动到指定坐标 (x, y, z)',
          followPlayer: '跟随玩家 (playerName, distance)',
          comeToMe: '来到玩家身边 (playerName)',
          stop: '停止移动'
        }
      },
      mining: {
        description: '挖掘相关技能',
        methods: {
          digBlock: '挖掘指定坐标的方块 (x, y, z)',
          findAndMine: '寻找并挖掘指定方块 (blockName, count)',
          mineBlocksInArea: '挖掘区域内的方块 (x1, y1, z1, x2, y2, z2, blockName)'
        }
      },
      perception: {
        description: '感知相关技能',
        methods: {
          getGameState: '获取游戏状态',
          getInventory: '获取物品栏',
          getNearbyEntities: '获取附近实体 (range)',
          getNearbyBlocks: '获取附近方块 (blockNames, range)',
          getBlockAt: '获取指定坐标的方块 (x, y, z)',
          getNearbyPlayers: '获取附近玩家 (range)'
        }
      }
    };
    return skillsInfo;
  }
}

module.exports = SkillManager;
