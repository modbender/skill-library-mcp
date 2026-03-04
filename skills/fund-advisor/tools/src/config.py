"""
配置管理模块
"""
import os
from pathlib import Path
from typing import Optional, Dict


FUND_ADVISOR_DATA_PATH = "FUND_ADVISOR_DATA_PATH"
QIEMAN_API_KEY = "QIEMAN_API_KEY"

DB_FILENAME = "fund_portfolio_v1.db"


def get_default_data_path() -> Path:
    """获取默认数据目录路径"""
    home_dir = Path.home()
    data_dir = home_dir / ".fund-advisor"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def get_data_path() -> Path:
    """获取数据目录路径
    
    优先级：
    1. 环境变量 FUND_ADVISOR_DATA_PATH
    2. 默认路径 $HOME/.fund-advisor
    """
    env_path = os.environ.get(FUND_ADVISOR_DATA_PATH)
    if env_path:
        data_dir = Path(env_path)
        data_dir.mkdir(parents=True, exist_ok=True)
        return data_dir
    return get_default_data_path()


def get_db_path() -> str:
    """获取数据库路径"""
    return str(get_data_path() / DB_FILENAME)


def get_api_key() -> Optional[str]:
    """从环境变量获取 API Key"""
    return os.environ.get(QIEMAN_API_KEY)


def is_api_key_configured() -> bool:
    """检查 API Key 是否已配置"""
    api_key = get_api_key()
    return api_key is not None and len(api_key) > 0 and api_key != "YOUR_API_KEY_HERE"


def get_qieman_mcp_config() -> Dict[str, str]:
    """获取 qieman-mcp 配置，优先使用环境变量中的 API Key"""
    api_key = get_api_key()
    if api_key:
        return {
            "baseUrl": f"https://stargate.yingmi.com/mcp/sse?apiKey={api_key}",
            "description": "基金投资工具包，提供基金、内容、投研、投顾等专业领域能力。"
        }
    return {
        "baseUrl": "https://stargate.yingmi.com/mcp/sse?apiKey=YOUR_API_KEY_HERE",
        "description": "基金投资工具包，提供基金、内容、投研、投顾等专业领域能力。"
    }
