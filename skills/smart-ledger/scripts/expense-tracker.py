#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能收支追踪器 - 核心逻辑
支持自然语言记账、自动分类、数据持久化
"""

import json
import os
import re
import sys
import tempfile
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# 数据存储路径
DATA_DIR = Path(os.path.expanduser("~/.openclaw/workspace/data/expenses"))
DATA_FILE = DATA_DIR / "expenses.json"

# 隐私保护：确保数据文件权限仅限当前用户
_PRIVATE_PERMS = 0o600  # rw-------
_PRIVATE_DIR_PERMS = 0o700  # rwx------

# 默认分类配置
DEFAULT_CATEGORIES = {
    "income": ["工资", "奖金", "投资", "兼职", "红包", "退款", "其他收入"],
    "expense": ["餐饮", "交通", "购物", "娱乐", "居住", "医疗", "教育", "通讯", "人情", "其他支出"]
}

# 关键词映射到分类
KEYWORD_MAPPING = {
    # 收入
    "工资": "工资", "薪水": "工资", "发钱": "工资",
    "奖金": "奖金", "年终奖": "奖金", "分红": "奖金",
    "投资": "投资", "股票": "投资", "基金": "投资", "理财": "投资", "利息": "投资",
    "兼职": "兼职", "副业": "兼职", "外快": "兼职",
    "红包": "红包", "转账": "红包",
    "退款": "退款", "退货": "退款",
    
    # 餐饮
    "吃饭": "餐饮", "午饭": "餐饮", "晚饭": "餐饮", "早餐": "餐饮", "宵夜": "餐饮",
    "餐厅": "餐饮", "外卖": "餐饮", "奶茶": "餐饮", "咖啡": "餐饮", "火锅": "餐饮",
    "烧烤": "餐饮", "超市": "餐饮", "水果": "餐饮", "买菜": "餐饮",
    
    # 交通
    "地铁": "交通", "公交": "交通", "打车": "交通", "滴滴": "交通", "出租车": "交通",
    "加油": "交通", "停车": "交通", "高铁": "交通", "火车": "交通", "飞机": "交通",
    "修车": "交通", "保养": "交通", "车险": "交通",
    
    # 购物
    "购物": "购物", "买衣服": "购物", "鞋子": "购物", "包包": "购物", "化妆品": "购物",
    "护肤品": "购物", "数码": "购物", "手机": "购物", "电脑": "购物", "家电": "购物",
    "淘宝": "购物", "京东": "购物", "拼多多": "购物", "天猫": "购物",
    
    # 娱乐
    "电影": "娱乐", "游戏": "娱乐", "充值": "娱乐", "会员": "娱乐", "视频": "娱乐",
    "音乐": "娱乐", "KTV": "娱乐", "旅游": "娱乐", "旅行": "娱乐", "酒店": "娱乐",
    
    # 居住
    "房租": "居住", "房贷": "居住", "水电": "居住", "物业费": "居住", "装修": "居住",
    "家具": "居住", "维修": "居住",
    
    # 医疗
    "医院": "医疗", "看病": "医疗", "买药": "医疗", "体检": "医疗", "保险": "医疗",
    
    # 教育
    "学费": "教育", "培训": "教育", "课程": "教育", "书本": "教育", "买书": "教育",
    "考试": "教育", "书": "教育",
    
    # 通讯
    "话费": "通讯", "宽带": "通讯", "流量": "通讯",
    
    # 人情
    "礼物": "人情", "请客": "人情", "份子钱": "人情", "聚餐": "人情"
}


class ExpenseTracker:
    """收支追踪器主类"""
    
    def __init__(self):
        self._ensure_data_dir()
        self.data = self._load_data()
    
    def _ensure_data_dir(self):
        """确保数据目录存在，并设置严格权限（仅当前用户可访问）"""
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        try:
            os.chmod(str(DATA_DIR), _PRIVATE_DIR_PERMS)
        except OSError:
            pass  # Windows 等不支持 chmod 的系统跳过
    
    def _load_data(self) -> Dict:
        """加载数据文件"""
        if DATA_FILE.exists():
            try:
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"⚠️ 数据文件读取失败，创建新文件: {e}")
        return {"expenses": [], "categories": DEFAULT_CATEGORIES}
    
    def _save_data(self):
        """原子保存数据到文件（先写临时文件再rename，防止写入中断导致数据丢失）"""
        try:
            fd, tmp_path = tempfile.mkstemp(
                dir=str(DATA_DIR), suffix='.tmp', prefix='expenses_'
            )
            try:
                with os.fdopen(fd, 'w', encoding='utf-8') as f:
                    json.dump(self.data, f, ensure_ascii=False, indent=2)
                os.replace(tmp_path, str(DATA_FILE))
                # 隐私保护：确保数据文件仅当前用户可读写
                try:
                    os.chmod(str(DATA_FILE), _PRIVATE_PERMS)
                except OSError:
                    pass
            except Exception:
                # 清理临时文件
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
                raise
        except IOError as e:
            print(f"❌ 数据保存失败: {e}")
            sys.exit(1)
    
    def _parse_amount(self, text: str) -> Optional[float]:
        """从文本中提取金额"""
        # 先移除日期部分，避免误匹配日期中的数字
        cleaned = re.sub(r'\d{4}-\d{1,2}-\d{1,2}', '', text)
        cleaned = re.sub(r'\d{1,2}月\d{1,2}[日号]', '', cleaned)

        patterns = [
            # 优先匹配带单位的：35元、35块、35.5元
            r'(\d+\.?\d*)\s*[元块]',
            # 匹配"花了/收入了 + 数字"的模式（数字必须跟在动词后面）
            r'(?:花了|收入了|赚了|收到|花|赚)\s*(\d+\.?\d*)',
        ]
        for pattern in patterns:
            match = re.search(pattern, cleaned)
            if match:
                try:
                    amount = float(match.group(1))
                    if amount > 0:
                        return amount
                except ValueError:
                    continue
        return None
    
    def _detect_type(self, text: str) -> str:
        """检测收支类型（收入/支出）"""
        income_keywords = ['收入', '赚到', '收到', '发工资', '奖金', '退款', '红包', '赚了']
        expense_keywords = ['花', '买', '吃', '付', '消费', '支出', '花了', '买了', '吃了', '付了']
        
        text_lower = text.lower()
        
        for kw in income_keywords:
            if kw in text_lower:
                return 'income'
        
        for kw in expense_keywords:
            if kw in text_lower:
                return 'expense'
        
        # 默认支出
        return 'expense'
    
    def _auto_categorize(self, text: str, trans_type: str) -> str:
        """自动分类"""
        # 先尝试关键词匹配
        for keyword, category in KEYWORD_MAPPING.items():
            if keyword in text:
                return category
        
        # 默认分类
        if trans_type == 'income':
            return "其他收入"
        return "其他支出"
    
    def _parse_date(self, text: str) -> str:
        """解析日期，默认为今天"""
        today = datetime.now()
        
        if '昨天' in text:
            date = today - timedelta(days=1)
        elif '前天' in text:
            date = today - timedelta(days=2)
        elif '今天' in text or '刚才' in text or '刚刚' in text:
            date = today
        else:
            # 尝试匹配 YYYY-MM-DD
            match = re.search(r'(\d{4})-(\d{1,2})-(\d{1,2})', text)
            if match:
                year = match.group(1)
                month = match.group(2)
                day = match.group(3)
                try:
                    # 验证日期合法性
                    datetime(int(year), int(month), int(day))
                    return f"{year}-{int(month):02d}-{int(day):02d}"
                except ValueError:
                    pass

            # 尝试匹配 MM-DD（无年份）
            match = re.search(r'(?<!\d)(\d{1,2})-(\d{1,2})(?!\d)', text)
            if match:
                month = match.group(1)
                day = match.group(2)
                try:
                    datetime(today.year, int(month), int(day))
                    return f"{today.year}-{int(month):02d}-{int(day):02d}"
                except ValueError:
                    pass
            date = today
        
        return date.strftime("%Y-%m-%d")
    
    def _extract_note(self, text: str, amount: float, category: str) -> str:
        """提取备注信息"""
        note = text
        # 移除日期格式
        note = re.sub(r'\d{4}-\d{1,2}-\d{1,2}', '', note)
        note = re.sub(r'\d{1,2}月\d{1,2}[日号]', '', note)
        # 移除金额相关文本
        note = re.sub(r'\d+\.?\d*\s*[元块]', '', note)
        # 移除常见时间词
        note = re.sub(r'(今天|昨天|前天|刚才|刚刚)', '', note)
        # 移除常见动词
        note = re.sub(r'(花了|收入了|赚了|收到了?)', '', note)
        # 清理多余空格和标点
        note = re.sub(r'\s+', ' ', note).strip()

        if not note:
            note = category

        return note[:50]  # 限制长度
    
    def add(self, text: str) -> Dict:
        """
        添加一笔收支记录
        
        Args:
            text: 自然语言描述，如"今天午饭花了35元"
        
        Returns:
            记录详情字典
        """
        # 解析金额
        amount = self._parse_amount(text)
        if amount is None:
            raise ValueError("无法识别金额，请使用格式如：花了35元")
        if amount > 9999999:
            raise ValueError("金额不能超过9,999,999")
        if amount <= 0:
            raise ValueError("金额必须大于0")
        
        # 检测类型
        trans_type = self._detect_type(text)
        
        # 自动分类
        category = self._auto_categorize(text, trans_type)
        
        # 解析日期
        date = self._parse_date(text)
        
        # 提取备注
        note = self._extract_note(text, amount, category)
        
        # 创建记录 — 使用UUID短ID，避免删除后ID冲突
        record = {
            "id": uuid.uuid4().hex[:8],
            "date": date,
            "type": trans_type,
            "amount": round(amount, 2),
            "category": category,
            "note": note,
            "raw_text": text,
            "created_at": datetime.now().isoformat()
        }
        
        # 添加到数据
        self.data["expenses"].append(record)
        self._save_data()
        
        return record
    
    def list(self, days: int = 7, trans_type: Optional[str] = None) -> List[Dict]:
        """
        列出收支记录
        
        Args:
            days: 最近多少天，默认7天
            trans_type: 类型筛选，'income'/'expense'/None
        
        Returns:
            记录列表
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        cutoff_str = cutoff_date.strftime("%Y-%m-%d")
        
        records = []
        for r in self.data["expenses"]:
            if r["date"] >= cutoff_str:
                if trans_type is None or r["type"] == trans_type:
                    records.append(r)
        
        # 按日期倒序
        records.sort(key=lambda x: x["date"], reverse=True)
        return records
    
    def delete(self, record_id: str) -> bool:
        """删除指定记录"""
        for i, r in enumerate(self.data["expenses"]):
            if str(r["id"]) == str(record_id):
                del self.data["expenses"][i]
                self._save_data()
                return True
        return False
    
    def get_summary(self, days: int = 30) -> Dict:
        """获取收支摘要"""
        records = self.list(days=days)
        
        income_total = sum(r["amount"] for r in records if r["type"] == "income")
        expense_total = sum(r["amount"] for r in records if r["type"] == "expense")
        
        # 分类统计
        category_stats = {}
        for r in records:
            cat = r["category"]
            if cat not in category_stats:
                category_stats[cat] = {"income": 0, "expense": 0}
            category_stats[cat][r["type"]] += r["amount"]
        
        return {
            "period_days": days,
            "income": round(income_total, 2),
            "expense": round(expense_total, 2),
            "balance": round(income_total - expense_total, 2),
            "record_count": len(records),
            "category_breakdown": category_stats
        }
    
    def get_categories(self) -> Dict:
        """获取分类列表"""
        return self.data.get("categories", DEFAULT_CATEGORIES)
    
    def add_category(self, trans_type: str, category: str):
        """添加自定义分类"""
        if trans_type not in ["income", "expense"]:
            raise ValueError("类型必须是 income 或 expense")
        
        if "categories" not in self.data:
            self.data["categories"] = DEFAULT_CATEGORIES.copy()
        
        if category not in self.data["categories"][trans_type]:
            self.data["categories"][trans_type].append(category)
            self._save_data()


def main():
    """命令行入口"""
    tracker = ExpenseTracker()
    
    if len(sys.argv) < 2:
        print("智能收支追踪器")
        print("用法: python expense-tracker.py <命令> [参数]")
        print("")
        print("命令:")
        print("  add <描述>     - 添加记录，如: add '今天午饭花了35元'")
        print("  list [天数]    - 列出记录，默认最近7天")
        print("  summary [天数] - 收支摘要，默认最近30天")
        print("  delete <ID>    - 删除指定记录")
        print("  categories     - 显示分类列表")
        print("")
        sys.exit(0)
    
    command = sys.argv[1]
    
    try:
        if command == "add":
            if len(sys.argv) < 3:
                print("❌ 请提供描述，如: python expense-tracker.py add '今天午饭35元'")
                sys.exit(1)
            
            text = " ".join(sys.argv[2:])
            record = tracker.add(text)
            type_emoji = "💰" if record["type"] == "income" else "💸"
            type_text = "收入" if record["type"] == "income" else "支出"
            print(f"✅ 已记录{type_emoji} {type_text}")
            print(f"   金额: ¥{record['amount']}")
            print(f"   分类: {record['category']}")
            print(f"   日期: {record['date']}")
            print(f"   备注: {record['note']}")
        
        elif command == "list":
            days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
            records = tracker.list(days=days)
            
            if not records:
                print(f"📭 最近{days}天没有记录")
                return
            
            print(f"📋 最近{days}天收支记录 ({len(records)}条)")
            print("-" * 60)
            
            current_date = ""
            for r in records:
                if r["date"] != current_date:
                    current_date = r["date"]
                    print(f"\n📅 {current_date}")
                
                type_emoji = "💰" if r["type"] == "income" else "💸"
                print(f"  [{r['id']}] {type_emoji} ¥{r['amount']:8.2f}  {r['category']:8s}  {r['note']}")
        
        elif command == "summary":
            days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
            summary = tracker.get_summary(days=days)
            
            print(f"📊 最近{days}天收支摘要")
            print("=" * 50)
            print(f"💰 总收入: ¥{summary['income']:.2f}")
            print(f"💸 总支出: ¥{summary['expense']:.2f}")
            balance_emoji = "📈" if summary['balance'] >= 0 else "📉"
            print(f"{balance_emoji} 净余额: ¥{summary['balance']:.2f}")
            print(f"📝 记录数: {summary['record_count']} 条")
            
            if summary['category_breakdown']:
                print("\n📁 分类统计:")
                for cat, amounts in sorted(summary['category_breakdown'].items()):
                    if amounts['expense'] > 0:
                        print(f"  💸 {cat}: ¥{amounts['expense']:.2f}")
                    if amounts['income'] > 0:
                        print(f"  💰 {cat}: ¥{amounts['income']:.2f}")
        
        elif command == "delete":
            if len(sys.argv) < 3:
                print("❌ 请提供记录ID")
                sys.exit(1)
            
            record_id = sys.argv[2]
            if tracker.delete(record_id):
                print(f"✅ 已删除记录 #{record_id}")
            else:
                print(f"❌ 未找到记录 #{record_id}")
        
        elif command == "categories":
            cats = tracker.get_categories()
            print("📁 分类列表")
            print("\n收入分类:")
            for c in cats["income"]:
                print(f"  💰 {c}")
            print("\n支出分类:")
            for c in cats["expense"]:
                print(f"  💸 {c}")
        
        else:
            print(f"❌ 未知命令: {command}")
            print("可用命令: add, list, summary, delete, categories")
    
    except ValueError as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
