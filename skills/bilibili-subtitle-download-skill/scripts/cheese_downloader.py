import asyncio
import os
import sys
import json
from json import loads, dumps
from bilibili_api import Credential, cheese, login_v2
from qrcode import QRCode

CHARS_PER_CHUNK = 100000

async def login_with_qrcode_picture():
    qr = login_v2.QrCodeLogin(platform=login_v2.QrCodeLoginChannel.WEB)
    await qr.generate_qrcode()
    
    qr_path = os.path.join(os.getcwd(), "bilibili_login_qr.png")
    
    from qrcode import QRCode
    url = getattr(qr, '_QrCodeLogin__qr_link', None)
    if not url:
        raise Exception("无法获取二维码 URL 喵！")
    
    qr_gen = QRCode()
    qr_gen.add_data(url)
    qr_gen.make(fit=True)
    img = qr_gen.make_image(fill_color="black", back_color="white")
    img.save(qr_path)
    
    print(f"QR_CODE_PATH:{qr_path}")
    print("请使用B站APP扫描二维码图片进行登录喵！")
    sys.stdout.flush()

    while not qr.has_done():
        state = await qr.check_state()
        print(f"STATUS:{state}")
        if "SCAN" in str(state):
            print("STATUS:二维码已扫描喵，请在手机上确认喵！")
        elif "CONFIRM" in str(state):
            print("STATUS:已确认登录喵！")
        elif "EXPIRE" in str(state):
            print("STATUS:二维码已过期喵！")
            return None
        await asyncio.sleep(2)

    credential = qr.get_credential()
    return credential


def save_subtitle_chunks(subtitle_content, ep_id, title=""):
    """将字幕内容切分并保存到文件"""
    if not subtitle_content:
        return None
    
    body = subtitle_content.get('body', [])
    full_text = "\n".join([b.get('content', '') for b in body])
    
    if not full_text:
        return None
    
    total_chars = len(full_text)
    output_dir = os.path.join(os.getcwd(), 'bili_temp', ep_id)
    os.makedirs(output_dir, exist_ok=True)
    
    chunks = []
    for i in range(0, total_chars, CHARS_PER_CHUNK):
        chunk_content = full_text[i : i + CHARS_PER_CHUNK]
        chunk_file = os.path.join(output_dir, f"chunk_{i // CHARS_PER_CHUNK}.txt")
        with open(chunk_file, 'w', encoding='utf-8') as f:
            f.write(chunk_content)
        chunks.append(chunk_file)
    
    return {
        "ep_id": ep_id,
        "title": title,
        "total_chars": total_chars,
        "chunks": chunks
    }

async def main(target_id):
    # 尝试加载现有凭证
    session_path = 'bilibili_cheese_session.json'
    credential = None
    
    if os.path.exists(session_path):
        with open(session_path, 'r', encoding='utf-8') as f:
            cookies = loads(f.read())
            credential = Credential(
                sessdata=cookies.get('SESSDATA', ''),
                bili_jct=cookies.get('bili_jct', ''),
                buvid3=cookies.get('buvid3', '')
            )
        if not await credential.check_valid():
            credential = await login_with_qrcode_picture()
    else:
        credential = await login_with_qrcode_picture()

    if not credential:
        print("ERROR:登录失败或取消喵。")
        return

    # 保存凭证
    with open(session_path, 'w', encoding='utf-8') as f:
        f.write(dumps(credential.get_cookies(), indent=4, ensure_ascii=False))

    import aiohttp
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Referer": "https://www.bilibili.com/"
    }
    cookies = credential.get_cookies()

    try:
        if target_id.startswith('ep'):
            ep_id_num = int(target_id[2:])
            ep = cheese.CheeseVideo(epid=ep_id_num, credential=credential)
            meta = await ep.get_meta()
            episode_title = meta.get('title', '')
            print(f"EPISODE_TITLE:{episode_title}")
            
            aid = meta.get('aid')
            cid = meta.get('cid')
            
            if not cid:
                detail_api = "https://api.bilibili.com/pugv/view/web/episode"
                async with aiohttp.ClientSession(cookies=cookies) as session:
                    async with session.get(detail_api, params={'ep_id': ep_id_num}, headers=headers) as r:
                        detail_resp = await r.json()
                if detail_resp.get('code') == 0:
                    data = detail_resp.get('data', {})
                    aid = aid or data.get('aid')
                    cid = cid or data.get('cid')

            if cid:
                print(f"DEBUG: FOUND AID={aid}, CID={cid}")
                player_api = "https://api.bilibili.com/x/player/wbi/v2"
                params = {'cid': cid}
                if aid: params['aid'] = aid
                
                async with aiohttp.ClientSession(cookies=cookies) as session:
                    async with session.get(player_api, params=params, headers=headers) as r:
                        player_resp = await r.json()
                
                if player_resp.get('code') == 0 and 'subtitle' in player_resp.get('data', {}):
                    subtitles = player_resp['data']['subtitle'].get('subtitles', [])
                    if subtitles:
                        target_url = None
                        for s in subtitles:
                            if 'zh' in s.get('lan', ''):
                                target_url = s['subtitle_url']
                                break
                        if not target_url:
                            target_url = subtitles[0].get('subtitle_url', '')
                        
                        if target_url:
                            if target_url.startswith('//'): 
                                target_url = "https:" + target_url
                            async with aiohttp.ClientSession() as session:
                                async with session.get(target_url) as sub_r:
                                    sub_content = await sub_r.json()
                                    result = save_subtitle_chunks(sub_content, target_id, episode_title)
                                    if result:
                                        print(f"[*] Success. Total chunks: {len(result['chunks'])}")
                                        print("RESULT_JSON:" + json.dumps(result))
                                    else:
                                        print("ERROR: 字幕内容为空喵。")
                        else:
                            print("SUBTITLES_INFO:未找到有效字幕URL喵。")
                    else:
                        print("SUBTITLES_INFO:字幕列表为空喵。")
                else:
                    print(f"SUBTITLES_INFO:未发现字幕信息喵 (Code: {player_resp.get('code')})。")
            else:
                print("SUBTITLES_INFO:无法确定 CID，无法获取字幕喵。")

        elif target_id.startswith('ss') or target_id.isdigit():
            season_id = int(target_id[2:]) if target_id.startswith('ss') else int(target_id)
            cheese_list = cheese.CheeseList(season_id=season_id, credential=credential)
            meta = await cheese_list.get_meta()
            print(f"COURSE_TITLE:{meta.get('title', 'Unknown')}")
            episodes = await cheese_list.get_list()
            print(f"TOTAL_EPISODES:{len(episodes)}")
            print("=" * 50)
            print("课程剧集列表 (请使用 EP_ID 获取具体字幕):")
            print("=" * 50)
            for i, ep in enumerate(episodes, 1):
                ep_meta = await ep.get_meta()
                print(f"  {i}. {ep_meta.get('title')} (ID: ep{ep.get_epid()})")
            print("=" * 50)
    except Exception as e:
        print(f"ERROR:处理 {target_id} 时出错喵: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 cheese_downloader.py <ID>")
    else:
        asyncio.run(main(sys.argv[1]))
