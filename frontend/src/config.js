const fs = require('fs');
const path = require('path');

function loadConfig() {
  // RELASE CHANGE
  const configPath = path.join(__dirname, '../../configdev.json');
  const configData = fs.readFileSync(configPath, 'utf-8');
  return JSON.parse(configData);
}

module.exports = { loadConfig };
