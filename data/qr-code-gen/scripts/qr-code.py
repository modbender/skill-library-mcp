#!/usr/bin/env python3
"""
QR Code Generator
生成二维码图片
支持文本、URL、WiFi、名片等多种格式
"""

import sys
import os

def check_qrcode_module():
    """检查 qrcode 模块是否安装"""
    try:
        import qrcode
        return True
    except ImportError:
        return False

def generate_qr(text, output_path=None, box_size=10, border=4):
    """生成二维码"""
    try:
        import qrcode
        from PIL import Image
        
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=box_size,
            border=border,
        )
        qr.add_data(text)
        qr.make(fit=True)
        
        # 创建图像
        img = qr.make_image(fill_color="black", back_color="white")
        
        # 保存或显示
        if output_path:
            img.save(output_path)
            return output_path
        else:
            # 默认保存到临时目录
            default_path = os.path.expanduser("~/qrcode_output.png")
            img.save(default_path)
            return default_path
            
    except Exception as e:
        print(f"生成失败: {e}")
        return None

def generate_wifi_qr(ssid, password, security="WPA", hidden=False):
    """生成 WiFi 连接二维码"""
    # WiFi QR Code 格式: WIFI:T:<security>;S:<ssid>;P:<password>;H:<hidden>;;
    hidden_flag = "true" if hidden else "false"
    wifi_string = f"WIFI:T:{security};S:{ssid};P:{password};H:{hidden_flag};;"
    return wifi_string

def generate_vcard(name, phone=None, email=None, org=None, title=None, url=None):
    """生成名片二维码 (vCard 格式)"""
    vcard = ["BEGIN:VCARD", "VERSION:3.0"]
    vcard.append(f"FN:{name}")
    vcard.append(f"N:{name};;;")
    
    if phone:
        vcard.append(f"TEL:{phone}")
    if email:
        vcard.append(f"EMAIL:{email}")
    if org:
        vcard.append(f"ORG:{org}")
    if title:
        vcard.append(f"TITLE:{title}")
    if url:
        vcard.append(f"URL:{url}")
    
    vcard.append("END:VCARD")
    return "\n".join(vcard)

def main():
    if len(sys.argv) < 2:
        print("用法: qr-code <command> [args]")
        print("")
        print("命令:")
        print("  qr-code text <内容> [输出路径]     生成文本/URL二维码")
        print("  qr-code wifi <SSID> <密码> [输出]  生成WiFi连接二维码")
        print("  qr-code vcard [参数...] [输出]      生成名片二维码")
        print("")
        print("示例:")
        print('  qr-code text "Hello World"')
        print('  qr-code text "https://example.com" ./myqr.png')
        print('  qr-code wifi "MyHomeWiFi" "password123"')
        print('  qr-code vcard --name "张三" --phone "13800138000" --email "zhang@example.com"')
        print("")
        print("依赖安装:")
        print("  pip3 install qrcode[pil]")
        return 1

    # 检查依赖
    if not check_qrcode_module():
        print("❌ 缺少 qrcode 模块")
        print("")
        print("请安装依赖:")
        print("  pip3 install qrcode[pil]")
        print("")
        print("或:")
        print("  sudo apt-get install python3-qrcode")
        return 1

    command = sys.argv[1]

    if command == "text":
        if len(sys.argv) < 3:
            print("错误: 请提供文本内容")
            return 1
        
        text = sys.argv[2]
        output = sys.argv[3] if len(sys.argv) > 3 else None
        
        result = generate_qr(text, output)
        if result:
            print(f"✅ 二维码已生成: {result}")
            print(f"内容: {text[:50]}{'...' if len(text) > 50 else ''}")
        else:
            print("❌ 生成失败")
            return 1

    elif command == "wifi":
        if len(sys.argv) < 4:
            print("错误: 请提供 WiFi 名称和密码")
            print("用法: qr-code wifi <SSID> <密码> [输出路径]")
            return 1
        
        ssid = sys.argv[2]
        password = sys.argv[3]
        output = sys.argv[4] if len(sys.argv) > 4 else None
        
        wifi_string = generate_wifi_qr(ssid, password)
        result = generate_qr(wifi_string, output)
        
        if result:
            print(f"✅ WiFi 二维码已生成: {result}")
            print(f"SSID: {ssid}")
            print("手机扫描即可自动连接WiFi")
        else:
            print("❌ 生成失败")
            return 1

    elif command == "vcard":
        # 解析参数
        import argparse
        
        parser = argparse.ArgumentParser(description='生成名片二维码', prog='qr-code vcard')
        parser.add_argument('--name', '-n', required=True, help='姓名')
        parser.add_argument('--phone', '-p', help='电话')
        parser.add_argument('--email', '-e', help='邮箱')
        parser.add_argument('--org', '-o', help='公司/组织')
        parser.add_argument('--title', '-t', help='职位')
        parser.add_argument('--url', '-u', help='网址')
        parser.add_argument('output', nargs='?', help='输出路径')
        
        # 移除 'qr-code vcard' 后解析剩余参数
        try:
            args = parser.parse_args(sys.argv[2:])
        except SystemExit:
            return 1
        
        vcard_data = generate_vcard(
            name=args.name,
            phone=args.phone,
            email=args.email,
            org=args.org,
            title=args.title,
            url=args.url
        )
        
        result = generate_qr(vcard_data, args.output)
        
        if result:
            print(f"✅ 名片二维码已生成: {result}")
            print(f"姓名: {args.name}")
            if args.phone:
                print(f"电话: {args.phone}")
            if args.email:
                print(f"邮箱: {args.email}")
            print("手机扫描即可添加到通讯录")
        else:
            print("❌ 生成失败")
            return 1

    else:
        print(f"未知命令: {command}")
        print("使用 'qr-code' 查看帮助")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
