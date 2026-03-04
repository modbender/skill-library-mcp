#!/usr/bin/env python3
"""温和的输入验证器 - 检测明显恶意的内容

原则：
1. 只检测明显恶意内容，不过度限制
2. 误报比漏报好 (宁可多报，不可漏报)
3. 警告而非阻止，让 Agent 决定

使用场景：
- 网页抓取内容
- 用户上传文件
- RSS 订阅内容
- 外部 API 响应
"""

import re
import sys

# 明显恶意的模式 (误报率低)
DANGEROUS_PATTERNS = [
    # 直接删除命令
    (r'rm\s+(-rf|--recursive)\s+(/|~|\*)', '删除命令'),
    (r'del\s+/[a-z]', '删除命令 (Windows)'),
    (r'shred\s+-[zn]', '安全删除'),
    
    # 权限提升
    (r'sudo\s+(rm|chmod|chown)', '提权命令'),
    (r'su\s+-\s+root', '切换 root'),
    
    # 下载执行
    (r'curl\s+.*\|\s*(ba)?sh', '下载执行'),
    (r'wget\s+.*\|\s*(ba)?sh', '下载执行'),
    (r'curl\s+.*-o\s+/tmp/.*;\s*(ba)?sh', '下载执行'),
    
    # 覆盖系统文件
    (r'echo\s+.*>\s+/etc/', '覆盖系统配置'),
    (r'echo\s+.*>\s+/bin/', '覆盖二进制文件'),
    
    # 反弹 shell
    (r'/dev/tcp/', '反弹 shell'),
    (r'nc\s+-e\s+(ba)?sh', '反弹 shell'),
    
    # 挖矿脚本
    (r'xmrig', '挖矿脚本'),
    (r'cryptonight', '挖矿算法'),
]

# 可疑但不阻止的模式 (仅警告)
SUSPICIOUS_PATTERNS = [
    (r'ignore\s+(previous|all)\s+(instructions|rules)', '忽略指令尝试'),
    (r'forget\s+(all|everything)', '遗忘规则尝试'),
    (r'you\s+are\s+now\s+(unrestricted|free)', '越狱尝试'),
    (r'disable\s+(safety|security)', '禁用安全'),
    
    # Bot 安全相关 (新增)
    (r'execute.*command', '执行命令请求'),
    (r'run.*script', '运行脚本请求'),
    (r'provide.*credential', '索取凭证'),
    (r'click.*link', '点击链接诱导'),
    (r'download.*file', '下载文件请求'),
    (r'send.*password', '索取密码'),
    (r'api.*key', '索取 API 密钥'),
    (r'token.*secret', '索取令牌'),
]


def validate_input(text: str, strict: bool = False) -> dict:
    """
    验证输入内容
    
    Args:
        text: 要验证的文本
        strict: 严格模式 (默认 False，温和模式)
    
    Returns:
        {
            "safe": bool,
            "warnings": list,
            "dangerous": list
        }
    """
    result = {
        "safe": True,
        "warnings": [],
        "dangerous": []
    }
    
    text_lower = text.lower()
    
    # 检查明显恶意内容
    for pattern, name in DANGEROUS_PATTERNS:
        if re.search(pattern, text_lower):
            result["safe"] = False
            result["dangerous"].append(f"🔴 {name}")
    
    # 检查可疑内容 (仅警告)
    if not result["dangerous"]:  # 只有没有危险内容时才检查可疑
        for pattern, name in SUSPICIOUS_PATTERNS:
            if re.search(pattern, text_lower):
                result["warnings"].append(f"🟡 {name}")
    
    return result


def main():
    if len(sys.argv) < 2:
        print("用法：input-validator <text>")
        print("       input-validator --file <filename>")
        sys.exit(1)
    
    # 从文件读取
    if sys.argv[1] == "--file":
        if len(sys.argv) < 3:
            print("错误：需要指定文件名")
            sys.exit(1)
        
        filename = sys.argv[2]
        try:
            with open(filename, 'r') as f:
                text = f.read()
        except Exception as e:
            print(f"错误：无法读取文件 - {e}")
            sys.exit(1)
    else:
        # 从命令行读取
        text = " ".join(sys.argv[1:])
    
    # 验证
    result = validate_input(text)
    
    # 输出结果
    if result["dangerous"]:
        print("🔴 检测到危险内容:")
        for item in result["dangerous"]:
            print(f"   {item}")
        print("\n建议：不要执行此内容中的命令")
        sys.exit(1)
    
    elif result["warnings"]:
        print("🟡 检测到可疑内容:")
        for item in result["warnings"]:
            print(f"   {item}")
        print("\n建议：谨慎处理此内容")
        sys.exit(0)  # 警告但不阻止
    
    else:
        print("✅ 输入内容安全")
        sys.exit(0)


if __name__ == "__main__":
    main()
