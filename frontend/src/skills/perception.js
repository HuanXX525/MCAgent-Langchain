class PerceptionSkill {
  constructor(bot) {
    this.bot = bot;
  }

  getGameState() {
    return {
      position: {
        x: this.bot.entity.position.x,
        y: this.bot.entity.position.y,
        z: this.bot.entity.position.z
      },
      health: this.bot.health,
      food: this.bot.food,
      gameMode: this.bot.game.gameMode,
      dimension: this.bot.game.dimension,
      time: this.bot.time.timeOfDay,
      weather: {
        isRaining: this.bot.isRaining,
        thunderState: this.bot.thunderState
      }
    };
  }

  getInventory() {
    return this.bot.inventory.items().map(item => ({
      name: item.name,
      count: item.count,
      slot: item.slot,
      displayName: item.displayName
    }));
  }

  getNearbyEntities(range = 16) {
    const entities = Object.values(this.bot.entities)
      .filter(e => {
        if (!e.position) return false;
        const distance = e.position.distanceTo(this.bot.entity.position);
        return distance <= range && distance > 0;
      })
      .map(e => ({
        type: e.type,
        name: e.name || e.displayName || e.username,
        position: {
          x: e.position.x,
          y: e.position.y,
          z: e.position.z
        },
        distance: e.position.distanceTo(this.bot.entity.position)
      }));
    return entities;
  }

  getNearbyBlocks(blockNames, range = 16) {
    try {
      const mcData = require('minecraft-data')(this.bot.version);
      const blockTypes = blockNames.map(name => mcData.blocksByName[name]?.id).filter(id => id);
      
      if (blockTypes.length === 0) {
        return [];
      }

      const blocks = this.bot.findBlocks({
        matching: blockTypes,
        maxDistance: range,
        count: 100
      });

      return blocks.map(pos => {
        const block = this.bot.blockAt(pos);
        return {
          position: { x: pos.x, y: pos.y, z: pos.z },
          name: block ? block.name : 'unknown',
          distance: pos.distanceTo(this.bot.entity.position)
        };
      });
    } catch (error) {
      console.error('获取附近方块失败:', error);
      return [];
    }
  }

  getBlockAt(x, y, z) {
    const Vec3 = require('vec3');
    const block = this.bot.blockAt(new Vec3(x, y, z));
    if (!block) {
      return { success: false, error: '方块未找到' };
    }
    return {
      success: true,
      name: block.name,
      position: { x, y, z },
      type: block.type,
      hardness: block.hardness
    };
  }

  getNearbyPlayers(range = 32) {
    const players = Object.values(this.bot.players)
      .filter(p => {
        if (!p.entity || p.username === this.bot.username) return false;
        const distance = p.entity.position.distanceTo(this.bot.entity.position);
        return distance <= range;
      })
      .map(p => ({
        username: p.username,
        position: {
          x: p.entity.position.x,
          y: p.entity.position.y,
          z: p.entity.position.z
        },
        distance: p.entity.position.distanceTo(this.bot.entity.position)
      }));
    return players;
  }
}

module.exports = PerceptionSkill;
