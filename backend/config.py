import json
from pathlib import Path
from typing import Dict, Any

def load_config() -> Dict[str, Any]:
    """加载配置文件"""
    # RELEASE CHANGE
    config_path = Path(__file__).parent.parent / 'configdev.json'
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

CONFIG = load_config()

API_KEY = CONFIG['gpt']['api_key']
BASE_URL = CONFIG['gpt']['base_url']
MODEL = CONFIG['gpt']['model']

DB_URL = f"{CONFIG['db']['db']}://{CONFIG['db']['user']}:{CONFIG['db']['password']}@{CONFIG['db']['host']}:{CONFIG['db']['port']}/{CONFIG['db']['database']}"
