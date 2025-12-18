const fs = require('fs');
const path = require('path');

function loadConfig() {
  const configPath = path.join(__dirname, '../../config.json');
  const configData = fs.readFileSync(configPath, 'utf-8');
  return JSON.parse(configData);
}

module.exports = { loadConfig };
