# 社区论坛和用户支持
## 技能社区建设、用户支持和反馈管理

## 🎯 社区建设策略

### 1. 社区平台选择
```
多平台社区架构:
• 官方论坛: 深度讨论和技术支持
• Discord频道: 实时交流和协作
• GitHub Discussions: 开发讨论和问题跟踪
• 社交媒体: 宣传和用户互动
• 邮件列表: 正式通知和公告
```

### 2. 社区管理团队
```
社区角色分工:
• 管理员: 整体管理和策略制定
• 版主: 内容管理和用户支持
• 技术专家: 技术问题解答
• 内容创作者: 教程和文档编写
• 社区大使: 用户引导和活动组织
```

## 💬 论坛管理

### 1. 论坛结构设计
```
论坛版块划分:
📚 文档和教程
├── 使用指南
├── 教程分享
├── 最佳实践
└── 视频教程

🛠️ 技术讨论
├── 安装和配置
├── 功能使用
├── 问题排查
└── 性能优化

💡 功能建议
├── 新功能提议
├── 改进建议
└── 投票功能

🔧 开发讨论
├── 源码分析
├── 贡献指南
└── 开发协作

🎉 社区活动
├── 用户分享
├── 竞赛活动
└── 线下聚会
```

### 2. 论坛管理工具
#### 使用Discord.py管理Discord社区：
```python
# discord_bot.py
import discord
from discord.ext import commands
import json
from datetime import datetime
from typing import Dict, List

class CommunityBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.messages = True
        intents.message_content = True
        intents.members = True
        
        super().__init__(command_prefix='!', intents=intents)
        self.support_tickets = {}
        self.faq_data = self._load_faq()
    
    def _load_faq(self) -> Dict:
        """加载FAQ数据"""
        try:
            with open('faq.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    async def on_ready(self):
        print(f'{self.user} 已上线！')
        await self._setup_channels()
    
    async def _setup_channels(self):
        """设置频道"""
        # 这里可以自动创建和管理频道
        pass
    
    @commands.command(name='faq')
    async def show_faq(self, ctx, topic: str = None):
        """显示FAQ"""
        if topic:
            if topic in self.faq_data:
                await ctx.send(f"**{topic}**:\n{self.faq_data[topic]}")
            else:
                await ctx.send(f"未找到关于 '{topic}' 的FAQ")
        else:
            topics = list(self.faq_data.keys())
            await ctx.send(f"可用FAQ主题: {', '.join(topics)}")
    
    @commands.command(name='support')
    async def create_support_ticket(self, ctx, *, issue: str):
        """创建支持工单"""
        ticket_id = f"TICKET-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.support_tickets[ticket_id] = {
            'user': ctx.author.id,
            'issue': issue,
            'created_at': datetime.now().isoformat(),
            'status': 'open'
        }
        
        # 发送到支持频道
        support_channel = discord.utils.get(ctx.guild.channels, name='support-tickets')
        if support_channel:
            await support_channel.send(
                f"🎫 新工单创建: {ticket_id}\n"
                f"用户: {ctx.author.mention}\n"
                f"问题: {issue}"
            )
        
        await ctx.send(f"✅ 工单已创建: {ticket_id}")
    
    @commands.command(name='solved')
    @commands.has_role('Moderator')
    async def mark_ticket_solved(self, ctx, ticket_id: str):
        """标记工单为已解决"""
        if ticket_id in self.support_tickets:
            self.support_tickets[ticket_id]['status'] = 'solved'
            self.support_tickets[ticket_id]['solved_by'] = ctx.author.id
            self.support_tickets[ticket_id]['solved_at'] = datetime.now().isoformat()
            
            await ctx.send(f"✅ 工单 {ticket_id} 已标记为已解决")
        else:
            await ctx.send(f"❌ 未找到工单: {ticket_id}")

# 运行机器人
bot = CommunityBot()
bot.run('YOUR_BOT_TOKEN')
```

## 📊 用户支持系统

### 1. 支持工单管理
#### 工单管理系统：
```python
# support_ticket_system.py
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum

class TicketStatus(Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    WAITING = "waiting_for_user"
    SOLVED = "solved"
    CLOSED = "closed"

class SupportTicketSystem:
    def __init__(self, db_path: str = "support_tickets.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tickets (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                user_email TEXT,
                subject TEXT NOT NULL,
                description TEXT NOT NULL,
                status TEXT NOT NULL,
                priority INTEGER DEFAULT 3,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                assigned_to TEXT,
                category TEXT,
                tags TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ticket_replies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                content TEXT NOT NULL,
                is_internal BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (ticket_id) REFERENCES tickets (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_ticket(self, user_id: str, subject: str, description: str, 
                     user_email: Optional[str] = None, priority: int = 3) -> str:
        """创建新工单"""
        ticket_id = f"T{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO tickets 
            (id, user_id, user_email, subject, description, status, priority)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (ticket_id, user_id, user_email, subject, description, 
              TicketStatus.OPEN.value, priority))
        
        conn.commit()
        conn.close()
        
        return ticket_id
    
    def get_ticket(self, ticket_id: str) -> Optional[Dict]:
        """获取工单详情"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM tickets WHERE id = ?', (ticket_id,))
        ticket = cursor.fetchone()
        
        if ticket:
            cursor.execute(
                'SELECT * FROM ticket_replies WHERE ticket_id = ? ORDER BY created_at',
                (ticket_id,)
            )
            replies = cursor.fetchall()
            
            result = dict(ticket)
            result['replies'] = [dict(reply) for reply in replies]
            return result
        
        return None
    
    def add_reply(self, ticket_id: str, user_id: str, content: str, 
                 is_internal: bool = False):
        """添加工单回复"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO ticket_replies (ticket_id, user_id, content, is_internal)
            VALUES (?, ?, ?, ?)
        ''', (ticket_id, user_id, content, is_internal))
        
        # 更新工单状态和时间戳
        cursor.execute('''
            UPDATE tickets 
            SET updated_at = CURRENT_TIMESTAMP,
                status = CASE 
                    WHEN ? = 1 THEN status
                    ELSE 'waiting_for_user'
                END
            WHERE id = ?
        ''', (is_internal, ticket_id))
        
        conn.commit()
        conn.close()
    
    def update_ticket_status(self, ticket_id: str, status: TicketStatus, 
                           assigned_to: Optional[str] = None):
        """更新工单状态"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        update_fields = ['status = ?', 'updated_at = CURRENT_TIMESTAMP']
        params = [status.value]
        
        if assigned_to:
            update_fields.append('assigned_to = ?')
            params.append(assigned_to)
        
        params.append(ticket_id)
        
        query = f'''
            UPDATE tickets 
            SET {', '.join(update_fields)}
            WHERE id = ?
        '''
        
        cursor.execute(query, params)
        conn.commit()
        conn.close()
    
    def search_tickets(self, query: str = None, status: str = None, 
                      user_id: str = None, limit: int = 50) -> List[Dict]:
        """搜索工单"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        conditions = []
        params = []
        
        if query:
            conditions.append('(subject LIKE ? OR description LIKE ?)')
            params.extend([f'%{query}%', f'%{query}%'])
        
        if status:
            conditions.append('status = ?')
            params.append(status)
        
        if user_id:
            conditions.append('user_id = ?')
            params.append(user_id)
        
        where_clause = ' AND '.join(conditions) if conditions else '1=1'
        params.append(limit)
        
        cursor.execute(f'''
            SELECT * FROM tickets 
            WHERE {where_clause}
            ORDER BY created_at DESC
            LIMIT ?
        ''', params)
        
        tickets = cursor.fetchall()
        return [dict(ticket) for ticket in tickets]
```

### 2. 知识库管理
#### FAQ和知识库系统：
```python
# knowledge_base_system.py
import json
from datetime import datetime
from typing import Dict, List, Optional
import sqlite3

class KnowledgeBaseSystem:
    def __init__(self, db_path: str = "knowledge_base.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                category TEXT,
                tags TEXT,
                views INTEGER DEFAULT 0,
                helpful_count INTEGER DEFAULT 0,
                not_helpful_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                author TEXT,
                status TEXT DEFAULT 'published'
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS faq (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                category TEXT,
                frequency INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_article(self, title: str, content: str, category: str = None, 
                   tags: List[str] = None, author: str = None) -> int:
        """添加知识库文章"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        tags_json = json.dumps(tags) if tags else '[]'
        
        cursor.execute('''
            INSERT INTO articles (title, content, category, tags, author)
            VALUES (?, ?, ?, ?, ?)
        ''', (title, content, category, tags_json, author))
        
        article_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return article_id
    
    def search_articles(self, query: str = None, category: str = None, 
                       tag: str = None, limit: int = 20) -> List[Dict]:
        """搜索文章"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        conditions = []
        params = []
        
        if query:
            conditions.append('(title LIKE ? OR content LIKE ?)')
            params.extend([f'%{query}%', f'%{query}%'])
        
        if category:
            conditions.append('category = ?')
            params.append(category)
        
        if tag:
            conditions.append('tags LIKE ?')
            params.append(f'%"{tag}"%')
        
        where_clause = ' AND '.join(conditions) if conditions else '1=1'
        params.append(limit)
        
        cursor.execute(f'''
            SELECT * FROM articles 
            WHERE status = 'published' AND {where_clause}
            ORDER BY views DESC, helpful_count DESC
            LIMIT ?
        ''', params)
        
        articles = cursor.fetchall()
        return [dict(article) for article in articles]
    
    def track_faq_frequency(self, question: str):
        """跟踪FAQ频率"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 查找相似问题
        cursor.execute(
            'SELECT id FROM faq WHERE question LIKE ?',
            (f'%{question}%',)
        )
        existing = cursor.fetchone()
        
        if existing:
            # 更新频率
            cursor.execute(
                'UPDATE faq SET frequency = frequency + 1 WHERE id = ?',
                (existing[0],)
            )
        else:
            # 记录新问题
            cursor.execute(
                'INSERT INTO faq (question, frequency) VALUES (?, 1)',
                (question,)
            )
        
        conn.commit()
        conn.close()
    
    def get_popular_faq(self, limit: int = 10) -> List[Dict]:
        """获取热门FAQ"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM faq 
            WHERE answer IS NOT NULL AND answer != ''
            ORDER BY frequency DESC
            LIMIT ?
        ''', (limit,))
        
        faqs = cursor.fetchall()
        return [dict(faq) for faq in faqs]
```

## 📈 社区分析和反馈

### 1. 社区数据分析
#### 社区分析工具：
```python
# community_analytics.py
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List
import matplotlib.pyplot as plt
import pandas as pd

class CommunityAnalytics:
    def __init__(self, db_path: str = "community.db"):
        self.db_path = db_path
    
    def get_user_activity(self, days: int = 30) -> Dict:
        """获取用户活动数据"""
        conn = sqlite3.connect(self.db_path)
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # 查询每日活动
        query = '''
            SELECT DATE(created_at) as date,
                   COUNT(*) as activity_count,
                   COUNT(DISTINCT user_id) as unique_users
            FROM forum_posts
            WHERE created_at >= ? AND created_at <= ?
            GROUP BY DATE(created_at)
            ORDER BY date
        '''
        
        df = pd.read_sql_query(query, conn, 
                              params=(start_date.isoformat(), end_date.isoformat()))
        conn.close()
        
        return {
            'total_activities': df['activity_count'].sum(),
            'total_unique_users': df['unique_users'].sum(),
            'daily_activity': df.to_dict('records'),
            'avg_daily_activity': df['activity_count'].mean(),
            'avg_daily_users': df['unique_users'].mean()
        }
    
    def get_topic_popularity(self, limit: int = 10) -> List[Dict]:
        """获取热门话题"""
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT category,
                   COUNT(*) as post_count,
                   COUNT(DISTINCT user_id) as user_count,
                   AVG(LENGTH(content)) as avg_content_length,
                   SUM(views) as total_views
            FROM forum_posts
            WHERE created_at >= datetime('now', '-30 days')
            GROUP BY category
            ORDER BY post_count DESC
            LIMIT ?
        '''
        
        df = pd.read_sql_query(query, conn, params=(limit,))
        conn.close()
        
        return df.to_dict('records')
    
    def get_user_engagement(self, user_id: str) -> Dict:
        """获取用户参与度"""
        conn = sqlite3.connect(self.db_path)
        
        queries = {
            'total_posts': '''
                SELECT COUNT(*) FROM forum_posts WHERE user_id = ?
            ''',
            'avg_post_length': '''
                SELECT AVG(LENGTH(content)) FROM forum_posts WHERE user_id = ?
            ''',
            'recent_activity': '''
                SELECT COUNT(*) FROM forum_posts 
                WHERE user_id = ? AND created_at >= datetime('now', '-7 days')
            ''',
            'helpful_posts': '''
                SELECT COUNT(*) FROM forum_posts 
                WHERE user_id = ? AND helpful_votes > 5
            '''
        }
        
        result = {}
        cursor = conn.cursor()
        
        for key, query in queries.items():
            cursor.execute(query, (user_id,))
            result[key] = cursor.fetchone()[0]
        
        conn.close()
        return result
    
    def generate_community_report(self) -> Dict:
        """生成社区报告"""
        report = {
            'user_activity': self.get_user_activity(30),
            'popular_topics': self.get_topic_popularity(10),
            'growth_metrics': self._calculate_growth_metrics(),
            'engagement_metrics': self._calculate_engagement_metrics(),
            'recommendations': self._generate_recommendations()
        }
        
        return report
    
    def _calculate_growth_metrics(self) -> Dict:
        """计算增长指标"""
        conn = sqlite3.connect(self.db_path)
        
        # 计算用户增长
        query = '''
            SELECT 
                COUNT(*) as total_users,
                COUNT(CASE WHEN created_at >= datetime('now', '-30 days') THEN 1 END) as new_users_30d,
                COUNT(CASE WHEN created_at >= datetime('now', '-7 days') THEN 1 END) as new_users_7d
            FROM users
        '''
        
        cursor = conn.cursor()
        cursor.execute(query)
        row = cursor.fetchone()
        
        conn.close()
        
        return {
            'total_users': row[0],
            'new_users_30d': row[1],
            'new_users_7d': row[2],
            'growth_rate_30d': row[1] / max(row[0] - row[1], 1) * 100 if row[0] > row[1] else 100
        }
    
    def _calculate_engagement_metrics(self) -> Dict:
        """计算参与度指标"""
        conn = sqlite3.connect(self.db_path)
        
        queries = {
            'avg_posts_per_user': '''
                SELECT AVG(post_count) FROM (
                    SELECT user_id, COUNT(*) as post_count 
                    FROM forum_posts 
                    GROUP BY user_id
                )
            ''',
            'active_user_ratio': '''
                SELECT 
                    COUNT(DISTINCT user_id) * 100.0 / (
                        SELECT COUNT(*) FROM users
                    ) as active_ratio
                FROM forum_posts 
                WHERE created_at >= datetime('now', '-30 days')
            ''',
            'avg_session_duration': '''
                SELECT AVG(duration_minutes) FROM user_sessions
            '''
        }
        
        metrics = {}
        cursor = conn.cursor()
        
        for key, query in queries.items():
            cursor.execute(query)
            metrics[key] = cursor.fetchone()[0]
        
        conn.close()
        return metrics
    
    def _generate_recommendations(self) -> List[str]:
        """生成改进建议"""
        recommendations = []
        report = self.generate_community_report()
        
        # 基于数据分析生成建议
        if report['engagement_metrics'].get('active_user_ratio', 0) < 20:
            recommendations.append("活跃用户比例较低，建议增加社区活动")
        
        if report['growth_metrics'].get('growth_rate_30d', 0) < 10:
            recommendations.append("用户增长缓慢，建议加强宣传和推广")
        
        if len(report['popular_topics']) < 5:
            recommendations.append("话题多样性不足，建议引导更多讨论主题")
        
        return recommendations

### 2. 反馈收集和分析
#### 用户反馈系统：
```python
# feedback_system.py
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum
import json

class FeedbackType(Enum):
    BUG = "bug"
    FEATURE = "feature"
    IMPROVEMENT = "improvement"
    DOCUMENTATION = "documentation"
    OTHER = "other"

class FeedbackSystem:
    def __init__(self, db_path: str = "feedback.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                feedback_type TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                priority INTEGER DEFAULT 3,
                status TEXT DEFAULT 'new',
                votes INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                tags TEXT,
                metadata TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback_votes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                feedback_id INTEGER NOT NULL,
                user_id TEXT NOT NULL,
                vote_type TEXT CHECK(vote_type IN ('up', 'down')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(feedback_id, user_id),
                FOREIGN KEY (feedback_id) REFERENCES feedback (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback_comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                feedback_id INTEGER NOT NULL,
                user_id TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (feedback_id) REFERENCES feedback (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def submit_feedback(self, user_id: str, feedback_type: FeedbackType, 
                       title: str, description: str, tags: List[str] = None,
                       priority: int = 3, metadata: Dict = None) -> int:
        """提交反馈"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        tags_json = json.dumps(tags) if tags else '[]'
        metadata_json = json.dumps(metadata) if metadata else '{}'
        
        cursor.execute('''
            INSERT INTO feedback 
            (user_id, feedback_type, title, description, priority, tags, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, feedback_type.value, title, description, 
              priority, tags_json, metadata_json))
        
        feedback_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return feedback_id
    
    def vote_feedback(self, feedback_id: int, user_id: str, vote_type: str):
        """投票反馈"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 检查是否已投票
            cursor.execute('''
                SELECT vote_type FROM feedback_votes 
                WHERE feedback_id = ? AND user_id = ?
            ''', (feedback_id, user_id))
            
            existing_vote = cursor.fetchone()
            
            if existing_vote:
                # 更新现有投票
                if existing_vote[0] == vote_type:
                    # 取消投票
                    cursor.execute('''
                        DELETE FROM feedback_votes 
                        WHERE feedback_id = ? AND user_id = ?
                    ''', (feedback_id, user_id))
                    
                    # 更新票数
                    cursor.execute('''
                        UPDATE feedback 
                        SET votes = votes - 1 
                        WHERE id = ?
                    ''', (feedback_id,))
                else:
                    # 更改投票类型
                    cursor.execute('''
                        UPDATE feedback_votes 
                        SET vote_type = ? 
                        WHERE feedback_id = ? AND user_id = ?
                    ''', (vote_type, feedback_id, user_id))
            else:
                # 新投票
                cursor.execute('''
                    INSERT INTO feedback_votes (feedback_id, user_id, vote_type)
                    VALUES (?, ?, ?)
                ''', (feedback_id, user_id, vote_type))
                
                # 更新票数
                cursor.execute('''
                    UPDATE feedback 
                    SET votes = votes + 1 
                    WHERE id = ?
                ''', (feedback_id,))
            
            conn.commit()
            
        except Exception as e:
            conn.rollback()
            raise e
        
        finally:
            conn.close()
    
    def get_popular_feedback(self, feedback_type: str = None, 
                           limit: int = 20) -> List[Dict]:
        """获取热门反馈"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        conditions = []
        params = []
        
        if feedback_type:
            conditions.append('feedback_type = ?')
            params.append(feedback_type)
        
        where_clause = ' AND '.join(conditions) if conditions else '1=1'
        params.append(limit)
        
        cursor.execute(f'''
            SELECT * FROM feedback 
            WHERE {where_clause}
            ORDER BY votes DESC, created_at DESC
            LIMIT ?
        ''', params)
        
        feedbacks = cursor.fetchall()
        
        # 获取评论数量
        result = []
        for feedback in feedbacks:
            feedback_dict = dict(feedback)
            
            cursor.execute('''
                SELECT COUNT(*) FROM feedback_comments 
                WHERE feedback_id = ?
            ''', (feedback_dict['id'],))
            
            feedback_dict['comment_count'] = cursor.fetchone()[0]
            result.append(feedback_dict)
        
        conn.close()
        return result
    
    def analyze_feedback_trends(self, days: int = 90) -> Dict:
        """分析反馈趋势"""
        conn = sqlite3.connect(self.db_path)
        
        # 按类型统计
        type_query = '''
            SELECT feedback_type, COUNT(*) as count
            FROM feedback
            WHERE created_at >= datetime('now', ?)
            GROUP BY feedback_type
            ORDER BY count DESC
        '''
        
        # 按时间统计
        time_query = '''
            SELECT DATE(created_at) as date, feedback_type, COUNT(*) as count
            FROM feedback
            WHERE created_at >= datetime('now', ?)
            GROUP BY DATE(created_at), feedback_type
            ORDER BY date
        '''
        
        cursor = conn.cursor()
        
        # 执行类型统计
        cursor.execute(type_query, (f'-{days} days',))
        type_stats = {}
        for row in cursor.fetchall():
            type_stats[row[0]] = row[1]
        
        # 执行时间统计
        cursor.execute(time_query, (f'-{days} days',))
        time_stats = []
        for row in cursor.fetchall():
            time_stats.append({
                'date': row[0],
                'type': row[1],
                'count': row[2]
            })
        
        conn.close()
        
        return {
            'type_distribution': type_stats,
            'time_series': time_stats,
            'total_feedback': sum(type_stats.values()),
            'avg_daily_feedback': sum(type_stats.values()) / days
        }
```

## 🚀 最佳实践

### 1. 社区管理最佳实践
```
内容管理:
• 及时回复用户问题
• 鼓励高质量内容
• 处理不当行为
• 维护友好氛围

用户支持:
• 提供多种支持渠道
• 建立知识库和FAQ
• 培训支持团队
• 跟踪问题解决率

社区发展:
• 定期组织活动
• 鼓励用户贡献
• 建立奖励机制
• 收集用户反馈
```

### 2. 反馈处理流程
```
反馈收集:
1. 用户提交反馈
2. 自动分类和标签
3. 初步评估优先级
4. 分配给相关人员

处理流程:
1. 确认收到反馈
2. 调查和分析问题
3. 制定解决方案
4. 实施和测试
5. 通知用户结果

跟进和优化:
1. 收集用户满意度
2. 分析处理效果
3. 优化处理流程
4. 预防类似问题
```

### 3. 社区健康指标
```
活跃度指标:
• 日活跃用户数
• 月活跃用户数
• 用户发帖频率
• 用户互动率

质量指标:
• 问题解决率
• 用户满意度
• 内容质量评分
• 专家参与度

增长指标:
• 新用户增长率
• 用户留存率
• 社区影响力
• 品牌认知度
```

---
**社区论坛和用户支持指南版本**: 1.0.0
**最后更新**: 2026-02-23
**适用对象**: 社区管理员、用户支持团队

**强大社区，卓越支持！** 💬🤝

**用户第一，服务至上！** 👥🏆