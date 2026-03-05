#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
赚钱灵感分析器
分析项目的变现潜力，生成赚钱灵感
"""

import re
from typing import Dict, List, Optional, Tuple

from config import POTENTIAL_RULES, IDEA_TEMPLATES


class IdeaAnalyzer:
    """赚钱灵感分析器"""
    
    def __init__(self):
        self.templates = IDEA_TEMPLATES
    
    def analyze_potential(self, project: Dict) -> Tuple[str, float]:
        """
        分析项目的变现潜力
        
        Args:
            project: 项目信息
            
        Returns:
            (潜力等级, 潜力分数 0-100)
        """
        score = 0
        
        # 1. 星标数评分（最多 30 分）
        stars = project.get('stars', 0)
        if stars > 1000:
            score += 30
        elif stars > 500:
            score += 25
        elif stars > 100:
            score += 20
        elif stars > 50:
            score += 15
        else:
            score += 10
        
        # 2. 新增星标速度评分（最多 25 分）
        trending_stars = project.get('trending_stars', 0)
        if trending_stars > 100:
            score += 25
        elif trending_stars > 50:
            score += 20
        elif trending_stars > 20:
            score += 15
        elif trending_stars > 10:
            score += 10
        else:
            score += 5
        
        # 3. 技术栈评分（最多 20 分）
        language = project.get('language', '').lower()
        description = project.get('description', '').lower()
        
        # AI/LLM 相关加分
        ai_keywords = ['ai', 'llm', 'gpt', 'chatgpt', 'claude', 'agent', 'openai', 'anthropic']
        if any(k in description for k in ai_keywords):
            score += 15
        
        # 热门语言加分
        hot_languages = ['python', 'typescript', 'rust', 'go']
        if language in hot_languages:
            score += 5
        
        # 4. 变现关键词评分（最多 15 分）
        monetization_keywords = [
            'api', 'sdk', 'cli', 'framework', 'platform', 'tool',
            'automation', 'chatbot', 'assistant', 'dashboard'
        ]
        if any(k in description for k in monetization_keywords):
            score += 15
        elif any(k in description for k in ['library', 'package']):
            score += 10
        
        # 5. 商业模式评分（最多 10 分）
        if 'saas' in description or 'enterprise' in description:
            score += 10
        elif 'api' in description or 'service' in description:
            score += 7
        elif 'tool' in description or 'app' in description:
            score += 5
        
        # 确定潜力等级
        if score >= 70:
            potential = '高'
        elif score >= 50:
            potential = '中'
        else:
            potential = '低'
        
        return potential, score
    
    def generate_ideas(self, project: Dict, user_preferences: Dict = None) -> List[Dict]:
        """
        为项目生成赚钱灵感
        
        Args:
            project: 项目信息
            user_preferences: 用户偏好
            
        Returns:
            赚钱灵感列表
        """
        ideas = []
        project_name = project.get('name', '').split('/')[-1]
        description = project.get('description', '')
        
        # 分析适合的变现方式
        suitable_types = self._analyze_suitable_types(project)
        
        for idea_type in suitable_types:
            template = self.templates.get(idea_type)
            if not template:
                continue
            
            # 根据用户偏好调整
            cost, income, time = self._adjust_for_user(template, user_preferences)
            
            idea = {
                'type': idea_type,
                'name': template['name'].format(project_name=project_name),
                'description': template['description'].format(project_name=project_name),
                'target_users': template['target_users'],
                'cost': cost,
                'expected_income': income,
                'time_needed': time,
                'project': project_name,
                'project_url': project.get('url', ''),
            }
            
            ideas.append(idea)
        
        return ideas
    
    def _analyze_suitable_types(self, project: Dict) -> List[str]:
        """分析项目适合的变现方式"""
        description = project.get('description', '').lower()
        language = project.get('language', '').lower()
        stars = project.get('stars', 0)
        
        suitable = []
        
        # 1. 部署服务 - 大多数项目都适合
        if stars > 50:
            suitable.append('deployment_service')
        
        # 2. 技术咨询 - 复杂项目适合
        if any(k in description for k in ['framework', 'platform', 'architecture']):
            suitable.append('consulting')
        
        # 3. 培训课程 - 有学习门槛的项目适合
        if any(k in description for k in ['tutorial', 'guide', 'learn']) or stars > 100:
            suitable.append('training')
        
        # 4. 定制开发 - 企业级项目适合
        if any(k in description for k in ['enterprise', 'business', 'saas', 'api']):
            suitable.append('customization')
        
        # 默认至少返回部署服务和培训
        if not suitable:
            suitable = ['deployment_service', 'training']
        
        return suitable
    
    def _adjust_for_user(self, template: Dict, preferences: Dict = None) -> Tuple[int, int, int]:
        """根据用户偏好调整成本/收入/时间"""
        if not preferences:
            return (
                template['cost_range'][0],
                template['income_range'][0],
                template['time_range'][0]
            )
        
        # 根据预算调整成本
        budget = preferences.get('budget', 1000)
        cost = min(template['cost_range'][1], max(template['cost_range'][0], budget // 2))
        
        # 根据可用时间调整
        time_available = preferences.get('time_available', 2)
        time_needed = min(template['time_range'][1], max(template['time_range'][0], time_available))
        
        # 根据技能调整收入预期
        skills = preferences.get('skills', [])
        income = template['income_range'][0]
        if any(s.lower() in ['python', 'ai', 'web', 'javascript'] for s in skills):
            income = (template['income_range'][0] + template['income_range'][1]) // 2
        
        return cost, income, time_needed
    
    def rank_ideas(self, ideas: List[Dict], user_preferences: Dict = None) -> List[Dict]:
        """对灵感进行排序"""
        def get_score(idea):
            # 收入越高越好
            income_score = idea['expected_income'] / 1000
            
            # 时间越短越好
            time_score = 10 / max(idea['time_needed'], 1)
            
            # 成本越低越好
            cost_score = 10 / max(idea['cost'] / 100, 1)
            
            return income_score + time_score + cost_score
        
        return sorted(ideas, key=get_score, reverse=True)


# 测试
if __name__ == '__main__':
    analyzer = IdeaAnalyzer()
    
    # 测试项目
    test_project = {
        'name': 'openai/chatgpt',
        'stars': 50000,
        'trending_stars': 150,
        'description': 'Official Python library for the ChatGPT API',
        'language': 'Python',
    }
    
    potential, score = analyzer.analyze_potential(test_project)
    print(f"潜力: {potential} (分数: {score})")
    
    ideas = analyzer.generate_ideas(test_project)
    for idea in ideas:
        print(f"\n灵感: {idea['name']}")
        print(f"  目标用户: {idea['target_users']}")
        print(f"  成本: ¥{idea['cost']}")
        print(f"  预期收入: ¥{idea['expected_income']}/月")
        print(f"  所需时间: {idea['time_needed']} 天")