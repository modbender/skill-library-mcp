"""
知乎助手 - 主程序入口

功能：
- 抓取知乎热榜并生成回答草稿
- 管理待审核队列
- 推送到飞书
- 记录操作日志

使用方法：
    # 抓取热榜
    python main.py fetch --limit 10
    
    # 推送到飞书
    python main.py notify
    
    # 查看统计
    python main.py stats
    
    # 查看日志
    python main.py logs
    
    # 拒绝草稿
    python main.py reject --id P20260228...
"""
import os
import sys
import yaml
import json
import logging
import argparse
import subprocess
from pathlib import Path
from datetime import datetime

# 添加模块路径
sys.path.insert(0, str(Path(__file__).parent / "modules"))

from zhihu_hot import ZhihuHotFetcher
from memory_store import MemoryStore
from content_gen import ContentGenerator
from feishu_notify import FeishuNotifier

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('./logs/app.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


def get_openclaw_config(key: str, default=None):
    """从 OpenClaw 配置读取"""
    try:
        result = subprocess.run(
            ['openclaw', 'config', 'get', f'skills.zhihu-assistant.{key}'],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            value = result.stdout.strip()
            # 处理 JSON 输出
            if value.startswith('"') and value.endswith('"'):
                return json.loads(value)
            return value
    except Exception as e:
        logger.debug(f"读取 OpenClaw 配置失败: {e}")
    return default


class ZhihuAssistant:
    """
    知乎助手主类
    
    整合所有功能模块，提供统一的接口。
    
    Attributes:
        config: 配置字典
        memory: 记忆存储管理器
        zhihu: 知乎热榜抓取器
        generator: 内容生成器
        notifier: 飞书通知器
    """
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        初始化助手
        
        Args:
            config_path: 配置文件路径，默认 config.yaml
        """
        self.config = self._load_config(config_path)
        self.memory = MemoryStore(
            data_dir=self.config['storage']['data_dir'],
            log_dir=self.config['storage']['log_dir']
        )
        self.zhihu = None
        self.generator = None
        self.notifier = None
        
        self._init_components()
    
    def _load_config(self, config_path: str) -> dict:
        """
        加载配置文件，优先从 OpenClaw config 读取敏感信息
        
        Args:
            config_path: 配置文件路径
            
        Returns:
            配置字典
        """
        # 默认配置
        config = {
            'zhihu': {
                'cookie': '',
                'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                'hot_url': 'https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total',
                'question_prefix': 'https://www.zhihu.com/question/'
            },
            'kimi': {
                'api_key': '',
                'model': 'kimi-coding/k2p5',
                'base_url': 'https://api.moonshot.cn/v1'
            },
            'feishu': {
                'use_openclaw': True,
                'webhook_url': '',
                'target_user': ''
            },
            'storage': {
                'data_dir': './data',
                'log_dir': './logs',
                'answered_file': './data/answered.json',
                'pending_file': './data/pending.json',
                'log_file': './logs/operation.log'
            },
            'filter': {
                'skip_keywords': ['广告', '推广', '招聘'],
                'min_heat': 10
            }
        }
        
        # 尝试从本地配置文件加载（非敏感配置）
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    local_config = yaml.safe_load(f)
                    if local_config:
                        # 合并配置
                        for section in local_config:
                            if section in config:
                                config[section].update(local_config[section])
        except Exception as e:
            logger.warning(f"加载本地配置失败: {e}")
        
        # 从 OpenClaw config 读取敏感信息（优先级更高）
        # 知乎 Cookie
        zhihu_cookie = get_openclaw_config('zhihu_cookie')
        if zhihu_cookie:
            config['zhihu']['cookie'] = zhihu_cookie
            logger.info("已从 OpenClaw config 加载知乎 Cookie")
        
        # API Key（支持多种命名）
        api_key = get_openclaw_config('kimi_api_key') or get_openclaw_config('doubao_api_key')
        if api_key:
            config['kimi']['api_key'] = api_key
            logger.info("已从 OpenClaw config 加载 API Key")
        
        # 飞书用户 ID
        feishu_user = get_openclaw_config('feishu_user_id')
        if feishu_user:
            config['feishu']['target_user'] = feishu_user
            logger.info("已从 OpenClaw config 加载飞书用户 ID")
        
        # 其他配置
        fetch_limit = get_openclaw_config('fetch_limit')
        if fetch_limit:
            try:
                config['filter']['fetch_limit'] = int(fetch_limit)
            except:
                pass
        
        min_heat = get_openclaw_config('min_heat')
        if min_heat:
            try:
                config['filter']['min_heat'] = float(min_heat)
            except:
                pass
        
        # 如果仍然没有敏感配置，尝试从环境变量读取
        if not config['kimi']['api_key']:
            config['kimi']['api_key'] = os.environ.get('KIMI_API_KEY', '')
        
        return config
    
    def _init_components(self):
        """初始化各功能组件"""
        # 知乎抓取器
        cookie = self.config['zhihu'].get('cookie', '')
        self.zhihu = ZhihuHotFetcher(
            cookie=cookie,
            user_agent=self.config['zhihu'].get('user_agent'),
            test_mode=(not cookie or cookie == 'your_zhihu_cookie_here')
        )
        
        # 内容生成器
        self.generator = ContentGenerator(
            api_key=self.config['kimi']['api_key'],
            model=self.config['kimi']['model'],
            base_url=self.config['kimi']['base_url']
        )
        
        # 飞书通知器
        self.notifier = FeishuNotifier(
            use_openclaw=self.config['feishu'].get('use_openclaw', True),
            webhook_url=self.config['feishu'].get('webhook_url'),
            target_user=self.config['feishu'].get('target_user')
        )
    
    def fetch_and_generate(self, limit: int = 10):
        """
        抓取热榜并生成回答草稿
        
        Args:
            limit: 抓取前 N 条热榜
            
        Returns:
            新增待审核项数量
        """
        logger.info("开始抓取知乎热榜...")
        
        # 检查是否测试模式
        cookie = self.config['zhihu'].get('cookie', '')
        is_test_mode = not cookie or cookie == 'your_zhihu_cookie_here'
        
        # 1. 抓取热榜
        hot_list = self.zhihu.fetch_hot_list(limit=limit)
        
        if not hot_list:
            logger.warning("未获取到热榜数据")
            return 0
        
        logger.info(f"获取到 {len(hot_list)} 条热榜问题")
        
        # 2. 过滤和生成
        new_count = 0
        for question in hot_list:
            question_id = question['id']
            
            # 检查是否已回答
            if self.memory.is_answered(question_id):
                logger.info(f"跳过已回答问题: {question['title']}")
                continue
            
            # 检查热度
            min_heat = self.config.get('filter', {}).get('min_heat', 0)
            if question.get('heat', 0) < min_heat:
                logger.info(f"跳过低热度问题: {question['title']}")
                continue
            
            # 检查关键词过滤
            skip_keywords = self.config.get('filter', {}).get('skip_keywords', [])
            if any(kw in question['title'] for kw in skip_keywords):
                logger.info(f"跳过含关键词问题: {question['title']}")
                continue
            
            logger.info(f"正在生成回答: {question['title']}")
            
            # 3. 生成回答草稿
            draft = self.generator.generate_answer(
                question_title=question['title'],
                question_detail=question.get('excerpt', ''),
                excerpt=question.get('excerpt', '')
            )
            
            if not draft:
                logger.error(f"生成回答失败: {question['title']}")
                continue
            
            # 4. 质量评估
            quality = self.generator.estimate_quality(draft)
            logger.info(f"质量评分: {quality['score']}/100")
            
            # 质量阈值
            min_score = 30 if is_test_mode else 60
            if quality['score'] < min_score:
                logger.warning(f"质量不达标，跳过: {question['title']}")
                continue
            
            # 5. 添加到待审核队列
            pending_id = self.memory.add_pending(question, draft)
            new_count += 1
            
            logger.info(f"已添加到待审核队列: {pending_id}")
        
        logger.info(f"本次新增 {new_count} 条待审核项")
        return new_count
    
    def notify_pending(self):
        """
        获取待推送的待审核项列表
        
        Returns:
            待推送项列表
        """
        pending_items = self.memory.get_pending('pending')
        
        if not pending_items:
            logger.info("没有待审核项")
            return []
        
        logger.info(f"找到 {len(pending_items)} 条待审核项")
        
        # 返回未推送的项
        notified_items = []
        for item in pending_items:
            if not item.get('feishu_message_id'):
                notified_items.append(item)
                logger.info(f"待推送: {item['title']} (ID: {item['id']})")
        
        return notified_items
    
    def get_stats(self):
        """
        获取统计信息
        
        Returns:
            统计字典
        """
        return self.memory.get_stats()
    
    def reject(self, pending_id: str):
        """
        拒绝待审核项
        
        Args:
            pending_id: 待审核项ID
            
        Returns:
            True 如果成功，False 否则
        """
        if self.memory.update_pending_status(pending_id, 'rejected'):
            logger.info(f"已拒绝: {pending_id}")
            return True
        return False


def main():
    """主函数 - 解析命令行参数并执行"""
    parser = argparse.ArgumentParser(
        description='知乎助手 - 热榜抓取与内容管理',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 抓取热榜并生成草稿
  python main.py fetch --limit 10
  
  # 推送到飞书
  python main.py notify
  
  # 查看统计
  python main.py stats
  
  # 查看日志
  python main.py logs
  
  # 拒绝草稿
  python main.py reject --id P20260228...
        """
    )
    
    parser.add_argument('action', choices=[
        'fetch',      # 抓取热榜并生成草稿
        'notify',     # 获取待推送列表
        'stats',      # 查看统计
        'reject',     # 拒绝草稿
        'logs'        # 查看操作日志
    ], help='执行的操作')
    
    parser.add_argument('--id', help='待审核项ID（用于 reject）')
    parser.add_argument('--limit', type=int, default=10, help='抓取数量（默认10）')
    
    args = parser.parse_args()
    
    assistant = ZhihuAssistant()
    
    if args.action == 'fetch':
        count = assistant.fetch_and_generate(limit=args.limit)
        print(f"新增 {count} 条待审核项")
    
    elif args.action == 'notify':
        items = assistant.notify_pending()
        if items:
            print(f"找到 {len(items)} 条待推送项:")
            for item in items:
                print(f"  - {item['title'][:40]}... (ID: {item['id']})")
        else:
            print("没有待推送项")
    
    elif args.action == 'stats':
        stats = assistant.get_stats()
        print("\n=== 统计信息 ===")
        print(f"已回答问题: {stats['answered_count']}")
        print(f"待审核: {stats['pending_count']}")
        print(f"已批准: {stats['approved_count']}")
        print(f"已发布: {stats['published_count']}")
        print(f"已拒绝: {stats['rejected_count']}")
    
    elif args.action == 'reject':
        if not args.id:
            print("错误: 请指定 --id 参数")
            sys.exit(1)
        if assistant.reject(args.id):
            print(f"已拒绝: {args.id}")
        else:
            print(f"拒绝失败: {args.id}")
            sys.exit(1)
    
    elif args.action == 'logs':
        logs = assistant.memory.get_logs(limit=20)
        print("\n=== 最近操作日志 ===")
        for log in logs:
            print(f"[{log['timestamp']}] {log['action']}: {log['detail']}")


if __name__ == '__main__':
    main()
