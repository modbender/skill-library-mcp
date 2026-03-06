"""
配置管理模块
保存、加载、验证配置
"""

import yaml
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime


class ConfigManager:
    """配置管理器"""
    
    DEFAULT_CONFIG_PATH = Path.home() / ".openclaw" / "router_config.yaml"
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or self.DEFAULT_CONFIG_PATH
        self.config: Optional[Dict] = None
    
    def load_config(self) -> Optional[Dict]:
        """加载配置"""
        if not self.config_path.exists():
            return None
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
            return self.config
        except Exception as e:
            print(f"加载配置失败：{e}")
            return None
    
    def save_config(self, config: Dict) -> bool:
        """保存配置"""
        try:
            # 确保目录存在
            if isinstance(self.config_path, str):
                from pathlib import Path
                self.config_path = Path(self.config_path)
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 添加元数据
            config["last_updated"] = datetime.now().isoformat()
            
            # 保存为 YAML
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
            
            self.config = config
            return True
        except Exception as e:
            print(f"保存配置失败：{e}")
            return False
    
    def validate_config(self, config: Optional[Dict] = None) -> Dict:
        """
        验证配置
        
        Returns:
            {"valid": bool, "errors": list, "warnings": list}
        """
        if not config:
            config = self.config
        
        errors = []
        warnings = []
        
        # 检查必需字段
        if not config:
            errors.append("配置为空")
            return {"valid": False, "errors": errors, "warnings": warnings}
        
        # 检查版本
        if "version" not in config:
            warnings.append("缺少版本号")
        
        # 检查模型配置
        models = config.get("models", {})
        if not models.get("primary"):
            warnings.append("未配置主路由模型")
        
        # 检查阈值
        thresholds = config.get("thresholds", {})
        if not thresholds:
            warnings.append("未配置阈值")
        else:
            auto_pass = thresholds.get("auto_pass", 0)
            if auto_pass < 1 or auto_pass > 5:
                errors.append(f"无效的 auto_pass 值：{auto_pass} (应在 1-5 之间)")
        
        # 检查预算
        budget = config.get("budget", {})
        if budget:
            monthly = budget.get("monthly", 0)
            if monthly < 0:
                errors.append(f"无效的月度预算：{monthly}")
            elif monthly > 10000:
                warnings.append(f"月度预算过高：{monthly}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def get_model_info(self, model_type: str) -> Optional[Dict]:
        """获取模型信息"""
        if not self.config:
            self.load_config()
        
        if not self.config:
            return None
        
        models = self.config.get("models", {})
        return models.get(model_type)
    
    def get_threshold(self, threshold_name: str) -> float:
        """获取阈值"""
        if not self.config:
            self.load_config()
        
        if not self.config:
            return 3.5  # 默认值
        
        thresholds = self.config.get("thresholds", {})
        return thresholds.get(threshold_name, 3.5)
    
    def update_budget(self, monthly_budget: float) -> bool:
        """更新预算"""
        if not self.config:
            self.load_config()
        
        if not self.config:
            return False
        
        if "budget" not in self.config:
            self.config["budget"] = {}
        
        self.config["budget"]["monthly"] = monthly_budget
        self.config["budget"]["daily_average"] = round(monthly_budget / 30, 2)
        
        return self.save_config(self.config)
    
    def reset_config(self) -> bool:
        """重置配置"""
        if self.config_path.exists():
            try:
                self.config_path.unlink()
                self.config = None
                return True
            except Exception as e:
                print(f"重置配置失败：{e}")
                return False
        return True
