#!/usr/bin/env python3
"""
Weekly Reporter Tool for OpenClaw
自动周报生成器 - 工作周报智能生成
"""
import json
import sys
from datetime import datetime, timedelta
import random

# 模拟任务数据
def get_this_week_tasks():
    """获取本周任务数据（模拟）"""
    return {
        'total': 15,
        'completed': 12,
        'in_progress': 2,
        'not_started': 1,
        'total_hours': 32,
        'completed_tasks': [
            {'name': '完成用户需求文档', 'hours': 4, 'status': 'done'},
            {'name': '修复登录Bug', 'hours': 2, 'status': 'done'},
            {'name': '优化数据库查询', 'hours': 3, 'status': 'done'},
            {'name': '代码审查', 'hours': 2, 'status': 'done'},
            {'name': '编写测试用例', 'hours': 3, 'status': 'done'},
            {'name': '完成API文档', 'hours': 2, 'status': 'done'},
            {'name': '修复UI显示问题', 'hours': 1, 'status': 'done'},
            {'name': '配置CI/CD流程', 'hours': 3, 'status': 'done'},
            {'name': '更新技术文档', 'hours': 2, 'status': 'done'},
            {'name': '性能测试', 'hours': 2, 'status': 'done'},
            {'name': '用户培训', 'hours': 2, 'status': 'done'},
            {'name': 'Bug回归测试', 'hours': 2, 'status': 'done'},
        ],
        'in_progress_tasks': [
            {'name': '聊天功能开发', 'hours': 4, 'progress': '60%', 'status': 'in_progress'},
            {'name': '性能优化', 'hours': 3, 'progress': '40%', 'status': 'in_progress'},
        ],
        'not_started_tasks': [
            {'name': 'APP上线准备', 'hours': 5, 'status': 'not_started'},
        ],
        'next_week_plan': [
            '完成聊天功能开发',
            '用户反馈处理',
            '性能优化',
            'APP上线准备',
        ],
        'issues': [
            '接口联调需要额外资源协调',
            '测试环境不稳定，建议增加带宽',
            '建议采购新的开发机器',
        ]
    }

def get_last_week_tasks():
    """获取上周任务数据（模拟）"""
    return {
        'total': 12,
        'completed': 10,
        'in_progress': 1,
        'not_started': 1,
        'total_hours': 28,
        'completed_tasks': [
            {'name': '架构设计', 'hours': 4, 'status': 'done'},
            {'name': '数据库设计', 'hours': 3, 'status': 'done'},
            {'name': '原型评审', 'hours': 2, 'status': 'done'},
            {'name': '技术选型', 'hours': 2, 'status': 'done'},
            {'name': '开发环境搭建', 'hours': 3, 'status': 'done'},
            {'name': '基础框架搭建', 'hours': 4, 'status': 'done'},
            {'name': '权限模块开发', 'hours': 3, 'status': 'done'},
            {'name': '用户模块开发', 'hours': 3, 'status': 'done'},
            {'name': '接口定义', 'hours': 2, 'status': 'done'},
            {'name': '单元测试', 'hours': 2, 'status': 'done'},
        ],
        'in_progress_tasks': [
            {'name': '登录模块开发', 'hours': 3, 'progress': '70%', 'status': 'in_progress'},
        ],
        'not_started_tasks': [
            {'name': '第三方登录', 'hours': 4, 'status': 'not_started'},
        ],
        'next_week_plan': [
            '完成登录模块',
            '第三方登录对接',
            '开始消息模块',
            'UI优化',
        ],
        'issues': [
            '部分需求变更需要确认',
            '第三方API文档不完整',
        ]
    }

def format_simple(data, title):
    """简洁版模板"""
    completion_rate = (data['completed'] / data['total']) * 100
    lines = [
        f"# 📋 {title}",
        "",
        "## 📊 数据概览",
        f"- 总任务数：{data['total']}",
        f"- 已完成：{data['completed']} ({completion_rate:.0f}%)",
        f"- 进行中：{data['in_progress']}",
        f"- 未开始：{data['not_started']}",
        f"- 总耗时：{data['total_hours']}小时",
        "",
    ]
    
    if data['completed_tasks']:
        lines.append("## ✅ 已完成任务")
        for t in data['completed_tasks'][:5]:
            lines.append(f"- ✅ {t['name']} - {t['hours']}h")
        if len(data['completed_tasks']) > 5:
            lines.append(f"- ... 还有{len(data['completed_tasks'])-5}项")
        lines.append("")
    
    if data['in_progress_tasks']:
        lines.append("## 🔥 进行中")
        for t in data['in_progress_tasks']:
            lines.append(f"- 🔄 {t['name']} - 已完成{t['progress']}")
        lines.append("")
    
    if data['next_week_plan']:
        lines.append("## 📅 下周计划")
        for p in data['next_week_plan']:
            lines.append(f"- {p}")
        lines.append("")
    
    return '\n'.join(lines)

def format_detailed(data, title):
    """详细版模板"""
    completion_rate = (data['completed'] / data['total']) * 100
    lines = [
        f"# 📋 {title}",
        "",
        "## 📊 数据概览",
        f"| 指标 | 数值 |",
        f"|------|------|",
        f"| 总任务数 | {data['total']} |",
        f"| 已完成 | {data['completed']} ({completion_rate:.1f}%) |",
        f"| 进行中 | {data['in_progress']} |",
        f"| 未开始 | {data['not_started']} |",
        f"| 总耗时 | {data['total_hours']}小时 |",
        "",
    ]
    
    if data['completed_tasks']:
        lines.append("## ✅ 已完成任务")
        lines.append("| 任务名称 | 耗时 |")
        lines.append("|----------|------|")
        for t in data['completed_tasks']:
            lines.append(f"| {t['name']} | {t['hours']}h |")
        lines.append("")
    
    if data['in_progress_tasks']:
        lines.append("## 🔥 进行中")
        lines.append("| 任务名称 | 进度 | 预计耗时 |")
        lines.append("|----------|------|----------|")
        for t in data['in_progress_tasks']:
            lines.append(f"| {t['name']} | {t['progress']} | {t['hours']}h |")
        lines.append("")
    
    if data['not_started_tasks']:
        lines.append("## ⏳ 未开始")
        for t in data['not_started_tasks']:
            lines.append(f"- ⏳ {t['name']} - 预计{t['hours']}h")
        lines.append("")
    
    if data['next_week_plan']:
        lines.append("## 📅 下周计划")
        for i, p in enumerate(data['next_week_plan'], 1):
            lines.append(f"{i}. {p}")
        lines.append("")
    
    if data['issues']:
        lines.append("## 💡 问题与建议")
        for issue in data['issues']:
            lines.append(f"- {issue}")
        lines.append("")
    
    lines.append(f"---\n")
    lines.append(f"*报告生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}*")
    
    return '\n'.join(lines)

def format_tech(data, title):
    """技术版模板"""
    completion_rate = (data['completed'] / data['total']) * 100
    lines = [
        f"# 🔧 技术周报 - {title}",
        "",
        "## 📈 开发统计",
        f"- **代码提交**: {len(data['completed_tasks'])} 次",
        f"- **代码行数**: ~{data['total_hours'] * 20} 行",
        f"- **完成率**: {completion_rate:.0f}%",
        f"- **Bug修复**: {random.randint(5, 15)} 个",
        "",
        "## ✅ 已完成",
    ]
    
    for t in data['completed_tasks']:
        lines.append(f"- [x] {t['name']} ({t['hours']}h)")
    
    if data['in_progress_tasks']:
        lines.append("")
        lines.append("## 🔄 进行中")
        for t in data['in_progress_tasks']:
            lines.append(f"- [~] {t['name']} ({t['progress']})")
    
    lines.append("")
    lines.append("## 📅 下周计划")
    for p in data['next_week_plan']:
        lines.append(f"- [ ] {p}")
    
    if data['issues']:
        lines.append("")
        lines.append("## ⚠️ 技术债务")
        for issue in data['issues']:
            lines.append(f"- {issue}")
    
    return '\n'.join(lines)

def main():
    """主函数"""
    if len(sys.argv) < 2 or sys.argv[1] in ['help', '-h', '--help']:
        print("=" * 50)
        print("📋 Weekly Reporter 自动周报生成器")
        print("=" * 50)
        print("")
        print("用法: /weekly-reporter <选项> [参数]")
        print("")
        print("选项:")
        print("  this-week           - 生成本周周报")
        print("  last-week           - 生成上周周报")
        print("  --template <类型>   - 指定模板 (simple/detailed/tech)")
        print("  --brief             - 简短模式")
        print("")
        print("模板类型:")
        print("  simple    - 简洁版（默认）")
        print("  detailed  - 详细版")
        print("  tech      - 技术版")
        print("")
        print("示例:")
        print("  /weekly-reporter this-week")
        print("  /weekly-reporter last-week --template detailed")
        print("  /weekly-reporter this-week --template tech")
        return
    
    # 解析参数
    template = 'simple'
    week_type = 'this-week'
    
    args = sys.argv[1:]
    for i, arg in enumerate(args):
        if arg == '--template' and i + 1 < len(args):
            template = args[i + 1]
        elif arg == '--brief':
            template = 'simple'
        elif arg in ['this-week', 'last-week']:
            week_type = arg
    
    # 获取数据
    if week_type == 'this-week':
        data = get_this_week_tasks()
        title = "本周工作周报 (2026.03.02)"
    else:
        data = get_last_week_tasks()
        title = "上周工作周报 (2026.02.23-03.01)"
    
    # 生成周报
    if template == 'detailed':
        print(format_detailed(data, title))
    elif template == 'tech':
        print(format_tech(data, title))
    else:
        print(format_simple(data, title))

if __name__ == '__main__':
    main()