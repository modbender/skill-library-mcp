#!/usr/bin/env python3
"""
研读报告生成脚本
根据论文元数据生成结构化研读报告
"""

import argparse
import json
from pathlib import Path
from datetime import datetime


def load_template(template_path: str) -> str:
    """加载报告模板"""
    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()


def generate_report(metadata: dict, template: str) -> str:
    """生成研读报告"""
    
    # 提取核心贡献（从摘要和引言推断）
    contributions = []
    abstract = metadata.get('abstract', '')
    if 'propose' in abstract.lower():
        contributions.append(abstract.split('propose')[1].split('.')[0].strip() + '.')
    if 'introduce' in abstract.lower():
        contributions.append(abstract.split('introduce')[1].split('.')[0].strip() + '.')
    if not contributions:
        contributions = ['待详细分析论文内容']
    
    # 复现可行性评估
    reproducibility = {
        'code_available': '待确认',
        'dataset_access': '待确认',
        'complexity': '中',
        'estimated_time': '1-2 周'
    }
    
    report = f"""# 论文研读报告

**生成时间：** {datetime.now().strftime('%Y-%m-%d %H:%M')}

## 基本信息

| 项目 | 内容 |
|------|------|
| 标题 | {metadata.get('title', 'N/A')} |
| 类型 | {metadata.get('paper_type', 'N/A')} |
| 关键词 | {', '.join(metadata.get('keywords', [])) or 'N/A'} |

## 摘要

{metadata.get('abstract', 'N/A')}

## 核心贡献

{''.join([f'{i+1}. {c}\\n' for i, c in enumerate(contributions)])}

## 方法论

### 问题定义
待详细分析...

### 核心思路
待详细分析...

### 关键公式
{chr(10).join([f"- 公式 ({f['number']}): {f['content']}" for f in metadata.get('key_formulas', [])]) or '待提取'}

## 实验配置

| 配置项 | 详情 |
|--------|------|
| 数据集 | 待确认 |
| 基线方法 | 待确认 |
| 评估指标 | 待确认 |
| 超参数 | 待确认 |

## 复现可行性评估

- **官方代码：** {reproducibility['code_available']}
- **数据集：** {reproducibility['dataset_access']}
- **计算需求：** GPU (建议 RTX 3090 或更高)
- **预计难度：** {reproducibility['complexity']}
- **预计时间：** {reproducibility['estimated_time']}

## 论文章节结构

{chr(10).join([f"- {s}" for s in metadata.get('sections', [])]) or '待提取'}

## 待澄清问题

1. 论文中是否有未明确说明的实现细节？
2. 是否有未公开的关键超参数？
3. 数据集预处理步骤是否完整描述？

## 下一步行动

- [ ] 查找官方代码仓库
- [ ] 确认可用的数据集来源
- [ ] 搭建基础实验环境
- [ ] 实现核心算法模块
- [ ] 复现关键实验结果

---
*本报告由 paper-research-assistant 自动生成*
"""
    return report


def main():
    parser = argparse.ArgumentParser(description='研读报告生成工具')
    parser.add_argument('--metadata', required=True, help='论文元数据 JSON 文件')
    parser.add_argument('--template', default='references/report_template.md', help='报告模板文件')
    parser.add_argument('--output', required=True, help='输出报告文件路径')
    
    args = parser.parse_args()
    
    # 加载元数据
    with open(args.metadata, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    
    # 加载模板（如果存在）
    template_path = Path(args.template)
    if template_path.exists():
        template = load_template(str(template_path))
    else:
        template = ""
    
    # 生成报告
    report = generate_report(metadata, template)
    
    # 输出
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"报告生成完成：{output_path}")


if __name__ == '__main__':
    main()
