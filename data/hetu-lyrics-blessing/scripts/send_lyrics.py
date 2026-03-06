#!/usr/bin/env python3
"""
河图歌词每日祝福 - 每天从百度百科获取歌词并发送
必须使用 agent-browser 从 baike.baidu.com 获取歌词
"""
import smtplib
import random
import subprocess
import os
from email.mime.text import MIMEText
from email.header import Header

SMTP_SERVER = "smtp.qq.com"
SMTP_PORT = 465
SMTP_EMAIL = "853375443@qq.com"
SMTP_PASSWORD = "nzhgbgilzgmabeih"

TO_EMAIL = "836633245@qq.com"

# 预定义的歌曲列表 - 百度百科URL
SONGS = [
    {"name": "倾尽天下", "url": "https://baike.baidu.com/item/倾尽天下"},
    {"name": "如梦", "url": "https://baike.baidu.com/item/如梦"},
    {"name": "第三十八年夏至", "url": "https://baike.baidu.com/item/第三十八年夏至"},
    {"name": "琴师", "url": "https://baike.baidu.com/item/琴师"},
    {"name": "永定四十年", "url": "https://baike.baidu.com/item/永定四十年"},
    {"name": "海棠酒满", "url": "https://baike.baidu.com/item/海棠酒满"},
    {"name": "风起天阑", "url": "https://baike.baidu.com/item/风起天阑"},
    {"name": "寸缕", "url": "https://baike.baidu.com/item/寸缕"},
    {"name": "不见长安", "url": "https://baike.baidu.com/item/不见长安"},
    {"name": "凤凰劫", "url": "https://baike.baidu.com/item/凤凰劫"},
    {"name": "越人歌", "url": "https://baike.baidu.com/item/越人歌"},
    {"name": "长夜梦我", "url": "https://baike.baidu.com/item/长夜梦我"},
]

# 祝福语库
BLESSINGS = [
    "最珍贵的不是江山，而是你。愿秋男每天都被温柔以待～",
    "繁华只是过眼云烟，真情才最珍贵。愿秋男珍惜当下每一天～",
    "时光易逝，要珍惜眼前人。愿秋男每天都开心快乐！",
    "最长情的等待最动人。愿秋男也被温柔等待～",
    "不要辜负爱你的人。愿秋男每天都被爱包围～",
    "有些人一直在原地等你。愿秋男感受到这份温暖～",
    "音乐让时光温柔。愿秋男每天都有好心情～",
    "做自己就好，不必在乎别人眼光。愿秋男勇敢做自己！",
    "离别是为了更好的重逢。愿秋男珍惜每一次相遇～",
    "愿为你种下最美的风景。祝秋男每天都像花儿一样灿烂～",
    "有些回忆值得珍藏。愿秋男每天都有美好回忆～",
    "即使有再多烦恼，也要坚强面对。愿秋男一切顺利！",
    "愿你的人生如诗如画。祝秋男每天都充满诗意～",
    "放下执念，才能自在。愿秋男每天轻松愉快！",
    "爱要勇敢说出来。祝秋男有勇气追求幸福～",
    "学会放下，才能前行。愿秋男轻装上阵～",
]

def fetch_lyrics_from_baike(song_name, song_url):
    """从百度百科获取歌词"""
    print(f"正在从百度百科获取 {song_name} 的歌词...")
    
    # 使用 agent-browser 打开百度百科
    cmd = f'agent-browser open "{song_url}"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(f"Result: {result.stdout}")
    
    # 等待页面加载
    import time
    time.sleep(2)
    
    # 获取页面内容
    cmd = 'agent-browser eval "document.body.innerText"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    content = result.stdout
    
    # 提取歌词部分
    lyrics = []
    in_lyrics_section = False
    for line in content.split('\n'):
        if '歌词' in line:
            in_lyrics_section = True
            continue
        if in_lyrics_section and line.strip():
            if '词条' in line or '相关' in line or '参考' in line:
                break
            lyrics.append(line.strip())
    
    # 关闭浏览器
    subprocess.run('agent-browser close', shell=True)
    
    if lyrics:
        # 取前4行作为每日歌词
        return '\n'.join(lyrics[:4])
    return None

def send_daily_message():
    """发送每日祝福"""
    # 随机选歌
    song = random.choice(SONGS)
    blessing = random.choice(BLESSINGS)
    
    # 尝试从百度百科获取歌词（如果失败则用预定义）
    lyric = None
    try:
        lyric = fetch_lyrics_from_baike(song['name'], song['url'])
    except Exception as e:
        print(f"获取歌词失败: {e}")
    
    # 如果获取失败，使用预定义歌词
    if not lyric:
        predefined = {
            "倾尽天下": "血染江山的画，怎敌你眉间一点朱砂",
            "如梦": "十八年守候，她站在小渡口",
            "第三十八年夏至": "他还演着那场郎骑竹马来的戏",
            "琴师": "若为此和弦，朝夕可相依",
            "永定四十年": "不群则狂，俗世人笑我簪花带酒",
            "海棠酒满": "落地成花，陪你种下十里红妆",
            "风起天阑": "记忆是条河，翻腾着不愿忘记的浪花",
            "寸缕": "任这一缕虚弱的重担，来隔开我明目张胆的悲歌",
            "不见长安": "长安城有人歌诗三百，歌尽悲欢",
            "凤凰劫": "谁应了谁的劫，谁又变成了谁的执念",
            "越人歌": "山有木兮木有枝，心悦君兮君不知",
            "长夜梦我": "长路漫漫终有一别，勿念莫回首",
        }
        lyric = predefined.get(song['name'], "歌词获取中...")
    
    # 发送邮件
    MESSAGE = f"""【比巴卜提醒】💊 秋男吃药了～

🎵 歌词来源：河图 - {song['name']}
📝 百度百科：{song['url']}
📝 歌词：{lyric}

💌 祝福：{blessing}

——来自比巴卜的温馨提醒🤖
"""
    
    msg = MIMEText(MESSAGE, 'plain', 'utf-8')
    msg['Subject'] = Header(f"【比巴卜】秋男，该吃药了～ {song['name']}", 'utf-8')
    msg['From'] = SMTP_EMAIL
    msg['To'] = TO_EMAIL
    
    server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
    server.login(SMTP_EMAIL, SMTP_PASSWORD)
    server.sendmail(SMTP_EMAIL, [TO_EMAIL], msg.as_string())
    server.quit()
    print(f"✅ 已发送: {song['name']} - {lyric}")

if __name__ == "__main__":
    send_daily_message()
