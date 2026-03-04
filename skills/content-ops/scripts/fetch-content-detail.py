#!/usr/bin/env python3
"""
小红书内容详情抓取
基于已获取的列表，批量抓取详情正文
"""

import json
import requests
import time

class XHSMCPClient:
    def __init__(self, base_url="http://localhost:18060"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def get_feed_detail(self, feed_id, xsec_token):
        """获取帖子详情"""
        data = {
            "feed_id": feed_id,
            "xsec_token": xsec_token,
            "load_all_comments": False
        }
        
        resp = self.session.post(
            f"{self.base_url}/api/v1/feeds/detail",
            json=data,
            timeout=60
        )
        return resp.json()

def fetch_details():
    """抓取所有内容的详情"""
    
    # 读取已抓取的结果
    with open('/tmp/xhs_ai_crawled.json', 'r') as f:
        crawl_data = json.load(f)
    
    client = XHSMCPClient()
    
    print("📝 开始抓取正文内容...\n")
    
    detailed_notes = []
    
    for i, note in enumerate(crawl_data['notes'], 1):
        print(f"[{i}/10] 抓取: {note['title'][:30]}...", end=" ", flush=True)
        
        try:
            result = client.get_feed_detail(note['id'], note.get('xsec_token', ''))
            
            if result.get('success'):
                feed_data = result.get('data', {}).get('feed', {})
                note_card = feed_data.get('noteCard', {})
                
                # 提取正文
                desc = note_card.get('desc', '')
                title = note_card.get('displayTitle', note['title'])
                
                detailed_note = {
                    **note,
                    'full_title': title,
                    'description': desc,
                    'images': [img.get('urlDefault', '') for img in note_card.get('imageList', [])[:5]],
                    'tags': note_card.get('tagList', []),
                    'fetch_success': True
                }
                
                detailed_notes.append(detailed_note)
                print(f"✅ 正文 {len(desc)} 字")
            else:
                print(f"❌ {result.get('message', '失败')}")
                detailed_notes.append({**note, 'fetch_success': False})
            
            # 间隔 2 秒，避免触发风控
            time.sleep(2)
            
        except Exception as e:
            print(f"❌ 错误: {e}")
            detailed_notes.append({**note, 'fetch_success': False, 'error': str(e)})
    
    # 保存完整数据
    output = {
        **crawl_data,
        'notes': detailed_notes,
        'detail_fetched_at': time.strftime('%Y-%m-%d %H:%M:%S')
    }
    
    with open('/tmp/xhs_ai_detailed.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    # 统计
    success_count = sum(1 for n in detailed_notes if n.get('fetch_success'))
    print(f"\n{'='*50}")
    print(f"✅ 抓取完成: {success_count}/{len(detailed_notes)} 条成功")
    print(f"📁 数据已保存到 /tmp/xhs_ai_detailed.json")
    print(f"{'='*50}")
    
    # 显示第一条正文预览
    for note in detailed_notes[:2]:
        if note.get('fetch_success'):
            print(f"\n【{note['title'][:30]}...】")
            print(f"正文预览: {note.get('description', '')[:200]}...")
    
    return output

if __name__ == "__main__":
    fetch_details()
