#!/usr/bin/env python3
"""
小红书评论回复生成器
生成针对第2和第3条评论的回复内容
"""

def generate_replies():
    # 模板回复 - 请根据实际评论内容修改
    reply2 = """@[用户名2] 
[根据第2条评论内容自定义回复]""" 
    
    # 模板回复 - 请根据实际评论内容修改
    reply3 = """@[用户名3]
[根据第3条评论内容自定义回复]"""
    
    print("=== 小红书评论回复模板 ===")
    print(f"\n回复第2条评论模板：")
    print(reply2)
    print(f"\n回复第3条评论模板：")
    print(reply3)
    
    return reply2, reply3

if __name__ == "__main__":
    generate_replies()