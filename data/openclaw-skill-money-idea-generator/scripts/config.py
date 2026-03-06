#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
赚钱灵感生成器 - 配置文件
"""

import os

# GitHub API Token（可选，提高速率限制）
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', '')

# 监控的项目最小星标数
MIN_STARS = 50

# 最小新增星标/周
MIN_WEEKLY_STARS = 20

# 关注的领域（GitHub 搜索关键词）
CATEGORIES = [
    'AI LLM Agent',
    'AI automation',
    'chatbot GPT',
    'AI agent framework',
    'LLM tools',
]

# 排除的项目（太成熟或无法变现）
EXCLUDE_KEYWORDS = [
    'awesome-',  # 资源列表
    'tutorial',  # 教程
    'course',    # 课程
    'book',      # 书籍
]

# 变现潜力评分规则
POTENTIAL_RULES = {
    'high': {
        'min_stars': 100,
        'min_weekly_growth': 50,
        'keywords': ['api', 'sdk', 'framework', 'platform'],
    },
    'medium': {
        'min_stars': 50,
        'min_weekly_growth': 20,
        'keywords': ['tool', 'cli', 'bot'],
    },
    'low': {
        'min_stars': 10,
        'min_weekly_growth': 5,
        'keywords': [],
    }
}

# 赚钱灵感模板
IDEA_TEMPLATES = {
    'deployment_service': {
        'name': '{project_name} 部署服务',
        'description': '帮助用户部署 {project_name}，提供技术支持',
        'target_users': ['技术小白', '企业用户', '创业者'],
        'cost_range': (100, 500),
        'income_range': (2000, 10000),
        'time_range': (1, 3),  # 天
    },
    'consulting': {
        'name': '{project_name} 技术咨询',
        'description': '提供 {project_name} 技术咨询和方案设计',
        'target_users': ['企业', '创业者', '产品经理'],
        'cost_range': (0, 100),
        'income_range': (5000, 20000),
        'time_range': (0.5, 2),
    },
    'training': {
        'name': '{project_name} 培训课程',
        'description': '制作 {project_name} 使用教程和培训课程',
        'target_users': ['学习者', '开发者', '企业员工'],
        'cost_range': (0, 200),
        'income_range': (1000, 50000),
        'time_range': (3, 7),
    },
    'customization': {
        'name': '{project_name} 定制开发',
        'description': '为用户定制开发基于 {project_name} 的功能',
        'target_users': ['企业', '创业者', '产品团队'],
        'cost_range': (500, 2000),
        'income_range': (5000, 50000),
        'time_range': (7, 30),
    },
}

# 用户偏好（从记忆系统读取）
USER_PREFERENCES = {
    'budget': 1000,  # 预算
    'time_available': 2,  # 可用时间（天/周）
    'skills': ['Python', 'AI', 'Web'],  # 技能
    'interests': ['AI工具', '自动化', 'SaaS'],  # 兴趣
}