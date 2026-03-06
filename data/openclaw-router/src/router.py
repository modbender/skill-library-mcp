"""
模型路由核心模块
根据自评得分选择最佳模型
"""

from typing import Dict, Optional
from datetime import datetime


class ModelRouter:
    """模型路由器"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.primary_model = config.get("primary_model")
        self.verifier_model = config.get("verifier_model")
        self.expert_model = config.get("expert_model")
        self.thresholds = config.get("thresholds", {})
    
    def select_model(self, self_assessment_score: float, 
                     task_type: str = "general",
                     user_tags: Optional[list] = None) -> Dict:
        """
        根据自评得分选择模型
        
        Args:
            self_assessment_score: 自评得分 (1-5 分)
            task_type: 任务类型 (code/creative/analysis/strategic/learning/daily)
            user_tags: 用户标签 (e.g., ["[BEST]", "[FAST]"])
        
        Returns:
            选择的模型配置
        """
        # 处理用户标签覆盖
        if user_tags:
            return self._handle_user_tags(user_tags, task_type)
        
        # 获取阈值
        auto_pass = self.thresholds.get("auto_pass", 3.5)
        verify_min = self.thresholds.get("verify_min", 3.0)
        verify_max = self.thresholds.get("verify_max", 3.5)
        escalate_below = self.thresholds.get("escalate_below", 3.0)
        
        # 模型选择逻辑
        if self_assessment_score >= auto_pass:
            return self._select_local_or_primary()
        elif verify_min <= self_assessment_score < verify_max:
            return self._select_with_verification()
        elif self_assessment_score < escalate_below:
            return self._select_expert()
        else:
            return self._select_local_or_primary()
    
    def _handle_user_tags(self, user_tags: list, task_type: str) -> Dict:
        """处理用户标签覆盖"""
        tag_mapping = {
            "[L1]": self._select_local_or_primary,
            "[L2]": self._select_verifier,
            "[L3]": self._select_expert,
            "[BEST]": self._select_expert,
            "[FAST]": self._select_local_or_primary,
            "[CHEAP]": self._select_local_or_primary,
            "[VERIFY]": self._select_with_verification
        }
        
        for tag in user_tags:
            if tag in tag_mapping:
                return tag_mapping[tag]()
        
        # 无匹配标签，按任务类型选择
        return self._select_by_task_type(task_type)
    
    def _select_by_task_type(self, task_type: str) -> Dict:
        """根据任务类型选择"""
        task_model_mapping = {
            "code": self._select_local_or_primary,
            "creative": self._select_verifier,
            "analysis": self._select_verifier,
            "strategic": self._select_expert,
            "learning": self._select_local_or_primary,
            "daily": self._select_local_or_primary
        }
        
        selector = task_model_mapping.get(task_type, self._select_local_or_primary)
        return selector()
    
    def _select_local_or_primary(self) -> Dict:
        """选择本地或主路由模型"""
        if self.primary_model:
            return {
                "selected": True,
                "model": self.primary_model,
                "reason": "自评得分高，本地/主路由可胜任",
                "requires_verification": False
            }
        return self._select_verifier()
    
    def _select_verifier(self) -> Dict:
        """选择验证模型"""
        if self.verifier_model:
            return {
                "selected": True,
                "model": self.verifier_model,
                "reason": "需要验证",
                "requires_verification": True
            }
        return self._select_expert()
    
    def _select_with_verification(self) -> Dict:
        """选择带验证的流程"""
        if self.verifier_model:
            return {
                "selected": True,
                "model": self.primary_model or self.verifier_model,
                "verifier": self.verifier_model,
                "reason": "边界情况，需要验证",
                "requires_verification": True
            }
        return self._select_expert()
    
    def _select_expert(self) -> Dict:
        """选择专家模型"""
        if self.expert_model:
            return {
                "selected": True,
                "model": self.expert_model,
                "reason": "复杂任务，需要专家模型",
                "requires_verification": False
            }
        
        # 降级到验证模型
        return self._select_verifier()
    
    def calculate_cost(self, input_tokens: int, output_tokens: int, 
                       model: Optional[Dict] = None) -> Dict:
        """
        计算成本
        
        Args:
            input_tokens: 输入 token 数
            output_tokens: 输出 token 数
            model: 使用的模型（如不传则使用当前选中的）
        
        Returns:
            成本信息
        """
        if not model:
            model = self.primary_model
        
        if not model:
            return {"cost": 0, "currency": "CNY"}
        
        cost_per_1k = model.get("cost_per_1k", 0)
        total_tokens = input_tokens + output_tokens
        cost = round((total_tokens / 1000) * cost_per_1k, 4)
        
        return {
            "cost": cost,
            "currency": model.get("currency", "CNY"),
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "model_id": model.get("id", "unknown")
        }
