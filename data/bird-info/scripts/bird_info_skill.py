#!/usr/bin/env python3
"""
Bird Info Skill - 鸟类信息查询技能
使用 requests 库获取网页内容
"""

import sys
import json
import re
import urllib.parse
from typing import Dict, List, Optional, Tuple

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


def http_fetch(url: str, timeout: int = 30) -> Optional[str]:
    """使用 requests 库获取网页内容"""
    try:
        if HAS_REQUESTS:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            return response.text
        else:
            import urllib.request
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0'
            })
            with urllib.request.urlopen(req, timeout=timeout) as f:
                return f.read().decode('utf-8')
    except Exception as e:
        print(f"获取网页失败：{e}", file=sys.stderr)
        return None


def extract_text_from_html(html: str) -> str:
    """从 HTML 中提取纯文本"""
    # 移除 script 和 style 标签
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
    # 移除所有 HTML 标签，替换为空格（不是换行）
    text = re.sub(r'<[^>]+>', ' ', html)
    # 解码 HTML 实体
    text = text.replace('&nbsp;', ' ')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&amp;', '&')
    text = text.replace('&quot;', '"')
    # 清理多余空白，但保留句子结构
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


class BirdInfoSkill:
    """鸟类信息查询技能"""
    
    TAXONOMY_URL = "https://dongniao.net/taxonomy.html"
    BASE_URL = "https://dongniao.net"
    
    def __init__(self):
        self.taxonomy_cache = None
        self.taxonomy_html = None
    
    def search_bird(self, bird_name: str) -> Optional[Dict]:
        """搜索鸟类"""
        if not self.taxonomy_cache:
            print(f"📚 正在加载懂鸟分类页面...")
            self.taxonomy_html = http_fetch(self.TAXONOMY_URL)
            if not self.taxonomy_html:
                return None
            self.taxonomy_cache = extract_text_from_html(self.taxonomy_html)
            print(f"✅ 分类页面已加载 ({len(self.taxonomy_cache)} 字符)")
        
        return self._find_bird_in_taxonomy(self.taxonomy_html, bird_name)
    
    def _find_bird_in_taxonomy(self, html: str, search_term: str) -> Optional[Dict]:
        """在分类页面 HTML 中查找鸟类"""
        matches = []
        exact_matches = []
        
        pattern = r'href="(/nd/\d+/[^/]+)/([^/]+)/([^"]+)"[^>]*>([^<]+)</a>'
        
        for match in re.finditer(pattern, html):
            link_path = match.group(1)
            english_raw = match.group(2)
            scientific_raw = match.group(3)
            display_name = match.group(4)
            
            chinese_name = urllib.parse.unquote(link_path.split('/')[-1].replace('+', ' '))
            english_name = urllib.parse.unquote(english_raw.replace('+', ' '))
            scientific_name = urllib.parse.unquote(scientific_raw.replace('+', ' '))
            full_url = f"{self.BASE_URL}{link_path}/{english_raw}/{scientific_raw}"
            
            search_lower = search_term.lower().strip()
            search_norm = self._normalize(search_term)
            chinese_norm = self._normalize(chinese_name)
            
            is_exact_match = False
            
            if search_norm == chinese_norm:
                is_exact_match = True
                match_type = "中文名（完全匹配）"
            elif search_lower == english_name.lower().strip():
                is_exact_match = True
                match_type = "英文名（完全匹配）"
            elif search_lower == scientific_name.lower().strip():
                is_exact_match = True
                match_type = "学名（完全匹配）"
            
            if is_exact_match:
                exact_matches.append({
                    'chinese_name': chinese_name,
                    'english_name': english_name,
                    'scientific_name': scientific_name,
                    'display_name': display_name,
                    'full_url': full_url,
                    'score': 100,
                    'match_type': match_type
                })
        
        if exact_matches:
            best = exact_matches[0]
            print(f"✅ 找到完全匹配：{best['chinese_name']} ({best['english_name']}) - {best['match_type']}")
            return best
        
        return None
    
    def _normalize(self, text: str) -> str:
        """规范化文本"""
        text = re.sub(r'[，。、\s]+', ' ', text.strip())
        text = re.sub(r'[^\w\s\u4e00-\u9fff]', '', text)
        return text.strip().lower()
    
    def get_bird_details(self, url: str) -> Optional[Dict]:
        """获取鸟类详情"""
        print(f"📖 获取详情页面：{url}")
        html = http_fetch(url)
        if not html:
            return None
        
        return self._parse_details(html)
    
    def _parse_details(self, html: str) -> Dict:
        """解析详情页面 HTML"""
        text = extract_text_from_html(html)
        
        info = {
            'basic_info': {},
            'features': {},
            'habitat': '',
            'reproduction': '',
            'identification': '',
            'conservation': '',
            'distribution': ''
        }
        
        # 尝试从文本中提取基本信息（包括科属）
        # 格式：中文名（英文名：xxx，学名：xxx），是 xxx 的
        basic_patterns = [
            r'(.+?)（英文名：([^,，]+)，学名：([^)]+)），是([^的]+)的',  # 包含科属
            r'(.+?)（英文名：([^,，]+)，学名：([^)]+)）',  # 无科属
        ]
        
        for pattern in basic_patterns:
            basic_match = re.search(pattern, text)
            if basic_match:
                info['basic_info'] = {
                    '中文名': basic_match.group(1).strip().split(' - ')[0],
                    '英文名': basic_match.group(2).strip(),
                    '学名': basic_match.group(3).strip()
                }
                # 第 4 组是科属信息（如"雀形目雀科雀属"）
                if len(basic_match.groups()) >= 4:
                    info['basic_info']['科属'] = basic_match.group(4).strip()
                break
        
        # 尝试从标题提取作为备用
        if not info['basic_info'].get('中文名'):
            lines = text.split('\n')
            title = lines[0].strip() if lines else ''
            if ' - ' in title:
                parts = title.split(' - ')
                info['basic_info']['中文名'] = parts[0].strip()
                if len(parts) >= 2:
                    info['basic_info']['英文名'] = parts[1].strip()
                if len(parts) >= 3 and parts[2].strip() != '懂鸟':
                    info['basic_info']['学名'] = parts[2].strip()
        
        # 提取各个章节
        sections = {
            '外形特征': 'features',
            '鸣叫特征': 'features',
            '生活习性': 'habitat',
            '生长繁殖': 'reproduction',
            '区别辨识': 'identification',
            '保护现状': 'conservation',
            '地理分布': 'distribution'
        }
        
        for section_name, key in sections.items():
            pattern = rf'{section_name}：(.+?)(?=\n[A-Z]|\n\n[A-Z]|\n其他：|请点击|$)'
            match = re.search(pattern, text, re.DOTALL)
            if match:
                content = match.group(1).strip()
                content = re.sub(r'\s+', ' ', content)
                
                if key == 'features':
                    if not isinstance(info['features'], dict):
                        info['features'] = {}
                    info['features'][section_name] = content
                else:
                    info[key] = content
        
        # 特别处理保护现状
        conservation_pattern = r'保护现状：IUCN：([A-Z]+)[(（]([^)）]+)[)）]'
        conservation_match = re.search(conservation_pattern, text)
        if conservation_match:
            info['conservation'] = f"IUCN：{conservation_match.group(1)} ({conservation_match.group(2)})"
        
        return info
    
    def format_output(self, info: Dict, bird_match: Optional[Dict] = None) -> str:
        """格式化输出"""
        lines = []
        lines.append("=" * 50)
        
        # 标题
        if bird_match:
            chinese = bird_match.get('chinese_name', '未知')
            english = bird_match.get('english_name', '')
            scientific = bird_match.get('scientific_name', '')
        else:
            chinese = info.get('basic_info', {}).get('中文名', '未知')
            english = info.get('basic_info', {}).get('英文名', '')
            scientific = info.get('basic_info', {}).get('学名', '')
        
        lines.append(f"🐦 {chinese} - 鸟类详细信息")
        if english:
            lines.append(f"   {english} ({scientific})")
        lines.append("=" * 50)
        lines.append("")
        
        # 基本信息
        if info.get('basic_info'):
            lines.append("📌 基本信息")
            lines.append("-" * 30)
            for k, v in info['basic_info'].items():
                lines.append(f"   {k}: {v}")
            lines.append("")
        
        # 形态特征
        if info.get('features'):
            lines.append("📖 形态特征")
            lines.append("-" * 30)
            features = info['features']
            if isinstance(features, dict):
                for k, v in features.items():
                    lines.append(f"   {k}: {v[:150]}..." if len(v) > 150 else f"   {k}: {v}")
            else:
                lines.append(f"   {features[:200]}..." if len(features) > 200 else f"   {features}")
            lines.append("")
        
        # 生活习性
        if info.get('habitat'):
            lines.append("🌿 生活习性")
            lines.append("-" * 30)
            text = info['habitat']
            lines.append(f"   {text[:200]}..." if len(text) > 200 else f"   {text}")
            lines.append("")
        
        # 分布区域
        if info.get('distribution'):
            lines.append("🌍 分布区域")
            lines.append("-" * 30)
            text = info['distribution']
            lines.append(f"   {text[:200]}..." if len(text) > 200 else f"   {text}")
            lines.append("")
        
        # 保护状况
        if info.get('conservation'):
            lines.append("⚠️ 保护状况")
            lines.append("-" * 30)
            lines.append(f"   {info['conservation']}")
            lines.append("")
        
        lines.append("=" * 50)
        lines.append(f"📊 数据来源：懂鸟 (https://dongniao.net)")
        
        return '\n'.join(lines)
    
    def query(self, bird_name: str) -> Tuple[bool, str]:
        """查询鸟类信息"""
        print(f"🔍 正在查询：{bird_name}")
        
        bird = self.search_bird(bird_name)
        if not bird:
            return False, (
                f"❌ 没有该鸟类，请检查鸟类名称是否正确\n\n"
                f"查询名称：{bird_name}\n\n"
                f"提示：\n"
                f"- 请检查鸟名拼写是否正确\n"
                f"- 可以尝试使用中文名或英文名\n"
                f"- 该鸟可能不在懂鸟数据库中"
            )
        
        print(f"📖 获取详细信息...")
        details = self.get_bird_details(bird['full_url'])
        if not details:
            return False, f"❌ 无法获取 {bird['chinese_name']} 的详细信息"
        
        # 从详情中提取学名并更新 bird_match
        if details.get('basic_info', {}).get('学名'):
            bird['scientific_name'] = details['basic_info']['学名']
        
        output = self.format_output(details, bird)
        return True, output


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法：bird-info <鸟名>")
        print("示例：bird-info '麻雀'")
        sys.exit(1)
    
    if not HAS_REQUESTS:
        print("❌ 错误：需要安装 requests 库")
        print("请运行：pip3 install requests")
        sys.exit(1)
    
    bird_name = ' '.join(sys.argv[1:])
    skill = BirdInfoSkill()
    
    success, message = skill.query(bird_name)
    print(message)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()