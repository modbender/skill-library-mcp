#!/usr/bin/env python3
"""
Investment Profile - User preference collection and opportunity filtering.

This module provides a convenient way for agents to collect user investment
preferences and filter opportunities accordingly.

Usage:
    from investment_profile import InvestmentProfile
    
    profile = InvestmentProfile()
    profile.chain = "ethereum"
    profile.capital_token = "USDC"
    profile.accept_il = False
    profile.reward_preference = "single"
    
    # Filter opportunities
    filtered = profile.filter_opportunities(opportunities)
"""

from typing import Optional, List, Dict, Any, Callable
import json


class InvestmentProfile:
    """
    Collect and store user investment preferences for opportunity filtering.
    
    This class helps agents:
    1. Ask the right questions to users
    2. Store preferences in a structured way
    3. Filter opportunities based on preferences
    """
    
    def __init__(self):
        # Required fields
        self.chain: Optional[str] = None
        self.capital_token: Optional[str] = None
        
        # Optional preference fields (None means "no preference / any")
        self.reward_preference: Optional[str] = None  # "single" | "multi" | "none" | None
        self.accept_il: Optional[bool] = None  # True | False | None
        self.underlying_preference: Optional[str] = None  # "rwa" | "onchain" | "mixed" | None
        
        # Additional constraints
        self.min_apy: Optional[float] = None
        self.max_apy: Optional[float] = None
        self.min_tvl: Optional[float] = None
    
    @classmethod
    def get_questions(cls) -> Dict[str, Any]:
        """
        Get the list of questions to ask users.
        
        Returns a structured dict that agents can use to build their UI.
        """
        return {
            "required": [
                {
                    "key": "chain",
                    "question": "您想在哪条链上投资？",
                    "description": "选择目标区块链",
                    "options": ["ethereum", "base", "arbitrum", "optimism"],
                    "type": "select"
                },
                {
                    "key": "capital_token",
                    "question": "您的投资本金是什么代币？",
                    "description": "例如：USDC, USDT, ETH, WBTC",
                    "examples": ["USDC", "USDT", "ETH"],
                    "type": "text"
                }
            ],
            "preference": [
                {
                    "key": "reward_preference",
                    "question": "您对奖励代币有什么偏好吗？",
                    "description": "有些产品奖励单一代币，有些奖励多种代币（如 CRV+CVX）",
                    "options": [
                        {"value": "single", "label": "只接受单一代币奖励", "description": "简单清晰，易于管理"},
                        {"value": "multi", "label": "可以接受多代币奖励", "description": "可能更高收益，但需要管理多种代币"},
                        {"value": "none", "label": "不需要奖励，只要基础收益", "description": "最稳定的收益结构"},
                        {"value": None, "label": "无特别偏好", "description": "都可以接受"}
                    ],
                    "type": "select"
                },
                {
                    "key": "accept_il",
                    "question": "您能接受无常损失（Impermanent Loss）吗？",
                    "description": "LP 类产品在价格波动时可能产生无常损失",
                    "options": [
                        {"value": False, "label": "不接受", "description": "只想要本金保障的产品，如借贷、单币质押"},
                        {"value": True, "label": "可以接受", "description": "理解并接受 LP 的无常损失风险"},
                        {"value": None, "label": "不确定/看情况", "description": "需要更多建议"}
                    ],
                    "type": "select"
                },
                {
                    "key": "underlying_preference",
                    "question": "您对底层资产有偏好吗？",
                    "description": "产品的底层资产类型",
                    "options": [
                        {"value": "onchain", "label": "纯链上合约", "description": "DeFi 原生协议，如 Aave、Compound"},
                        {"value": "rwa", "label": "现实世界资产 (RWA)", "description": "如国债代币化、美债收益"},
                        {"value": "mixed", "label": "混合资产", "description": "多种资产组合"},
                        {"value": None, "label": "无偏好", "description": "不限制底层资产类型"}
                    ],
                    "type": "select"
                }
            ],
            "constraints": [
                {
                    "key": "min_apy",
                    "question": "最低可接受的 APY 是多少？",
                    "description": "例如：5 表示至少 5%",
                    "type": "number",
                    "unit": "%"
                },
                {
                    "key": "max_apy",
                    "question": "最高 APY 上限（过滤过高风险）",
                    "description": "超过此 APY 的产品将被过滤，建议 30-50",
                    "type": "number",
                    "unit": "%"
                },
                {
                    "key": "min_tvl",
                    "question": "最低 TVL 要求？",
                    "description": "产品总锁仓价值，建议至少 $100万",
                    "type": "number",
                    "unit": "USD"
                }
            ]
        }
    
    def set_preferences(self, **kwargs) -> "InvestmentProfile":
        """
        Set multiple preferences at once.
        
        Example:
            profile.set_preferences(
                chain="ethereum",
                capital_token="USDC",
                accept_il=False,
                reward_preference="single"
            )
        """
        valid_fields = [
            'chain', 'capital_token', 'reward_preference', 'accept_il',
            'underlying_preference', 'min_apy', 'max_apy', 'min_tvl'
        ]
        
        for key, value in kwargs.items():
            if key in valid_fields:
                setattr(self, key, value)
        
        return self
    
    def is_valid(self) -> bool:
        """Check if required fields are set."""
        return self.chain is not None and self.capital_token is not None
    
    def _matches_reward_preference(self, opp: Dict[str, Any]) -> bool:
        """Check if opportunity matches reward preference."""
        if self.reward_preference is None:
            return True
        
        risk_signals = opp.get("risk_signals", {})
        reward_type = risk_signals.get("reward_type", "unknown")
        
        # Map preference to allowed types
        preference_map = {
            "single": ["single", "none"],
            "multi": ["multi"],
            "none": ["none"]
        }
        
        allowed = preference_map.get(self.reward_preference, [])
        return reward_type in allowed
    
    def _matches_il_preference(self, opp: Dict[str, Any]) -> bool:
        """Check if opportunity matches IL preference."""
        if self.accept_il is None:
            return True
        
        risk_signals = opp.get("risk_signals", {})
        has_il = risk_signals.get("has_il_risk", False)
        
        # If user doesn't accept IL, filter out products with IL risk
        if not self.accept_il and has_il:
            return False
        
        return True
    
    def _matches_underlying_preference(self, opp: Dict[str, Any]) -> bool:
        """Check if opportunity matches underlying asset preference."""
        if self.underlying_preference is None:
            return True
        
        risk_signals = opp.get("risk_signals", {})
        underlying_type = risk_signals.get("underlying_type", "unknown")
        
        # Exact match or "mixed" can satisfy "onchain" preference
        if self.underlying_preference == "onchain" and underlying_type in ["onchain", "mixed"]:
            return True
        
        return underlying_type == self.underlying_preference
    
    def _matches_constraints(self, opp: Dict[str, Any]) -> bool:
        """Check if opportunity matches numeric constraints."""
        apy = opp.get("apy", 0)
        tvl = opp.get("tvl_usd", 0)
        
        if self.min_apy is not None and apy < self.min_apy:
            return False
        
        if self.max_apy is not None and apy > self.max_apy:
            return False
        
        if self.min_tvl is not None and tvl < self.min_tvl:
            return False
        
        return True
    
    def filter_opportunities(self, opportunities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter opportunities based on stored preferences.
        
        Args:
            opportunities: List of opportunity dicts from find_opportunities()
        
        Returns:
            Filtered list matching all preferences
        """
        if not self.is_valid():
            raise ValueError("Required fields (chain, capital_token) must be set before filtering")
        
        filtered = []
        
        for opp in opportunities:
            # Check all preferences
            if not self._matches_reward_preference(opp):
                continue
            
            if not self._matches_il_preference(opp):
                continue
            
            if not self._matches_underlying_preference(opp):
                continue
            
            if not self._matches_constraints(opp):
                continue
            
            filtered.append(opp)
        
        return filtered
    
    def explain_filtering(self, original_count: int, filtered_count: int) -> str:
        """Generate a human-readable explanation of filtering results."""
        lines = [
            f"# 投资偏好过滤结果",
            f"",
            f"**原始产品数**: {original_count}",
            f"**符合条件**: {filtered_count}",
            f"**过滤比例**: {(1 - filtered_count/original_count)*100:.1f}%",
            f"",
            f"## 您的偏好设置",
            f"",
        ]
        
        # Required
        lines.append(f"- **目标链**: {self.chain}")
        lines.append(f"- **投资代币**: {self.capital_token}")
        
        # Preferences
        if self.reward_preference:
            reward_labels = {"single": "单一代币奖励", "multi": "多代币奖励", "none": "无奖励"}
            lines.append(f"- **奖励偏好**: {reward_labels.get(self.reward_preference, self.reward_preference)}")
        
        if self.accept_il is not None:
            lines.append(f"- **接受无常损失**: {'是' if self.accept_il else '否'}")
        
        if self.underlying_preference:
            underlying_labels = {"onchain": "纯链上", "rwa": "现实世界资产", "mixed": "混合"}
            lines.append(f"- **底层资产**: {underlying_labels.get(self.underlying_preference, self.underlying_preference)}")
        
        # Constraints
        if self.min_apy:
            lines.append(f"- **最低 APY**: {self.min_apy}%")
        if self.max_apy:
            lines.append(f"- **最高 APY**: {self.max_apy}%")
        if self.min_tvl:
            lines.append(f"- **最低 TVL**: ${self.min_tvl:,.0f}")
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict[str, Any]:
        """Export preferences as dict."""
        return {
            "chain": self.chain,
            "capital_token": self.capital_token,
            "reward_preference": self.reward_preference,
            "accept_il": self.accept_il,
            "underlying_preference": self.underlying_preference,
            "min_apy": self.min_apy,
            "max_apy": self.max_apy,
            "min_tvl": self.min_tvl
        }
    
    def from_dict(self, data: Dict[str, Any]) -> "InvestmentProfile":
        """Load preferences from dict."""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
        return self
    
    def __repr__(self) -> str:
        return f"InvestmentProfile(chain={self.chain}, token={self.capital_token})"


# Convenience function for quick filtering
def filter_by_preferences(
    opportunities: List[Dict[str, Any]],
    chain: str,
    capital_token: str,
    **kwargs
) -> List[Dict[str, Any]]:
    """
    One-shot filter function.
    
    Example:
        filtered = filter_by_preferences(
            opportunities,
            chain="ethereum",
            capital_token="USDC",
            accept_il=False,
            reward_preference="single"
        )
    """
    profile = InvestmentProfile()
    profile.set_preferences(chain=chain, capital_token=capital_token, **kwargs)
    return profile.filter_opportunities(opportunities)


if __name__ == "__main__":
    # Demo: Print available questions
    print("# 投资偏好收集问题列表\n")
    questions = InvestmentProfile.get_questions()
    
    print("## 必问问题")
    for q in questions["required"]:
        print(f"\n**{q['question']}**")
        print(f"- Key: `{q['key']}`")
        if 'options' in q:
            print(f"- 选项: {', '.join(q['options'])}")
    
    print("\n## 重要问题（强烈建议询问）")
    for q in questions["preference"]:
        print(f"\n**{q['question']}**")
        print(f"- Key: `{q['key']}`")
        print(f"- 说明: {q['description']}")
        for opt in q['options']:
            if isinstance(opt, dict):
                print(f"  - `{opt['value']}`: {opt['label']} ({opt.get('description', '')})")