#!/usr/bin/env python3
"""
Chinese Text Style Transformer
将文本转换为不同的中文写作风格
支持：口语化、知乎、小红书、公众号、学术、文艺等风格
"""

import sys
import re
import random

# 风格配置
STYLES = {
    'casual': {
        'name': '口语化风格',
        'description': '像朋友聊天，适合社交媒体',
        'connectors': ['说实话', '没想到', '确实', '挺', '真的', '其实', '不过'],
        'sentence_starters': ['你看', '我觉得', '说起来', '话说', '讲真'],
        'intensifiers': ['真的', '超级', '特别', '非常', '相当', '蛮'],
        'endings': ['吧', '呢', '啊', '哦', '嘛'],
        'avoid_formal': True,
        'use_emoji': True,
        'short_paragraphs': True,
    },
    
    'zhihu': {
        'name': '知乎风格',
        'description': '理性、有深度、带个人观点',
        'connectors': ['从我的经验来看', '实际上', '具体来说', '举个例子'],
        'sentence_starters': ['我认为', '个人觉得', '依我看', '说实在的'],
        'data_phrases': ['数据显示', '根据XX调研', '实测发现', '对比后发现'],
        'opinion_markers': ['我不这么认为', '这种说法有待商榷', '更准确的说法是'],
        'use_examples': True,
        'use_data': True,
        'logical_depth': True,
    },
    
    'xiaohongshu': {
        'name': '小红书风格',
        'description': '活泼、emoji多、种草感',
        'connectors': ['姐妹们', '真的绝了', '爱了爱了', '太好用了', '必须推荐'],
        'sentence_starters': ['分享一下', '来说说', '强烈推荐', '今天要说的是'],
        'intensifiers': ['超级', '巨', '绝绝子', 'yyds', '神仙', '宝藏'],
        'emoji_density': 'high',
        'use_hashtags': True,
        'enthusiastic': True,
        'short_sentences': True,
    },
    
    'wechat': {
        'name': '公众号风格',
        'description': '有故事感、引人入胜',
        'openings': ['你有没有想过', '曾经有这样一个故事', '最近发生了一件事', '很多人都经历过'],
        'connectors': ['这让我想起了', '说到这里', '你可能会问', '答案是'],
        'storytelling': True,
        'emotional': True,
        'relatable': True,
        'use_questions': True,
    },
    
    'academic': {
        'name': '学术风格',
        'description': '严谨但不死板',
        'connectors': ['研究表明', '数据显示', '实验结果表明', '根据XX理论'],
        'avoid_colloquial': True,
        'use_citations': True,
        'precise_terms': True,
        'logical_structure': True,
        'reduce_emotion': True,
    },
    
    'literary': {
        'name': '文艺风格',
        'description': '有文学感、意境',
        'connectors': ['仿佛', '犹如', '宛如', '恰似'],
        'descriptive_phrases': ['在XX的光影里', '伴随着XX的气息', '如同XX般'],
        'use_metaphor': True,
        'use_imagery': True,
        'poetic': True,
        'emotional_depth': True,
    },
}

# 通用替换规则
FORMAL_TO_CASUAL = {
    '首先': '首先',  # 直接删除或替换
    '其次': '再说',
    '最后': '最后',
    '值得注意的是': '注意',
    '综上所述': '总之',
    '不难发现': '可以看到',
    '总而言之': '总的来说',
    '与此同时': '同时',
    '在此基础上': '基于这个',
    '由此可见': '所以',
    '此外': '另外',
    '然而': '但是',
    '因此': '所以',
    '并且': '而且',
}

# Emoji库（按情感分类）
EMOJIS = {
    'positive': ['😊', '👍', '❤️', '🎉', '✨', '💪', '🔥', '👏', '💯', '🌟'],
    'thinking': ['🤔', '💭', '💡', '🧐', '👀'],
    'warning': ['⚠️', '❗', '⚡', '🚨'],
    'casual': ['😂', '💀', '😅', '🙃', '😎'],
}

def remove_formal_structure(text):
    """移除正式的三段式结构"""
    # 删除"首先、其次、最后"
    text = re.sub(r'首先[，,]\s*', '', text)
    text = re.sub(r'其次[，,]\s*', '', text)
    text = re.sub(r'最后[，,]\s*', '', text)
    
    # 删除"第一、第二、第三"
    text = re.sub(r'第[一二三四五][，,、]\s*', '', text)
    
    return text

def add_casual_connectors(text, style_config):
    """添加口语化连接词"""
    if 'connectors' not in style_config:
        return text
    
    sentences = re.split(r'([。！？])', text)
    result = []
    
    for i in range(0, len(sentences) - 1, 2):
        sentence = sentences[i]
        punct = sentences[i + 1] if i + 1 < len(sentences) else ''
        
        # 随机在句首添加连接词
        if i > 0 and random.random() < 0.2:
            connector = random.choice(style_config['connectors'])
            sentence = connector + '，' + sentence
        
        result.append(sentence + punct)
    
    return ''.join(result)

def add_emojis(text, density='medium'):
    """添加emoji表情"""
    if density == 'none':
        return text
    
    sentences = re.split(r'([。！？])', text)
    result = []
    emoji_prob = {'low': 0.1, 'medium': 0.2, 'high': 0.4}.get(density, 0.2)
    
    for i in range(0, len(sentences) - 1, 2):
        sentence = sentences[i]
        punct = sentences[i + 1] if i + 1 < len(sentences) else ''
        
        # 在句尾添加emoji
        if random.random() < emoji_prob:
            # 根据句子情感选择emoji类型
            if '?' in punct or '吗' in sentence:
                emoji = random.choice(EMOJIS['thinking'])
            elif '!' in punct or any(w in sentence for w in ['太', '超', '很', '特别']):
                emoji = random.choice(EMOJIS['positive'])
            else:
                emoji = random.choice(EMOJIS['casual'])
            
            sentence = sentence + ' ' + emoji
        
        result.append(sentence + punct)
    
    return ''.join(result)

def transform_xiaohongshu(text):
    """小红书风格转换"""
    # 移除正式结构
    text = remove_formal_structure(text)
    
    # 替换正式用词
    for formal, casual in FORMAL_TO_CASUAL.items():
        text = text.replace(formal, casual)
    
    # 添加种草用语
    grass_phrases = ['真的绝了', '爱了爱了', '强烈推荐', '必须安利', 'yyds']
    sentences = text.split('。')
    if len(sentences) > 1:
        sentences[0] = random.choice(['姐妹们！', '分享一下～']) + sentences[0]
    
    text = '。'.join(sentences)
    
    # 添加大量emoji
    text = add_emojis(text, density='high')
    
    # 添加话题标签
    if '##' not in text:
        tags = '\n\n#好物分享 #种草 #实用推荐'
        text += tags
    
    # 分段（短段落）
    text = shorten_paragraphs(text, max_length=100)
    
    return text

def transform_zhihu(text):
    """知乎风格转换"""
    # 移除过度正式的结构
    text = remove_formal_structure(text)
    
    # 添加个人观点标记
    opinion_markers = ['从我的经验来看', '个人认为', '依我看', '说实在的']
    sentences = text.split('。')
    if len(sentences) > 2:
        # 在第一段后添加个人观点
        sentences[1] = random.choice(opinion_markers) + '，' + sentences[1]
    
    text = '。'.join(sentences)
    
    # 添加实例引导
    text = re.sub(r'例如[，,]', '举个例子，', text)
    
    # 添加数据/经验支撑
    if '数据' not in text and '实测' not in text:
        data_phrases = ['从实际使用来看', '根据我的观察', '实测发现']
        if random.random() < 0.3:
            text = random.choice(data_phrases) + '，' + text
    
    return text

def transform_wechat(text):
    """公众号风格转换"""
    # 故事化开头
    openings = [
        '你有没有想过这样一个问题：',
        '最近发生了一件有意思的事。',
        '很多人都经历过这样的困境：',
        '说起来，这事儿挺有意思的。'
    ]
    
    # 如果开头太直接，添加故事化引入
    if not any(text.startswith(op[:5]) for op in openings):
        text = random.choice(openings) + '\n\n' + text
    
    # 添加提问和互动
    sentences = text.split('。')
    if len(sentences) > 3:
        # 在中间添加反问
        mid = len(sentences) // 2
        questions = ['你可能会问', '这是为什么呢', '答案可能会让你意外']
        sentences[mid] = random.choice(questions) + '？' + sentences[mid]
    
    text = '。'.join(sentences)
    
    return text

def transform_academic(text):
    """学术风格转换"""
    # 移除口语化表达
    casual_words = {
        '很': '较为',
        '非常': '显著',
        '特别': '尤其',
        '挺': '相对',
        '蛮': '较为',
    }
    
    for casual, formal in casual_words.items():
        text = text.replace(casual, formal)
    
    # 移除emoji
    text = re.sub(r'[😀-🙏🌀-🗿🚀-🛿✀-➿]', '', text)
    
    # 确保逻辑连接词的准确性
    text = text.replace('所以，', '因此，')
    text = text.replace('但是，', '然而，')
    
    # 移除过度情感化表达
    emotional_phrases = ['真的', '确实', '说实话', '没想到']
    for phrase in emotional_phrases:
        text = text.replace(phrase + '，', '')
        text = text.replace(phrase, '')
    
    return text

def transform_literary(text):
    """文艺风格转换"""
    # 添加意象和比喻
    metaphors = [
        ('开始', '如同晨曦初现'),
        ('结束', '宛如落日余晖'),
        ('变化', '恰似流水无痕'),
        ('时间', '岁月如梭'),
    ]
    
    for literal, metaphor in metaphors:
        if literal in text and random.random() < 0.2:
            text = text.replace(literal, metaphor, 1)
    
    # 添加描写性短语
    text = re.sub(r'在([^，。]{2,6})[中里]', r'在\1的光影里', text, count=1)
    
    return text

def transform_casual(text):
    """口语化风格转换"""
    # 移除正式结构
    text = remove_formal_structure(text)
    
    # 替换为口语化表达
    for formal, casual in FORMAL_TO_CASUAL.items():
        text = text.replace(formal, casual)
    
    # 添加口语化连接词
    casual_connectors = ['说实话', '确实', '其实', '不过', '讲真']
    sentences = text.split('。')
    if len(sentences) > 1:
        sentences[0] = random.choice(['你看', '说起来']) + '，' + sentences[0]
    
    text = '。'.join(sentences)
    
    # 添加语气词
    text = re.sub(r'([。！？])', lambda m: random.choice(['', '吧', '呢', '啊']) + m.group(1) if random.random() < 0.2 else m.group(1), text)
    
    # 添加少量emoji
    text = add_emojis(text, density='low')
    
    return text

def shorten_paragraphs(text, max_length=150):
    """缩短段落长度"""
    paragraphs = text.split('\n\n')
    result = []
    
    for para in paragraphs:
        if len(para) > max_length:
            sentences = re.split(r'([。！？])', para)
            chunks = []
            current = ''
            
            for i in range(0, len(sentences) - 1, 2):
                sent = sentences[i] + (sentences[i + 1] if i + 1 < len(sentences) else '')
                if len(current) + len(sent) > max_length and current:
                    chunks.append(current)
                    current = sent
                else:
                    current += sent
            
            if current:
                chunks.append(current)
            
            result.append('\n\n'.join(chunks))
        else:
            result.append(para)
    
    return '\n\n'.join(result)

def apply_style(text, style_name):
    """应用指定风格转换"""
    if style_name not in STYLES:
        print(f'错误: 不支持的风格 "{style_name}"', file=sys.stderr)
        print(f'支持的风格: {", ".join(STYLES.keys())}', file=sys.stderr)
        sys.exit(1)
    
    # 根据风格应用不同的转换
    if style_name == 'xiaohongshu':
        return transform_xiaohongshu(text)
    elif style_name == 'zhihu':
        return transform_zhihu(text)
    elif style_name == 'wechat':
        return transform_wechat(text)
    elif style_name == 'academic':
        return transform_academic(text)
    elif style_name == 'literary':
        return transform_literary(text)
    elif style_name == 'casual':
        return transform_casual(text)
    
    return text

def list_styles():
    """列出所有可用风格"""
    print('可用的文本风格：\n')
    for style_id, config in STYLES.items():
        print(f'  {style_id:15s} - {config["name"]:12s} ({config["description"]})')
    print('\n使用方法: python style_cn.py input.txt --style <风格名>')

def main():
    # 解析参数
    if len(sys.argv) < 2 or '--help' in sys.argv or '-h' in sys.argv:
        print('用法: python style_cn.py <input.txt> --style <风格> [-o output.txt]')
        print('\n示例: python style_cn.py essay.txt --style zhihu -o essay_zhihu.txt')
        print()
        list_styles()
        sys.exit(0)
    
    if sys.argv[1] == '--list':
        list_styles()
        sys.exit(0)
    
    # 读取参数
    input_file = None
    output_file = None
    style = None
    
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == '--style' and i + 1 < len(sys.argv):
            style = sys.argv[i + 1]
            i += 2
        elif arg == '-o' and i + 1 < len(sys.argv):
            output_file = sys.argv[i + 1]
            i += 2
        elif not arg.startswith('-'):
            input_file = arg
            i += 1
        else:
            i += 1
    
    # 检查必要参数
    if not style:
        print('错误: 必须指定 --style 参数', file=sys.stderr)
        list_styles()
        sys.exit(1)
    
    # 读取输入
    if input_file:
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                text = f.read()
        except FileNotFoundError:
            print(f'错误: 文件未找到 {input_file}', file=sys.stderr)
            sys.exit(1)
    else:
        text = sys.stdin.read()
    
    # 应用风格转换
    result = apply_style(text, style)
    
    # 输出
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result)
        print(f'✓ 已保存到 {output_file} (风格: {STYLES[style]["name"]})')
    else:
        print(result)

if __name__ == '__main__':
    main()
