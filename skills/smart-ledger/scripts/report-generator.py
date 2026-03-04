#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能收支报告生成器
支持日/周/月/年报告，趋势分析，异常检测
"""

import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# 数据路径
DATA_DIR = Path(os.path.expanduser("~/.openclaw/workspace/data/expenses"))
DATA_FILE = DATA_DIR / "expenses.json"


class ReportGenerator:
    """报告生成器"""
    
    def __init__(self):
        self.data = self._load_data()
    
    def _load_data(self) -> Dict:
        """加载数据"""
        if DATA_FILE.exists():
            try:
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {"expenses": []}
    
    def _get_records_in_range(self, start_date: str, end_date: str) -> List[Dict]:
        """获取日期范围内的记录"""
        records = []
        for r in self.data.get("expenses", []):
            if start_date <= r["date"] <= end_date:
                records.append(r)
        return records
    
    def _get_date_range(self, period: str, offset: int = 0) -> Tuple[str, str]:
        """
        获取日期范围
        
        Args:
            period: 'day', 'week', 'month', 'year'
            offset: 偏移量，0表示当前周期，1表示上一个周期
        """
        today = datetime.now()
        
        if period == 'day':
            target = today - timedelta(days=offset)
            start = end = target.strftime("%Y-%m-%d")
        
        elif period == 'week':
            # 获取本周一
            monday = today - timedelta(days=today.weekday(), weeks=offset)
            sunday = monday + timedelta(days=6)
            start = monday.strftime("%Y-%m-%d")
            end = sunday.strftime("%Y-%m-%d")
        
        elif period == 'month':
            # 获取目标月
            year = today.year
            month = today.month - offset
            while month <= 0:
                year -= 1
                month += 12
            
            start = f"{year}-{month:02d}-01"
            # 计算月末
            if month == 12:
                next_month = datetime(year + 1, 1, 1)
            else:
                next_month = datetime(year, month + 1, 1)
            last_day = (next_month - timedelta(days=1)).day
            end = f"{year}-{month:02d}-{last_day}"
        
        elif period == 'year':
            year = today.year - offset
            start = f"{year}-01-01"
            end = f"{year}-12-31"
        
        else:
            raise ValueError(f"不支持的周期类型: {period}")
        
        return start, end
    
    def generate_daily_report(self, date: Optional[str] = None) -> Dict:
        """生成日报"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        records = self._get_records_in_range(date, date)
        
        income = sum(r["amount"] for r in records if r["type"] == "income")
        expense = sum(r["amount"] for r in records if r["type"] == "expense")
        
        # 分类统计
        category_expense = defaultdict(float)
        category_income = defaultdict(float)
        
        for r in records:
            if r["type"] == "expense":
                category_expense[r["category"]] += r["amount"]
            else:
                category_income[r["category"]] += r["amount"]
        
        return {
            "type": "daily",
            "date": date,
            "income": round(income, 2),
            "expense": round(expense, 2),
            "balance": round(income - expense, 2),
            "record_count": len(records),
            "top_expenses": sorted(category_expense.items(), key=lambda x: x[1], reverse=True)[:5],
            "top_incomes": sorted(category_income.items(), key=lambda x: x[1], reverse=True)[:3],
            "records": records
        }
    
    def generate_weekly_report(self, offset: int = 0) -> Dict:
        """生成周报"""
        start, end = self._get_date_range('week', offset)
        records = self._get_records_in_range(start, end)
        
        # 按天统计
        daily_data = defaultdict(lambda: {"income": 0, "expense": 0})
        category_expense = defaultdict(float)
        category_income = defaultdict(float)
        
        for r in records:
            daily_data[r["date"]][r["type"]] += r["amount"]
            if r["type"] == "expense":
                category_expense[r["category"]] += r["amount"]
            else:
                category_income[r["category"]] += r["amount"]
        
        income = sum(r["amount"] for r in records if r["type"] == "income")
        expense = sum(r["amount"] for r in records if r["type"] == "expense")
        
        return {
            "type": "weekly",
            "start_date": start,
            "end_date": end,
            "income": round(income, 2),
            "expense": round(expense, 2),
            "balance": round(income - expense, 2),
            "record_count": len(records),
            "daily_breakdown": dict(daily_data),
            "top_expenses": sorted(category_expense.items(), key=lambda x: x[1], reverse=True)[:5],
            "top_incomes": sorted(category_income.items(), key=lambda x: x[1], reverse=True)[:3]
        }
    
    def generate_monthly_report(self, offset: int = 0) -> Dict:
        """生成月报"""
        start, end = self._get_date_range('month', offset)
        records = self._get_records_in_range(start, end)
        
        income = sum(r["amount"] for r in records if r["type"] == "income")
        expense = sum(r["amount"] for r in records if r["type"] == "expense")
        
        # 按周统计
        weekly_data = defaultdict(lambda: {"income": 0, "expense": 0})
        category_expense = defaultdict(float)
        category_income = defaultdict(float)
        
        for r in records:
            date = datetime.strptime(r["date"], "%Y-%m-%d")
            week_num = date.isocalendar()[1]
            weekly_data[f"第{week_num}周"][r["type"]] += r["amount"]
            
            if r["type"] == "expense":
                category_expense[r["category"]] += r["amount"]
            else:
                category_income[r["category"]] += r["amount"]
        
        # 计算日均支出
        days_in_month = int(end.split("-")[2])
        avg_daily_expense = expense / days_in_month if days_in_month > 0 else 0
        
        return {
            "type": "monthly",
            "start_date": start,
            "end_date": end,
            "income": round(income, 2),
            "expense": round(expense, 2),
            "balance": round(income - expense, 2),
            "record_count": len(records),
            "avg_daily_expense": round(avg_daily_expense, 2),
            "weekly_breakdown": dict(weekly_data),
            "top_expenses": sorted(category_expense.items(), key=lambda x: x[1], reverse=True)[:5],
            "top_incomes": sorted(category_income.items(), key=lambda x: x[1], reverse=True)[:3]
        }
    
    def generate_trend_analysis(self, days: int = 30) -> Dict:
        """
        生成趋势分析报告
        
        包含:
        - 支出趋势（上升/下降）
        - 异常消费检测
        - 消费建议
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        records = self._get_records_in_range(
            start_date.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d")
        )
        
        # 按周分组
        weekly_expense = defaultdict(float)
        weekly_income = defaultdict(float)
        
        for r in records:
            date = datetime.strptime(r["date"], "%Y-%m-%d")
            week_key = date.strftime("%Y-W%W")
            if r["type"] == "expense":
                weekly_expense[week_key] += r["amount"]
            else:
                weekly_income[week_key] += r["amount"]
        
        # 计算周环比变化
        weeks = sorted(weekly_expense.keys())
        trend = "stable"
        if len(weeks) >= 2:
            recent = weekly_expense[weeks[-1]]
            previous = weekly_expense[weeks[-2]]
            if previous > 0:
                change_pct = (recent - previous) / previous * 100
                if change_pct > 20:
                    trend = "increasing"
                elif change_pct < -20:
                    trend = "decreasing"
        
        # 异常检测（超过平均值2倍）
        if weekly_expense:
            avg_weekly = sum(weekly_expense.values()) / len(weekly_expense)
            anomalies = [
                {"week": w, "amount": a, "deviation": round((a - avg_weekly) / avg_weekly * 100, 1)}
                for w, a in weekly_expense.items() if a > avg_weekly * 2
            ]
        else:
            anomalies = []
        
        return {
            "type": "trend",
            "period_days": days,
            "expense_trend": trend,
            "weekly_expenses": dict(weekly_expense),
            "weekly_incomes": dict(weekly_income),
            "anomalies": anomalies,
            "avg_weekly_expense": round(sum(weekly_expense.values()) / len(weekly_expense), 2) if weekly_expense else 0
        }
    
    def format_report(self, report: Dict, format_type: str = "text") -> str:
        """格式化报告为可读文本"""
        if format_type == "json":
            return json.dumps(report, ensure_ascii=False, indent=2)
        
        lines = []
        
        # 标题
        if report["type"] == "daily":
            lines.append(f"📅 收支日报 ({report['date']})")
        elif report["type"] == "weekly":
            lines.append(f"📊 收支周报 ({report['start_date']} ~ {report['end_date']})")
        elif report["type"] == "monthly":
            lines.append(f"📈 收支月报 ({report['start_date'][:7]})")
        elif report["type"] == "trend":
            lines.append(f"📉 消费趋势分析 (近{report['period_days']}天)")
        
        lines.append("=" * 50)
        
        # 收支概览
        if "income" in report:
            balance = report.get('balance', report['income'] - report['expense'])
            balance_emoji = "📈" if balance >= 0 else "📉"
            
            lines.append(f"💰 总收入: ¥{report['income']:.2f}")
            lines.append(f"💸 总支出: ¥{report['expense']:.2f}")
            lines.append(f"{balance_emoji} 净余额: ¥{balance:.2f}")
            lines.append(f"📝 记录数: {report.get('record_count', 0)} 条")
            
            if "avg_daily_expense" in report:
                lines.append(f"📊 日均支出: ¥{report['avg_daily_expense']:.2f}")
        
        # 趋势信息
        if report["type"] == "trend":
            trend_text = {
                "increasing": "⚠️ 支出呈上升趋势",
                "decreasing": "✅ 支出呈下降趋势",
                "stable": "➡️ 支出保持稳定"
            }
            lines.append(f"\n{trend_text.get(report['expense_trend'], '')}")
            
            if report.get("anomalies"):
                lines.append("\n⚠️ 异常消费周:")
                for a in report["anomalies"]:
                    lines.append(f"  {a['week']}: ¥{a['amount']:.2f} (+{a['deviation']}%)")
        
        # 分类详情
        if "top_expenses" in report and report["top_expenses"]:
            lines.append("\n🏆 支出TOP分类:")
            for cat, amount in report["top_expenses"]:
                lines.append(f"  💸 {cat}: ¥{amount:.2f}")
        
        if "top_incomes" in report and report["top_incomes"]:
            lines.append("\n💰 收入TOP分类:")
            for cat, amount in report["top_incomes"]:
                lines.append(f"  💰 {cat}: ¥{amount:.2f}")
        
        return "\n".join(lines)


def main():
    """命令行入口"""
    generator = ReportGenerator()
    
    if len(sys.argv) < 2:
        print("智能收支报告生成器")
        print("用法: python report-generator.py <报告类型> [参数]")
        print("")
        print("报告类型:")
        print("  daily [日期]        - 日报，如: daily 2024-01-15")
        print("  weekly [周偏移]     - 周报，0=本周, 1=上周")
        print("  monthly [月偏移]    - 月报，0=本月, 1=上月")
        print("  trend [天数]        - 趋势分析，默认30天")
        print("")
        sys.exit(0)
    
    command = sys.argv[1]
    
    try:
        if command == "daily":
            date = sys.argv[2] if len(sys.argv) > 2 else None
            report = generator.generate_daily_report(date)
        
        elif command == "weekly":
            offset = int(sys.argv[2]) if len(sys.argv) > 2 else 0
            report = generator.generate_weekly_report(offset)
        
        elif command == "monthly":
            offset = int(sys.argv[2]) if len(sys.argv) > 2 else 0
            report = generator.generate_monthly_report(offset)
        
        elif command == "trend":
            days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
            report = generator.generate_trend_analysis(days)
        
        else:
            print(f"❌ 未知报告类型: {command}")
            print("可用类型: daily, weekly, monthly, trend")
            sys.exit(1)
        
        # 输出报告
        format_type = sys.argv[-1] if sys.argv[-1] in ["text", "json"] else "text"
        print(generator.format_report(report, format_type))
    
    except Exception as e:
        print(f"❌ 生成报告失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
