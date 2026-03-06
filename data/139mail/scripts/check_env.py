#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
139mail skill 环境检查脚本
帮助新人检查安装环境是否就绪
"""
import sys
import ssl

def check_python_version():
    """检查Python版本"""
    version = sys.version_info
    print(f"Python版本: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("  [FAIL] Python版本过低，需要 >= 3.8")
        return False
    print("  [OK] Python版本符合要求")
    return True

def check_openssl():
    """检查OpenSSL版本"""
    openssl_version = ssl.OPENSSL_VERSION
    print(f"\nOpenSSL版本: {openssl_version}")
    
    # 提取版本号
    try:
        import re
        match = re.search(r'(\d+)\.(\d+)\.(\d+)', openssl_version)
        if match:
            major, minor, patch = map(int, match.groups())
            if major < 1 or (major == 1 and minor < 1):
                print("  [FAIL] OpenSSL版本过低，需要 >= 1.1.1")
                return False
    except:
        pass
    
    print("  [OK] OpenSSL版本符合要求")
    return True

def check_imapclient():
    """检查imapclient安装"""
    print("\n检查 imapclient 模块...")
    try:
        import imapclient
        print(f"  [OK] imapclient 已安装 (版本: {imapclient.__version__})")
        return True
    except ImportError:
        print("  [FAIL] imapclient 未安装")
        print("  请运行: pip install imapclient")
        return False

def check_ssl_compatibility():
    """测试SSL兼容性"""
    print("\n测试SSL兼容性...")
    try:
        # 尝试创建兼容139邮箱的SSL上下文
        ssl_context = ssl._create_unverified_context()
        ssl_context.set_ciphers('DEFAULT@SECLEVEL=1')
        print("  [OK] SSL兼容模式可用")
        return True
    except Exception as e:
        print(f"  [FAIL] SSL配置失败: {e}")
        return False

def check_config():
    """检查配置文件"""
    print("\n检查配置文件...")
    import os
    config_file = os.path.join(os.path.dirname(__file__), '..', 'config', '139mail.conf')
    
    if not os.path.exists(config_file):
        print(f"  [WARN] 配置文件不存在")
        print("  请先运行: python scripts/config_manager.py save --username <账号> --password <授权码>")
        return False
    
    try:
        import json
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        if config.get('username') and config.get('password'):
            # 隐藏密码显示
            username = config['username']
            print(f"  [OK] 配置文件存在")
            print(f"  账号: {username}")
            return True
        else:
            print("  [WARN] 配置文件不完整")
            return False
    except Exception as e:
        print(f"  [FAIL] 配置文件读取失败: {e}")
        return False

def test_connection():
    """测试连接（可选）"""
    print("\n测试连接139邮箱（需要配置完成）...")
    
    import os
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    try:
        from config_manager import load_config
        config = load_config()
        
        if not config:
            print("  [SKIP] 跳过：未配置账号")
            return None
        
        import imapclient
        ssl_context = ssl._create_unverified_context()
        ssl_context.set_ciphers('DEFAULT@SECLEVEL=1')
        
        with imapclient.IMAPClient(
            config['imap_server'],
            port=config['imap_port'],
            ssl=True,
            ssl_context=ssl_context,
            timeout=10
        ) as server:
            server.login(config['username'], config['password'])
            print(f"  [OK] 连接成功！登录账号: {config['username']}")
            return True
            
    except Exception as e:
        print(f"  [FAIL] 连接失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("139mail Skill 环境检查")
    print("=" * 60)
    
    results = []
    
    # 基础环境检查
    results.append(("Python版本", check_python_version()))
    results.append(("OpenSSL版本", check_openssl()))
    results.append(("imapclient模块", check_imapclient()))
    results.append(("SSL兼容性", check_ssl_compatibility()))
    results.append(("配置文件", check_config()))
    
    # 可选的连接测试
    connection_result = test_connection()
    if connection_result is not None:
        results.append(("连接测试", connection_result))
    
    # 总结
    print("\n" + "=" * 60)
    print("检查结果汇总")
    print("=" * 60)
    
    all_passed = True
    for name, result in results:
        status = "[OK] 通过" if result else "[FAIL] 失败"
        if result is None:
            status = "[SKIP] 跳过"
        print(f"{name:20s} {status}")
        if result is False:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n[SUCCESS] 所有检查通过！可以开始使用139mail skill了。")
        print("\n常用命令：")
        print("  python scripts/check_mail.py --limit 5    # 查看最新邮件")
        print("  python scripts/check_mail.py --unread     # 查看未读邮件")
        return 0
    else:
        print("\n[WARNING] 部分检查未通过，请根据上方提示修复问题。")
        print("\n如需帮助，请参考 SKILL.md 文档的故障排除部分。")
        return 1

if __name__ == '__main__':
    exit(main())
