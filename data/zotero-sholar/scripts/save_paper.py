#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyzotero>=1.6.0"]
# ///

import argparse
import os
import sys
from pyzotero import zotero

def main():
    parser = argparse.ArgumentParser(description="保存论文到 Zotero 文献库")
    parser.add_argument("--title", required=True, help="论文标题")
    parser.add_argument("--authors", required=True, help="作者列表，以逗号分隔")
    parser.add_argument("--url", required=True, help="论文链接（用于查重）")
    parser.add_argument("--abstract", help="论文摘要")
    parser.add_argument("--summary", help="AI 生成的摘要")
    parser.add_argument("--tags", help="标签列表，以逗号分隔")
    
    args = parser.parse_args()
    
    library_id = None
    api_key = None

    zotero_creds = os.environ.get('ZOTERO_CREDENTIALS')
    if zotero_creds and ':' in zotero_creds:
        try:
            parts = zotero_creds.strip().split(':')
            if len(parts) == 2:
                library_id = parts[0].strip()
                api_key = parts[1].strip()
        except:
            pass

    library_type = 'user' # 默认使用个人文献库
    
    if not library_id or not api_key:
        print("错误：需要 Zotero 凭据。", file=sys.stderr)
        print("请设置 ZOTERO_CREDENTIALS='userID:apiKey'（用于 UI 配置）", file=sys.stderr)
        sys.exit(1)
        
    try:
        zot = zotero.Zotero(library_id, library_type, api_key)
        
        # 通过 URL 检查是否已存在
        # 使用搜索查询匹配 URL
        print(f"正在检查是否已存在该条目：{args.url}...")
        items = zot.items(q=args.url, limit=1)
        
        if items:
            print(f"该条目已存在：{items[0].get('data', {}).get('title', '未知')}")
            # 暂时跳过更新，避免覆盖用户数据
            print(f"Zotero 链接：https://www.zotero.org/{library_id}/items/{items[0]['key']}")
            return

        # 创建新条目
        template = zot.item_template('journalArticle')
        template['title'] = args.title
        
        # 格式化作者信息
        creators = []
        for author in args.authors.split(','):
            name_parts = author.strip().split(' ')
            if len(name_parts) > 1:
                creators.append({'creatorType': 'author', 'firstName': ' '.join(name_parts[:-1]), 'lastName': name_parts[-1]})
            else:
                creators.append({'creatorType': 'author', 'lastName': author.strip(), 'firstName': ''})
        template['creators'] = creators
        
        template['url'] = args.url
        if args.abstract:
            template['abstractNote'] = args.abstract
            
        # 添加标签
        if args.tags:
            template['tags'] = [{'tag': t.strip()} for t in args.tags.split(',')]

        print(f"正在创建条目：{args.title}...")
        resp = zot.create_items([template])
        
        if resp.get('successful'):
            new_item = resp['successful']['0']
            item_key = new_item['key']
            print(f"条目创建成功！")
            
            # 将摘要添加为笔记
            if args.summary:
                print("正在添加摘要笔记...")
                note_template = zot.item_template('note')
                note_template['note'] = f"<h3>AI 摘要</h3><p>{args.summary}</p>"
                note_template['parentItem'] = item_key
                zot.create_items([note_template])
                print("笔记已添加。")
            
            # 下载并附加 PDF
            if 'arxiv.org' in args.url:
                try:
                    import urllib.request
                    import tempfile
                    
                    # 将摘要链接转换为 PDF 链接
                    pdf_url = args.url.replace('/abs/', '/pdf/')
                    if not pdf_url.endswith('.pdf'):
                        pdf_url += '.pdf'
                        
                    print(f"正在下载 PDF...")
                    
                    # 设置 User-Agent 以支持下载
                    opener = urllib.request.build_opener()
                    opener.addheaders = [('User-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Chrome/120.0.0.0')]
                    urllib.request.install_opener(opener)
                    
                    # 创建安全的文件名
                    safe_title = "".join(c for c in args.title if c.isalnum() or c in (" ", "-", "_")).strip()
                    safe_title = safe_title[:50] # 限制长度
                    safe_filename = f"{safe_title}.pdf"
                    
                    # 使用临时目录，但指定文件名
                    with tempfile.TemporaryDirectory() as td:
                        pdf_path = os.path.join(td, safe_filename)
                        urllib.request.urlretrieve(pdf_url, pdf_path)
                        
                        print(f"正在上传 PDF 附件（{safe_filename}）...")
                        zot.attachment_simple([pdf_path], item_key)
                        print("PDF 已附加。")

                except Exception as e:
                    print(f"附加 PDF 失败：{e}", file=sys.stderr)
            
            print("注意: 请在 Zotero 客户端点击 '同步' (Sync) 按钮以获取云端 PDF 文件。")
            print("         如果是 Web API 写入，本地客户端必须同步才能看到附件内容。")
            
        else:
            print(f"创建条目失败：{resp}", file=sys.stderr)
            sys.exit(1)

    except Exception as e:
        print(f"错误：{e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
