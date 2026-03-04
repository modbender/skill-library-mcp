"""
国际化 (i18n) 模块
支持多语言切换
"""

import os
from typing import Dict, Optional

class I18n:
    """国际化支持"""
    
    # 支持的语言
    SUPPORTED_LANGUAGES = ['en', 'zh']
    
    # 默认语言
    DEFAULT_LANGUAGE = 'en'
    
    # 翻译字典
    TRANSLATIONS: Dict[str, Dict[str, str]] = {
        'en': {
            # 欢迎信息
            'welcome': 'Welcome to Router Skill',
            'welcome_desc': 'This wizard will help you detect environment and configure optimal routing strategy.',
            
            # 环境检测
            'detecting_env': '🔍 Detecting environment...',
            'ollama_installed': '✅ Ollama installed, found {count} models',
            'ollama_not_installed': '❌ Ollama not installed',
            'dashscope_configured': '✅ Alibaba Cloud configured (Key: {key})',
            'dashscope_not_configured': '❌ Alibaba Cloud not configured',
            'openai_configured': '✅ OpenAI configured (Key: {key})',
            'openai_not_configured': '❌ OpenAI not configured',
            'system_resources': '💻 System Resources:',
            'memory': 'Memory: {gb} GB',
            'cpu': 'CPU: {cores} cores',
            
            # 推荐配置
            'recommended_config': '📋 Recommended Config',
            'primary_model': 'Primary',
            'verifier_model': 'Verifier',
            'expert_model': 'Expert',
            'threshold_mode': 'Threshold Mode',
            'budget_suggestion': 'Budget Suggestion',
            'estimated_cost': 'Estimated Monthly Cost',
            
            # 选择
            'choose': 'Please Choose',
            'use_recommended': 'Use Recommended Config (Recommended)',
            'custom_config': 'Custom Configuration',
            'view_details': 'View Details',
            'setup_later': 'Setup Later',
            'enter_choice': 'Enter choice [1-4]',
            
            # 成功
            'config_saved': '✅ Configuration saved to: {path}',
            'config_complete': '✅ Configuration complete! Router Skill is ready.',
            'next_steps': 'Next Steps:',
            'enable_cmd': '  Enable: openclaw router enable',
            'status_cmd': '  Status: openclaw router status',
            
            # 错误
            'error': '❌ Error: {message}',
            'cancelled': '⚠️  Configuration cancelled',
            
            # 模型
            'local': 'local',
            'cloud': 'cloud',
            'free': 'free',
            'per_1k_tokens': '${price}/1k tokens',
            
            # 模式
            'mode_balanced': 'balanced',
            'mode_quality': 'quality',
            'mode_economy': 'economy',
            'mode_speed': 'speed',
        },
        
        'zh': {
            # 欢迎信息
            'welcome': '欢迎使用 Router Skill',
            'welcome_desc': '本向导将帮助您检测环境并配置最佳路由策略。',
            
            # 环境检测
            'detecting_env': '🔍 环境检测...',
            'ollama_installed': '✅ Ollama 已安装，发现 {count} 个模型',
            'ollama_not_installed': '❌ Ollama 未安装',
            'dashscope_configured': '✅ 阿里云百炼已配置 (Key: {key})',
            'dashscope_not_configured': '❌ 阿里云百炼未配置',
            'openai_configured': '✅ OpenAI 已配置 (Key: {key})',
            'openai_not_configured': '❌ OpenAI 未配置',
            'system_resources': '💻 系统资源:',
            'memory': '内存：{gb} GB',
            'cpu': 'CPU: {cores} 核心',
            
            # 推荐配置
            'recommended_config': '📋 推荐配置',
            'primary_model': '主路由',
            'verifier_model': '验证器',
            'expert_model': '专家',
            'threshold_mode': '阈值模式',
            'budget_suggestion': '预算建议',
            'estimated_cost': '预计月成本',
            
            # 选择
            'choose': '请选择',
            'use_recommended': '使用推荐配置 (推荐)',
            'custom_config': '自定义配置',
            'view_details': '查看详细说明',
            'setup_later': '稍后设置',
            'enter_choice': '输入选项 [1-4]',
            
            # 成功
            'config_saved': '✅ 配置已保存到：{path}',
            'config_complete': '✅ 配置完成！Router Skill 已就绪。',
            'next_steps': '下一步:',
            'enable_cmd': '  启用：openclaw router enable',
            'status_cmd': '  状态：openclaw router status',
            
            # 错误
            'error': '❌ 发生错误：{message}',
            'cancelled': '⚠️  配置已取消',
            
            # 模型
            'local': '本地',
            'cloud': '云端',
            'free': '免费',
            'per_1k_tokens': '¥{price}/1k tokens',
            
            # 模式
            'mode_balanced': '平衡',
            'mode_quality': '质量优先',
            'mode_economy': '成本优先',
            'mode_speed': '速度优先',
        }
    }
    
    def __init__(self, language: Optional[str] = None):
        """
        初始化 i18n
        
        Args:
            language: 语言代码 ('en' or 'zh'), 默认自动检测
        """
        if language:
            self.language = language
        else:
            self.language = self._auto_detect_language()
    
    def _auto_detect_language(self) -> str:
        """自动检测语言"""
        # 从环境变量检测
        lang = os.getenv('LANG', '').lower()
        
        if 'zh' in lang or 'chinese' in lang:
            return 'zh'
        elif 'en' in lang or 'english' in lang:
            return 'en'
        
        # 默认英文
        return self.DEFAULT_LANGUAGE
    
    def get(self, key: str, **kwargs) -> str:
        """
        获取翻译
        
        Args:
            key: 翻译键
            **kwargs: 格式化参数
        
        Returns:
            翻译后的字符串
        """
        # 获取当前语言的翻译
        translations = self.TRANSLATIONS.get(self.language, self.TRANSLATIONS[self.DEFAULT_LANGUAGE])
        
        # 获取翻译文本
        text = translations.get(key, key)
        
        # 格式化
        if kwargs:
            try:
                text = text.format(**kwargs)
            except KeyError:
                pass
        
        return text
    
    def set_language(self, language: str):
        """设置语言"""
        if language in self.SUPPORTED_LANGUAGES:
            self.language = language
        else:
            raise ValueError(f"Unsupported language: {language}. Supported: {self.SUPPORTED_LANGUAGES}")
    
    def get_language_name(self) -> str:
        """获取语言名称"""
        names = {
            'en': 'English',
            'zh': '中文'
        }
        return names.get(self.language, self.language)


# 全局 i18n 实例
_i18n: Optional[I18n] = None

def get_i18n() -> I18n:
    """获取全局 i18n 实例"""
    global _i18n
    if _i18n is None:
        _i18n = I18n()
    return _i18n

def _(key: str, **kwargs) -> str:
    """快捷翻译函数"""
    return get_i18n().get(key, **kwargs)
