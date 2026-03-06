#!/usr/bin/env python3
import sys
import os
import argparse
import requests
import json
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any
from dataclasses import dataclass
import sqlite3
import tempfile

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

@dataclass
class Skill:
    slug: str
    name: str
    version: str
    description: str
    author: str
    category: str
    tags: List[str]
    score: float
    published_at: str
    
    def __str__(self):
        return f"{self.name} ({self.slug}@v{self.version})"

class ClawHubSkillExplorer:
    def __init__(self, api_url: str = "https://clawhub.ai"):
        self.api_url = api_url
        self.session = requests.Session()
        self.cache_db = None
        self._init_cache()
    
    def _init_cache(self):
        """Initialize in-memory cache database"""
        self.cache_db = sqlite3.connect(':memory:')
        cursor = self.cache_db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS skills (
                slug TEXT PRIMARY KEY,
                name TEXT,
                version TEXT,
                description TEXT,
                author TEXT,
                category TEXT,
                tags TEXT,
                score REAL,
                published_at TEXT,
                cache_time TEXT
            )
        ''')
        self.cache_db.commit()
    
    def _execute_clawhub_cmd(self, cmd: str) -> str:
        """Execute ClawHub CLI command"""
        try:
            result = os.popen(cmd).read().strip()
            return result
        except Exception as e:
            print(f"❌ Error executing command: {e}")
            return ""
    
    def fetch_skills(self, limit: int = 50, force_refresh: bool = False) -> List[Skill]:
        """Fetch skills from ClawHub platform"""
        if not force_refresh:
            cached_skills = self._get_cached_skills()
            if cached_skills:
                print("✅ Using cached skills (last updated:", 
                      cached_skills[0].published_at, ")")
                return cached_skills
        
        print("🔄 Fetching skills from ClawHub platform...")
        
        try:
            # Use clawhub explore command to get skills
            output = self._execute_clawhub_cmd("clawhub explore")
            
            skills = []
            lines = output.split('\n')
            for i, line in enumerate(lines):
                if "Fetching latest skills" in line:
                    continue
                
                # Parse line format: <slug>  v<version>  <time>  <description>
                match = re.match(r'(\w[\w-]*)\s+v([\d\.]+)\s+(\w.*?ago|just now)\s+(.*)', 
                                line.strip())
                
                if match:
                    slug = match.group(1)
                    version = match.group(2)
                    published_time = match.group(3)
                    description = match.group(4)
                    
                    skills.append(Skill(
                        slug=slug,
                        name=slug.replace('-', ' ').title(),
                        version=version,
                        description=description,
                        author="Unknown",
                        category="general",
                        tags=[],
                        score=0.0,
                        published_at=self._parse_time(published_time)
                    ))
            
            self._cache_skills(skills)
            print(f"✅ Fetched {len(skills)} skills from ClawHub")
            return skills
        
        except Exception as e:
            print(f"❌ Error fetching skills: {e}")
            return []
    
    def _parse_time(self, time_str: str) -> str:
        """Parse relative time to ISO format"""
        if "just now" in time_str:
            return datetime.now().isoformat()
        
        match = re.match(r'(\d+)([mh])', time_str.replace(' ago', ''))
        if match:
            value = int(match.group(1))
            unit = match.group(2)
            
            delta = None
            if unit == 'm':
                delta = timedelta(minutes=value)
            elif unit == 'h':
                delta = timedelta(hours=value)
            
            if delta:
                return (datetime.now() - delta).isoformat()
        
        return datetime.now().isoformat()
    
    def search_skills(self, query: str, limit: int = 20) -> List[Skill]:
        """Search for skills by query string"""
        skills = self.fetch_skills()
        
        # Search in name, description, and tags
        results = []
        
        for skill in skills:
            search_text = (skill.name + " " + skill.description).lower()
            if query.lower() in search_text:
                score = self._calculate_score(skill, query)
                results.append((score, skill))
        
        # Sort by score
        results.sort(key=lambda x: x[0], reverse=True)
        
        return [skill for _, skill in results[:limit]]
    
    def _calculate_score(self, skill: Skill, query: str) -> float:
        """Calculate search relevancy score"""
        score = 0
        
        # Name match
        if query.lower() in skill.name.lower():
            score += 5
        
        # Description match
        if query.lower() in skill.description.lower():
            score += 3
        
        # Exact match bonus
        if query.lower() == skill.name.lower() or query.lower() == skill.slug.lower():
            score += 10
        
        # Version bonus
        try:
            version_num = float(skill.version.split('.')[0])  # Just check major version
            if version_num >= 1:
                score += 1
        except Exception as e:
            pass
        
        return score
    
    def browse_category(self, category: str, limit: int = 30) -> List[Skill]:
        """Browse skills by category"""
        skills = self.fetch_skills()
        
        if category == "all":
            return skills[:limit]
        
        return [skill for skill in skills if 
                category.lower() in skill.category.lower()][:limit]
    
    def get_skill_details(self, slug: str) -> Dict[str, Any]:
        """Get detailed information about a skill"""
        try:
            output = self._execute_clawhub_cmd(f"clawhub inspect {slug}")
            
            details = {
                'slug': slug,
                'basic_info': {},
                'files': {},
                'content': ''
            }
            
            lines = output.split('\n')
            in_basic_info = False
            in_files = False
            
            for line in lines:
                line = line.strip()
                
                if not line:
                    continue
                
                if "Basic info" in line:
                    in_basic_info = True
                    in_files = False
                    continue
                
                if "Files" in line:
                    in_basic_info = False
                    in_files = True
                    continue
                
                if "Content" in line:
                    in_basic_info = False
                    in_files = False
                    continue
                
                if in_basic_info and ':' in line:
                    key, value = line.split(':', 1)
                    details['basic_info'][key.strip()] = value.strip()
                
                if in_files and '.' in line and 'bytes' in line:
                    filename = line.split()[0]
                    details['files'][filename] = line
                
                if not in_basic_info and not in_files and line and not line.startswith('---'):
                    details['content'] += line + '\n'
            
            return details
        
        except Exception as e:
            print(f"❌ Error getting skill details: {e}")
            return {}
    
    def favorite_skill(self, slug: str) -> bool:
        """Add a skill to favorites"""
        try:
            # Check if skill exists
            skills = self.fetch_skills()
            if slug not in [skill.slug for skill in skills]:
                print(f"❌ Skill '{slug}' not found")
                return False
            
            output = self._execute_clawhub_cmd(f"clawhub star {slug}")
            
            if "Success" in output or "Added to favorites" in output:
                print(f"✅ Skill '{slug}' added to favorites")
                return True
            else:
                print(f"❌ Failed to favorite skill: {output}")
                return False
        
        except Exception as e:
            print(f"❌ Error favoriting skill: {e}")
            return False
    
    def get_recommendations(self, limit: int = 10) -> List[Skill]:
        """Get recommended skills based on user activity"""
        skills = self.fetch_skills()
        
        # Simple recommendation based on version and score
        def version_key(skill):
            try:
                # 只取主版本号
                main_version = float(skill.version.split('.')[0])
                return main_version * (1 + skill.score)
            except:
                return 0
        
        recommended = sorted(
            skills, 
            key=version_key,
            reverse=True
        )
        
        return recommended[:limit]
    
    def clear_cache(self):
        """Clear cached skills data"""
        try:
            cursor = self.cache_db.cursor()
            cursor.execute('DELETE FROM skills')
            self.cache_db.commit()
            print("✅ Cache cleared")
            return True
        except Exception as e:
            print(f"❌ Error clearing cache: {e}")
            return False
    
    def list_categories(self) -> List[str]:
        """List all available skill categories"""
        skills = self.fetch_skills()
        
        categories = set()
        for skill in skills:
            if skill.category:
                categories.add(skill.category)
        
        return sorted(list(categories))
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get platform statistics"""
        skills = self.fetch_skills()
        
        return {
            'total_skills': len(skills),
            'categories': self.list_categories(),
            'versions': self._get_version_distribution(skills)
        }
    
    def _get_version_distribution(self, skills: List[Skill]) -> Dict[str, int]:
        """Get version distribution statistics"""
        distribution = {}
        
        for skill in skills:
            try:
                version_num = float(skill.version)
                version_range = f"{int(version_num)}.x"
                
                if version_range in distribution:
                    distribution[version_range] += 1
                else:
                    distribution[version_range] = 1
            except:
                continue
        
        return distribution
    
    def _get_cached_skills(self) -> List[Skill]:
        """Get skills from cache database"""
        try:
            cursor = self.cache_db.cursor()
            cursor.execute('''
                SELECT slug, name, version, description, author, category, tags, score, published_at
                FROM skills
                ORDER BY score DESC
            ''')
            
            skills = []
            for row in cursor.fetchall():
                skills.append(Skill(
                    slug=row[0],
                    name=row[1],
                    version=row[2],
                    description=row[3],
                    author=row[4],
                    category=row[5],
                    tags=json.loads(row[6]) if row[6] else [],
                    score=row[7],
                    published_at=row[8]
                ))
            
            return skills
        except Exception as e:
            print(f"❌ Error reading cache: {e}")
            return []
    
    def _cache_skills(self, skills: List[Skill]):
        """Cache skills data to database"""
        try:
            cursor = self.cache_db.cursor()
            cursor.execute('DELETE FROM skills')
            
            for skill in skills:
                cursor.execute('''
                    INSERT OR REPLACE INTO skills 
                    (slug, name, version, description, author, category, tags, score, published_at, cache_time)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    skill.slug,
                    skill.name,
                    skill.version,
                    skill.description,
                    skill.author,
                    skill.category,
                    json.dumps(skill.tags),
                    skill.score,
                    skill.published_at,
                    datetime.now().isoformat()
                ))
            
            self.cache_db.commit()
        except Exception as e:
            print(f"❌ Error writing cache: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="ClawHub技能探索和导航工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例使用方法：
  clawhub-skill-explorer search "problem solving"
  clawhub-skill-explorer browse "productivity"
  clawhub-skill-explorer view "clawhub-search-verify"
  clawhub-skill-explorer favorite "clawhub-search-verify"
        '''
    )
    
    subparsers = parser.add_subparsers(title="命令", dest="command")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="搜索技能")
    search_parser.add_argument("query", help="搜索关键词")
    search_parser.add_argument("-l", "--limit", type=int, default=20, 
                             help="返回结果数量限制")
    search_parser.add_argument("-f", "--force-refresh", action="store_true",
                             help="强制刷新缓存")
    
    # Browse command
    browse_parser = subparsers.add_parser("browse", help="浏览分类")
    browse_parser.add_argument("category", nargs='?', default="all",
                             help="分类名称（默认：all）")
    browse_parser.add_argument("-l", "--limit", type=int, default=30, 
                             help="返回结果数量限制")
    
    # View command
    view_parser = subparsers.add_parser("view", help="查看技能详情")
    view_parser.add_argument("slug", help="技能slug")
    
    # Favorite command
    favorite_parser = subparsers.add_parser("favorite", help="收藏技能")
    favorite_parser.add_argument("slug", help="技能slug")
    
    # Recommendations command
    rec_parser = subparsers.add_parser("recommend", help="获取推荐技能")
    rec_parser.add_argument("-l", "--limit", type=int, default=10,
                          help="推荐数量限制")
    
    # Statistics command
    stats_parser = subparsers.add_parser("stats", help="获取平台统计")
    
    # Categories command
    cats_parser = subparsers.add_parser("categories", help="列出所有分类")
    
    # Clear cache command
    clear_parser = subparsers.add_parser("clear-cache", help="清除缓存")
    
    # Refresh cache command
    refresh_parser = subparsers.add_parser("refresh", help="刷新缓存")
    
    args = parser.parse_args()
    
    explorer = ClawHubSkillExplorer()
    
    if args.command == "search":
        results = explorer.search_skills(args.query, args.limit)
        
        if results:
            print(f"🔍 找到 {len(results)} 个匹配技能：")
            print("=" * 80)
            for skill in results:
                print(f"🎯 {skill.name} ({skill.slug}@v{skill.version})")
                print(f"   描述: {skill.description}")
                print(f"   发布: {skill.published_at}")
                print()
        else:
            print(f"❌ 未找到与 '{args.query}' 相关的技能")
    
    elif args.command == "browse":
        results = explorer.browse_category(args.category, args.limit)
        
        if results:
            print(f"📂 分类 '{args.category}' 的技能（{len(results)}个）：")
            print("=" * 80)
            for skill in results:
                print(f"🎯 {skill.name} ({skill.slug}@v{skill.version})")
                print(f"   描述: {skill.description}")
                print()
        else:
            print(f"❌ 分类 '{args.category}' 为空或未找到")
    
    elif args.command == "view":
        details = explorer.get_skill_details(args.slug)
        
        if details:
            print(f"🎯 技能详情 - {args.slug}")
            print("=" * 80)
            
            if details['basic_info']:
                print("\n📋 基本信息:")
                for key, value in details['basic_info'].items():
                    print(f"   {key}: {value}")
            
            if details['files']:
                print("\n📁 文件列表:")
                for filename, info in details['files'].items():
                    print(f"   {filename}")
            
            if details['content']:
                print("\n📄 详细介绍:")
                print(details['content'])
        else:
            print(f"❌ 技能 '{args.slug}' 未找到")
    
    elif args.command == "favorite":
        success = explorer.favorite_skill(args.slug)
        if not success:
            print(f"❌ 收藏技能 '{args.slug}' 失败")
    
    elif args.command == "recommend":
        recommendations = explorer.get_recommendations(args.limit)
        
        print("🌟 推荐技能：")
        print("=" * 80)
        for i, skill in enumerate(recommendations, 1):
            print(f"{i}. {skill.name} ({skill.slug}@v{skill.version})")
            print(f"   描述: {skill.description}")
            print()
    
    elif args.command == "stats":
        stats = explorer.get_statistics()
        
        print("📊 ClawHub 平台统计：")
        print("=" * 80)
        print(f"总技能数量: {stats['total_skills']}")
        print(f"分类: {', '.join(stats['categories'])}")
        print("版本分布:")
        for version, count in stats['versions'].items():
            print(f"   {version}: {count} 个技能")
    
    elif args.command == "categories":
        categories = explorer.list_categories()
        
        print("📂 所有分类：")
        print("=" * 80)
        for category in categories:
            print(f"🎯 {category}")
    
    elif args.command == "clear-cache":
        explorer.clear_cache()
    
    elif args.command == "refresh":
        explorer.clear_cache()
        explorer.fetch_skills(force_refresh=True)
        print("✅ 数据刷新完成")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
