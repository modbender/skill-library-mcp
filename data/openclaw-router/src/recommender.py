"""
配置推荐模块
根据环境检测结果生成推荐配置
"""

from typing import Dict, Optional
from datetime import datetime


class ConfigRecommender:
    """配置推荐器"""
    
    def __init__(self):
        self.thresholds_presets = {
            "balanced": {
                "auto_pass": 3.5,
                "verify_min": 3.0,
                "verify_max": 3.5,
                "escalate_below": 3.0
            },
            "quality": {
                "auto_pass": 4.0,
                "verify_min": 3.5,
                "verify_max": 4.0,
                "escalate_below": 3.5
            },
            "economy": {
                "auto_pass": 3.0,
                "verify_min": 2.5,
                "verify_max": 3.0,
                "escalate_below": 2.5
            },
            "speed": {
                "auto_pass": 3.0,
                "verify_min": 0,
                "verify_max": 0,
                "escalate_below": 2.5
            }
        }
    
    def generate_recommendation(self, detection: Dict) -> Dict:
        """根据检测结果生成推荐配置"""
        config = {
            "version": "3.0.0",
            "created_at": datetime.now().isoformat(),
            "auto_detected": True
        }
        
        # 确定部署模式
        has_local = detection["ollama"]["installed"] and len(detection["ollama"]["models"]) > 0
        has_cloud = any([
            detection["dashscope"]["configured"],
            detection["openai"]["configured"],
            detection["anthropic"]["configured"]
        ])
        
        # 确定主路由模型
        config["primary_model"] = self._select_primary_model(detection, has_local, has_cloud)
        
        # 确定验证模型
        config["verifier_model"] = self._select_verifier_model(detection, has_cloud)
        
        # 确定专家模型
        config["expert_model"] = self._select_expert_model(detection, has_cloud)
        
        # 确定阈值模式
        config["thresholds"] = self._select_thresholds(has_local)
        
        # 预算建议
        config["budget_suggestion"] = self._calculate_budget(has_local, has_cloud)
        
        return config
    
    def _select_primary_model(self, detection: Dict, has_local: bool, has_cloud: bool) -> Optional[Dict]:
        """选择主路由模型"""
        if has_local:
            # 优先选择 14b 模型
            ollama_models = detection["ollama"]["models"]
            if any("14b" in m for m in ollama_models):
                return {
                    "id": "qwen2.5:14b-32k",
                    "location": "local",
                    "cost_per_1k": 0,
                    "reason": "本地最佳平衡模型"
                }
            elif len(ollama_models) > 0:
                return {
                    "id": ollama_models[0],
                    "location": "local",
                    "cost_per_1k": 0,
                    "reason": "本地可用模型"
                }
        
        if has_cloud and detection["dashscope"]["configured"]:
            return {
                "id": "dashscope/qwen3.5-plus",
                "location": "cloud",
                "cost_per_1k": 0.002,
                "reason": "云端最佳性价比"
            }
        
        return None
    
    def _select_verifier_model(self, detection: Dict, has_cloud: bool) -> Optional[Dict]:
        """选择验证模型"""
        if has_cloud and detection["dashscope"]["configured"]:
            return {
                "id": "dashscope/qwen3.5-plus",
                "location": "cloud",
                "cost_per_1k": 0.002,
                "reason": "性价比高，适合验证"
            }
        return None
    
    def _select_expert_model(self, detection: Dict, has_cloud: bool) -> Optional[Dict]:
        """选择专家模型"""
        if has_cloud and detection["dashscope"]["configured"]:
            return {
                "id": "dashscope/qwen3-max",
                "location": "cloud",
                "cost_per_1k": 0.04,
                "reason": "最强推理，适合复杂任务"
            }
        return None
    
    def _select_thresholds(self, has_local: bool) -> Dict:
        """选择阈值模式"""
        if has_local:
            return {
                "mode": "balanced",
                **self.thresholds_presets["balanced"]
            }
        else:
            return {
                "mode": "conservative",
                **self.thresholds_presets["quality"]
            }
    
    def _calculate_budget(self, has_local: bool, has_cloud: bool) -> Dict:
        """计算预算建议"""
        if has_local and has_cloud:
            monthly = 100
            note = "混合部署，成本适中"
        elif has_local:
            monthly = 20
            note = "纯本地部署，成本最低"
        elif has_cloud:
            monthly = 300
            note = "纯云端部署，成本较高"
        else:
            monthly = 0
            note = "未检测到可用模型"
        
        return {
            "monthly": monthly,
            "daily_average": round(monthly / 30, 2),
            "currency": "CNY",
            "note": note
        }
