const { goals } = require('mineflayer-pathfinder');
const Vec3 = require('vec3');

class MiningSkill {
  constructor(bot) {
    this.bot = bot;
  }

  async digBlock(x, y, z) {
    try {
      const block = this.bot.blockAt(new Vec3(x, y, z));
      if (!block) {
        throw new Error('方块未找到');
      }
      
      if (!this.bot.canDigBlock(block)) {
        throw new Error('无法挖掘此方块');
      }

      await this.bot.dig(block);
      return { success: true, block: block.name, position: { x, y, z } };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  async findAndMine(blockName, count = 1) {
    try {
      const mcData = require('minecraft-data')(this.bot.version);
      const blockType = mcData.blocksByName[blockName];
      
      if (!blockType) {
        throw new Error(`未知方块: ${blockName}`);
      }

      let mined = 0;
      const minedBlocks = [];

      while (mined < count) {
        const block = this.bot.findBlock({
          matching: blockType.id,
          maxDistance: 64
        });

        if (!block) {
          throw new Error(`附近未找到 ${blockName}`);
        }

        // 移动到方块附近
        const goal = new goals.GoalBlock(block.position.x, block.position.y, block.position.z);
        await this.bot.pathfinder.goto(goal);
        
        // 挖掘方块
        await this.bot.dig(block);
        mined++;
        minedBlocks.push({
          x: block.position.x,
          y: block.position.y,
          z: block.position.z
        });
      }

      return { 
        success: true, 
        mined: mined, 
        blockName: blockName,
        positions: minedBlocks
      };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  async mineBlocksInArea(x1, y1, z1, x2, y2, z2, blockName = null) {
    try {
      const minedBlocks = [];
      
      for (let x = Math.min(x1, x2); x <= Math.max(x1, x2); x++) {
        for (let y = Math.min(y1, y2); y <= Math.max(y1, y2); y++) {
          for (let z = Math.min(z1, z2); z <= Math.max(z1, z2); z++) {
            const block = this.bot.blockAt(new Vec3(x, y, z));
            
            if (block && block.name !== 'air') {
              if (blockName && block.name !== blockName) continue;
              
              if (this.bot.canDigBlock(block)) {
                await this.bot.pathfinder.goto(new goals.GoalBlock(x, y, z));
                await this.bot.dig(block);
                minedBlocks.push({ x, y, z, name: block.name });
              }
            }
          }
        }
      }

      return { 
        success: true, 
        minedCount: minedBlocks.length,
        blocks: minedBlocks
      };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }
}

module.exports = MiningSkill;
