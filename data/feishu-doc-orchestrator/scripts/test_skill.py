#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试飞书文档创建技能
"""

import sys
import os
import tempfile
from pathlib import Path

def create_test_markdown():
    """创建测试Markdown文件"""
    content = """# 测试文档 - 飞书文档创建技能

这是一个测试文档，用于验证飞书文档创建技能的功能。

## 功能测试

### 1. 标题层级
- H1 标题（本文档标题）
- H2 标题（此节标题）
- H3 标题（这个标题）

### 2. 列表测试
无序列表：
- 项目一
- 项目二
- 项目三

有序列表：
1. 第一项
2. 第二项
3. 第三项

### 3. 代码块测试
```python
def hello_world():
    print("Hello, Feishu!")
    return "Success"
```

### 4. 引用测试
> 这是一个引用块。
> 第二行引用内容。

### 5. 表格测试
| 姓名 | 年龄 | 城市 |
|------|------|------|
| 张三 | 25   | 北京 |
| 李四 | 30   | 上海 |
| 王五 | 28   | 广州 |

### 6. 待办事项
- [ ] 待完成任务一
- [x] 已完成任务二
- [ ] 待完成任务三

### 7. 分割线
---

## 测试结论
如果此文档成功创建并显示所有格式，说明飞书文档创建技能工作正常。
"""
    
    # 创建临时文件
    temp_dir = tempfile.mkdtemp(prefix="feishu_test_")
    test_file = Path(temp_dir) / "test_document.md"
    
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(content)
    
    return test_file, temp_dir

def main():
    print("=" * 70)
    print("飞书文档创建技能 - 功能测试")
    print("=" * 70)
    
    # 导入CLI模块
    skill_root = Path(__file__).parent.parent
    sys.path.insert(0, str(skill_root / "scripts"))
    
    try:
        from feishu_doc_cli import run_orchestrator, load_config
    except ImportError:
        print("[错误] 无法导入CLI模块")
        return 1
    
    # 检查配置
    print("\n[步骤1] 检查配置...")
    config_file = load_config()
    if not config_file:
        print("[错误] 配置检查失败")
        return 1
    
    print(f"[信息] 使用配置文件: {config_file}")
    
    # 创建测试Markdown文件
    print("\n[步骤2] 创建测试文档...")
    test_file, temp_dir = create_test_markdown()
    print(f"[信息] 测试文件: {test_file}")
    
    # 运行测试
    print("\n[步骤3] 运行转换测试...")
    print(f"[信息] 文档标题: 飞书技能测试文档")
    
    try:
        # 获取orchestrator脚本路径
        orchestrator_script = (
            skill_root / "original-skill" / "feishu-doc-orchestrator" / "scripts" / "orchestrator.py"
        )
        
        if not orchestrator_script.exists():
            print(f"[错误] Orchestrator脚本未找到: {orchestrator_script}")
            return 1
        
        # 导入原始orchestrator
        import subprocess
        
        cmd = [
            sys.executable,
            str(orchestrator_script),
            str(test_file),
            "--title",
            "飞书技能测试文档"
        ]
        
        print(f"[执行] 命令: {' '.join(cmd)}")
        
        # 设置环境变量
        env = os.environ.copy()
        env["FEISHU_CONFIG_PATH"] = str(config_file)
        
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        
        # 输出结果
        print("\n" + "=" * 70)
        print("转换输出:")
        print("=" * 70)
        
        if result.stdout:
            print(result.stdout)
        
        if result.stderr:
            print("\n[错误输出]:")
            print(result.stderr)
        
        print("\n" + "=" * 70)
        
        if result.returncode == 0:
            print("[成功] 测试完成！请检查飞书文档")
            
            # 尝试从输出中提取文档链接
            if "文档链接:" in result.stdout:
                for line in result.stdout.split('\n'):
                    if "文档链接:" in line:
                        print(f"\n[文档链接] {line.split('文档链接:')[-1].strip()}")
            
            return 0
        else:
            print(f"[失败] 转换失败，退出码: {result.returncode}")
            return 1
            
    except Exception as e:
        print(f"[异常] 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        # 清理临时文件
        import shutil
        try:
            shutil.rmtree(temp_dir)
            print(f"\n[清理] 临时目录已删除: {temp_dir}")
        except:
            pass

if __name__ == "__main__":
    sys.exit(main())