#!/usr/bin/env python3
"""随机密码生成器"""

import random
import string
import os
from datetime import datetime

def generate_password(min_length=12, max_length=16, use_uppercase=True, use_lowercase=True, use_digits=True, use_symbols=True):
    """生成随机长度随机密码"""
    # 随机选择长度
    length = random.randint(min_length, max_length)
    
    chars = ''
    
    if use_uppercase:
        chars += string.ascii_uppercase
    if use_lowercase:
        chars += string.ascii_lowercase
    if use_digits:
        chars += string.digits
    if use_symbols:
        chars += string.punctuation
    
    if not chars:
        chars = string.ascii_letters + string.digits
    
    password = ''.join(random.choice(chars) for _ in range(length))
    return password, length

def main():
    # 生成12-16位随机长度密码，包含大小写+数字+符号
    password, length = generate_password(min_length=12, max_length=16)
    
    print(f"生成的密码: {password}")
    print(f"长度: {length} 位")
    
    # 保存到文件
    memory_dir = '/root/.openclaw/workspace/memory'
    os.makedirs(memory_dir, exist_ok=True)
    
    password_file = os.path.join(memory_dir, 'passwords.md')
    date = datetime.now().strftime('%Y-%m-%d')
    
    # 添加新密码
    new_entry = f"""
## {date}

- **随机密码**
  - 密码: `{password}`
  - 长度: {length} 位 (12-16位随机)
  - 字符: 大小写字母 + 数字 + 符号
"""
    
    with open(password_file, 'a') as f:
        f.write(new_entry)
    
    print(f"\n密码已保存到: {password_file}")
    return password, length

if __name__ == '__main__':
    main()
