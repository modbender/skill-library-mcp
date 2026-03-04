#!/usr/bin/env python3
"""
Password Generator
安全的密码生成器
支持多种字符集和复杂度选项
"""

import sys
import random
import string
import secrets

def generate_password(length=16, use_upper=True, use_lower=True, use_digits=True, use_symbols=True, exclude_ambiguous=False, exclude_similar=False):
    """生成密码"""
    
    if length < 4:
        return {"error": "密码长度至少为4位"}
    
    if length > 128:
        return {"error": "密码长度不能超过128位"}
    
    # 字符集
    chars = ""
    
    if use_lower:
        if exclude_ambiguous or exclude_similar:
            chars += "abcdefghijkmnpqrstuvwxyz"  # 排除l,o
        else:
            chars += string.ascii_lowercase
    
    if use_upper:
        if exclude_ambiguous or exclude_similar:
            chars += "ABCDEFGHJKLMNPQRSTUVWXYZ"  # 排除I,O
        else:
            chars += string.ascii_uppercase
    
    if use_digits:
        if exclude_ambiguous or exclude_similar:
            chars += "23456789"  # 排除0,1
        else:
            chars += string.digits
    
    if use_symbols:
        if exclude_ambiguous:
            chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"
        else:
            chars += "!@#$%^&*()_+-=[]{}|;:,.<>?~`"
    
    if not chars:
        return {"error": "请至少选择一种字符类型"}
    
    # 生成密码
    password = ''.join(secrets.choice(chars) for _ in range(length))
    
    # 计算强度
    strength = calculate_strength(password)
    
    return {
        "password": password,
        "length": length,
        "strength": strength,
        "charset": chars
    }

def calculate_strength(password):
    """计算密码强度"""
    score = 0
    
    # 长度分
    if len(password) >= 8:
        score += 1
    if len(password) >= 12:
        score += 1
    if len(password) >= 16:
        score += 1
    if len(password) >= 20:
        score += 1
    
    # 字符类型分
    if any(c.islower() for c in password):
        score += 1
    if any(c.isupper() for c in password):
        score += 1
    if any(c.isdigit() for c in password):
        score += 1
    if any(not c.isalnum() for c in password):
        score += 1
    
    # 强度等级
    if score < 4:
        return "弱"
    elif score < 6:
        return "中"
    elif score < 8:
        return "强"
    else:
        return "极强"

def generate_passphrase(word_count=4, separator="-"):
    """生成记忆密码（密码短语）"""
    # 简单单词库
    words = [
        "apple", "banana", "cherry", "dragon", "eagle", "forest", "garden", "house",
        "island", "jungle", "kitchen", "laptop", "mountain", "notebook", "orange",
        "pencil", "queen", "river", "sunset", "table", "umbrella", "violet",
        "window", "yellow", "zebra", "anchor", "bridge", "castle", "diamond",
        "energy", "flower", "guitar", "hammer", "internet", "jacket", "key",
        "laptop", "music", "nature", "ocean", "piano", "quiet", "rocket",
        "soccer", "train", "universe", "victory", "winter", "xylophone", "youth",
        "zeppelin", "alpha", "beta", "gamma", "delta", "epsilon", "zeta", "theta",
        "kappa", "lambda", "mu", "nu", "xi", "omicron", "pi", "rho", "sigma",
        "tau", "upsilon", "phi", "chi", "psi", "omega"
    ]
    
    selected_words = [secrets.choice(words) for _ in range(word_count)]
    passphrase = separator.join(selected_words)
    
    return {
        "password": passphrase,
        "length": len(passphrase),
        "strength": "中",
        "type": "passphrase"
    }

def analyze_password(password):
    """分析密码"""
    strength = calculate_strength(password)
    
    analysis = {
        "length": len(password),
        "strength": strength,
        "has_lowercase": any(c.islower() for c in password),
        "has_uppercase": any(c.isupper() for c in password),
        "has_digits": any(c.isdigit() for c in password),
        "has_symbols": any(not c.isalnum() for c in password),
        "charset_size": len(set(password))
    }
    
    return analysis

def main():
    if len(sys.argv) < 2:
        print("用法: password-gen <command> [options]")
        print("")
        print("命令:")
        print("  password-gen generate [长度] [选项]    生成随机密码")
        print("  password-gen passphrase [词数]         生成密码短语")
        print("  password-gen analyze <密码>            分析密码强度")
        print("  password-gen list                       显示字符集")
        print("")
        print("选项:")
        print("  --no-upper          不使用大写字母")
        print("  --no-lower          不使用小写字母")
        print("  --no-digits         不使用数字")
        print("  --no-symbols        不使用符号")
        print("  --exclude-ambiguous 排除易混淆字符(0,O,l,I)")
        print("  --exclude-similar   排除相似字符")
        print("")
        print("示例:")
        print("  password-gen generate")
        print("  password-gen generate 20")
        print("  password-gen generate 12 --no-symbols")
        print("  password-gen passphrase 6")
        print("  password-gen analyze 'MyPassword123!'")
        return 1

    command = sys.argv[1]

    if command == "generate":
        length = 16
        use_upper = True
        use_lower = True
        use_digits = True
        use_symbols = True
        exclude_ambiguous = False
        exclude_similar = False
        
        # 解析参数
        i = 2
        while i < len(sys.argv):
            arg = sys.argv[i]
            
            if arg.isdigit():
                length = int(arg)
            elif arg == "--no-upper":
                use_upper = False
            elif arg == "--no-lower":
                use_lower = False
            elif arg == "--no-digits":
                use_digits = False
            elif arg == "--no-symbols":
                use_symbols = False
            elif arg == "--exclude-ambiguous":
                exclude_ambiguous = True
            elif arg == "--exclude-similar":
                exclude_similar = True
            i += 1
        
        result = generate_password(length, use_upper, use_lower, use_digits, use_symbols, exclude_ambiguous, exclude_similar)
        
        if "error" in result:
            print(f"错误: {result['error']}")
            return 1
        
        print(f"\n🔐 密码生成成功")
        print(f"密码: {result['password']}")
        print(f"长度: {result['length']}")
        print(f"强度: {result['strength']}")
        print()

    elif command == "passphrase":
        word_count = 4
        separator = "-"
        
        # 解析参数
        i = 2
        while i < len(sys.argv):
            arg = sys.argv[i]
            if arg.isdigit():
                word_count = int(arg)
            elif arg.startswith("--separator="):
                separator = arg.split("=", 1)[1]
            i += 1
        
        if word_count > 12:
            word_count = 12
        
        result = generate_passphrase(word_count, separator)
        
        print(f"\n🔐 密码短语生成成功")
        print(f"密码: {result['password']}")
        print(f"词数: {word_count}")
        print(f"长度: {result['length']}")
        print(f"强度: {result['strength']}")
        print()

    elif command == "analyze":
        if len(sys.argv) < 3:
            print("错误: 请提供要分析的密码")
            return 1
        
        password = sys.argv[2]
        result = analyze_password(password)
        
        print(f"\n🔍 密码分析")
        print(f"密码: {password}")
        print(f"长度: {result['length']}")
        print(f"强度: {result['strength']}")
        print(f"字符集大小: {result['charset_size']}")
        print()
        print(f"包含小写字母: {'✅' if result['has_lowercase'] else '❌'}")
        print(f"包含大写字母: {'✅' if result['has_uppercase'] else '❌'}")
        print(f"包含数字: {'✅' if result['has_digits'] else '❌'}")
        print(f"包含符号: {'✅' if result['has_symbols'] else '❌'}")
        print()

    elif command == "list":
        print("\n📝 字符集")
        print(f"小写字母: {string.ascii_lowercase}")
        print(f"大写字母: {string.ascii_uppercase}")
        print(f"数字: {string.digits}")
        print("符号: !@#$%^&*()_+-=[]{}|;:,.<>?~`")
        print()
        print("排除易混淆字符:")
        print("小写: abcdefghijkmnpqrstuvwxyz (排除l,o)")
        print("大写: ABCDEFGHJKLMNPQRSTUVWXYZ (排除I,O)")
        print("数字: 23456789 (排除0,1)")
        print()

    else:
        print(f"未知命令: {command}")
        print("使用 'password-gen' 查看帮助")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
