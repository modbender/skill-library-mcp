#!/usr/bin/env python3
"""
Chinese AI Text Detector
Scans for AI-generated patterns in Chinese text
"""

import sys
import json
import re
from collections import defaultdict

# Detection patterns
PATTERNS = {
    # Critical patterns
    'three_part_structure': [
        r'首先[，,].*其次[，,].*最后',
        r'一方面[，,].*另一方面',
        r'第一[，,].*第二[，,].*第三',
        r'第一点.*第二点.*第三点',
    ],
    'mechanical_connectors': [
        '值得注意的是', '综上所述', '不难发现', '总而言之',
        '与此同时', '在此基础上', '由此可见', '此外',
        '不仅如此', '换句话说', '更重要的是', '需要强调的是',
    ],
    'empty_grand_words': [
        '赋能', '闭环', '智慧时代', '数字化转型', '生态',
        '愿景', '力量', '成就', '未来展望', '战略高度',
        '顶层设计', '协同增效', '降本增效', '打通壁垒',
    ],
    
    # High signal patterns
    'ai_high_freq_words': [
        '助力', '彰显', '凸显', '焕发', '深度剖析',
        '解构', '量子纠缠', '光谱', '加持', '赛道',
        '破圈', '出圈', '内卷', '颠覆', '革新',
        '创新驱动', '深度融合', '持续赋能', '全面升级',
    ],
    'technical_jargon': [
        '解构', '量子纠缠', '赛博', '光谱', '维度',
        '范式', '路径', '矩阵', '框架', '模型',
    ],
    
    # Medium signal patterns
    'filler_phrases': [
        '值得一提的是', '需要指出的是', '不得不说',
        '毫无疑问', '显而易见', '众所周知',
        '不言而喻', '如前所述', '正如我们所知',
    ],
    
    # Punctuation patterns
    'em_dash': '—',
    'semicolon': '；',
    'colon': '：',
    'ellipsis': '……',
    
    # Emotion indicators (lack of emotion is AI signal)
    'emotional_words': [
        '愤怒', '高兴', '难过', '失望', '惊讶', '担心',
        '开心', '郁闷', '焦虑', '兴奋', '害怕', '感动',
    ],
    
    # Internet slang (overuse is AI signal when mismatched)
    'internet_slang': [
        'yyds', '绝绝子', '破防', 'emo', 'cpu',
        '拿捏', '整活', '梗', '有梗', '无语',
    ],
}

# Replacements for humanization
REPLACEMENTS = {
    '值得注意的是': ['注意', '要提醒的是', '特别说一下'],
    '综上所述': ['总之', '说到底', '简单讲'],
    '不难发现': ['可以看到', '很明显'],
    '总而言之': ['总之', '总的来说'],
    '赋能': ['帮助', '提升', '支持'],
    '闭环': ['完整流程', '全链路'],
    '深度剖析': ['深入分析', '仔细看看'],
    '此外': ['另外', '还有'],
    '与此同时': ['同时', '这时候'],
}

def count_chinese_chars(text):
    """Count Chinese characters"""
    return len(re.findall(r'[\u4e00-\u9fff]', text))

def detect_patterns(text):
    """Detect AI patterns in Chinese text"""
    issues = defaultdict(list)
    char_count = count_chinese_chars(text)
    
    # Critical: Three-part structure
    for pattern in PATTERNS['three_part_structure']:
        matches = re.findall(pattern, text, re.DOTALL)
        for match in matches:
            issues['three_part_structure'].append(match[:50])
    
    # Critical: Mechanical connectors
    for phrase in PATTERNS['mechanical_connectors']:
        count = text.count(phrase)
        if count > 0:
            issues['mechanical_connectors'].append(f'{phrase} ({count}x)')
    
    # Critical: Empty grand words
    for word in PATTERNS['empty_grand_words']:
        count = text.count(word)
        if count > 0:
            issues['empty_grand_words'].append(f'{word} ({count}x)')
    
    # High signal: AI high-frequency words
    for word in PATTERNS['ai_high_freq_words']:
        count = text.count(word)
        if count > 0:
            issues['ai_high_freq_words'].append(f'{word} ({count}x)')
    
    # High signal: Filler phrases
    for phrase in PATTERNS['filler_phrases']:
        count = text.count(phrase)
        if count > 0:
            issues['filler_phrases'].append(f'{phrase} ({count}x)')
    
    # Medium signal: Punctuation overuse and distribution
    em_dash_count = text.count(PATTERNS['em_dash'])
    semicolon_count = text.count(PATTERNS['semicolon'])
    colon_count = text.count(PATTERNS['colon'])
    ellipsis_count = text.count(PATTERNS['ellipsis'])
    
    if char_count > 0:
        em_dash_density = em_dash_count / char_count * 100
        semicolon_density = semicolon_count / char_count * 100
        ellipsis_density = ellipsis_count / char_count * 100
        
        if em_dash_density > 1.0:
            issues['punctuation_overuse'].append(f'破折号过多 ({em_dash_count})')
        if semicolon_density > 0.5:
            issues['punctuation_overuse'].append(f'分号过多 ({semicolon_count})')
        if ellipsis_density > 1.5:
            issues['punctuation_overuse'].append(f'省略号过多 ({ellipsis_count})')
    
    # Detect parallel structures (对偶句)
    parallel_pattern = r'[，,][^，,。！？]{4,10}[；;，,][^，,。！？]{4,10}[。！？]'
    parallels = re.findall(parallel_pattern, text)
    if len(parallels) > 2:
        issues['excessive_rhetoric'].append(f'对偶句过多 ({len(parallels)})')
    
    # Detect uniform paragraph lengths
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    if len(paragraphs) >= 3:
        lengths = [len(p) for p in paragraphs]
        avg_len = sum(lengths) / len(lengths)
        variance = sum((l - avg_len) ** 2 for l in lengths) / len(lengths)
        if variance < avg_len * 0.1:  # Low variance = uniform
            issues['uniform_paragraphs'].append(f'段落长度过于均匀')
    
    # NEW: Detect emotional flatness
    emotional_count = sum(text.count(word) for word in PATTERNS['emotional_words'])
    if char_count > 0:
        emotional_density = emotional_count / char_count * 100
        if emotional_density < 0.1 and char_count > 500:  # Very low emotion in long text
            issues['emotional_flatness'].append(f'情感表达不足 (密度: {emotional_density:.2f}%)')
    
    # NEW: Detect vocabulary diversity (low = AI)
    sentences = re.split(r'[。！？]', text)
    if len(sentences) > 5:
        avg_sentence_len = sum(len(s) for s in sentences) / len(sentences)
        len_variance = sum((len(s) - avg_sentence_len) ** 2 for s in sentences) / len(sentences)
        if len_variance < avg_sentence_len * 0.2:
            issues['low_burstiness'].append(f'句子长度过于均匀 (低突发性)')
    
    # NEW: Detect repetitive sentence starters
    sentence_starters = defaultdict(int)
    for sent in sentences[:20]:  # Check first 20 sentences
        sent = sent.strip()
        if len(sent) > 3:
            starter = sent[:2]
            sentence_starters[starter] += 1
    
    max_repeat = max(sentence_starters.values()) if sentence_starters else 0
    if max_repeat > 3:
        issues['repetitive_structure'].append(f'句首重复过多 (最高{max_repeat}次)')
    
    # NEW: Check for internet slang overuse (context mismatch)
    slang_count = sum(text.count(word) for word in PATTERNS['internet_slang'])
    if slang_count > 5 and '学术' not in text and '论文' not in text:
        # High slang in non-casual context
        issues['slang_overuse'].append(f'网络用语过度 ({slang_count}次)')
    
    return issues, char_count

def calculate_score(issues, char_count):
    """Calculate AI probability score"""
    total_issues = sum(len(v) for v in issues.values())
    
    # Critical patterns trigger very high
    critical_count = (
        len(issues.get('three_part_structure', [])) +
        len(issues.get('mechanical_connectors', [])) +
        len(issues.get('empty_grand_words', []))
    )
    
    if critical_count > 0:
        return 'very high'
    
    # Calculate density
    if char_count > 0:
        density = total_issues / char_count * 100
    else:
        density = 0
    
    if total_issues > 20 or density > 3:
        return 'high'
    elif total_issues > 10 or density > 1.5:
        return 'medium'
    else:
        return 'low'

def format_output(issues, char_count, score, as_json=False, score_only=False):
    """Format detection results"""
    total_issues = sum(len(v) for v in issues.values())
    
    if score_only:
        return score
    
    if as_json:
        return json.dumps({
            'score': score,
            'char_count': char_count,
            'total_issues': total_issues,
            'issues': dict(issues)
        }, ensure_ascii=False, indent=2)
    
    # Human-readable output
    lines = []
    lines.append(f'AI 概率: {score.upper()}')
    lines.append(f'字符数: {char_count}')
    lines.append(f'问题总数: {total_issues}')
    lines.append('')
    
    # Category breakdown
    category_names = {
        'three_part_structure': '【严重】三段式套路',
        'mechanical_connectors': '【严重】机械连接词',
        'empty_grand_words': '【严重】空洞宏大词',
        'ai_high_freq_words': '【高信号】AI 高频词',
        'filler_phrases': '【中等】套话',
        'excessive_rhetoric': '【高信号】过度修辞',
        'punctuation_overuse': '【中等】标点过度',
        'uniform_paragraphs': '【中等】段落均匀',
        'emotional_flatness': '【风格】情感平淡',
        'low_burstiness': '【风格】低突发性',
        'repetitive_structure': '【中等】结构重复',
        'slang_overuse': '【中等】网络用语过度',
    }
    
    for category, name in category_names.items():
        if category in issues and issues[category]:
            lines.append(f'{name}: {len(issues[category])}')
            for item in issues[category][:3]:  # Show first 3
                lines.append(f'  - {item}')
            if len(issues[category]) > 3:
                lines.append(f'  ... 还有 {len(issues[category]) - 3} 个')
            lines.append('')
    
    return '\n'.join(lines)

def main():
    # Parse arguments
    as_json = '-j' in sys.argv
    score_only = '-s' in sys.argv
    
    # Read input
    if len(sys.argv) > 1 and sys.argv[1] not in ['-j', '-s']:
        filepath = sys.argv[1]
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()
        except FileNotFoundError:
            print(f'错误: 文件未找到 {filepath}', file=sys.stderr)
            sys.exit(1)
    else:
        text = sys.stdin.read()
    
    # Detect patterns
    issues, char_count = detect_patterns(text)
    score = calculate_score(issues, char_count)
    
    # Output results
    output = format_output(issues, char_count, score, as_json, score_only)
    print(output)

if __name__ == '__main__':
    main()
