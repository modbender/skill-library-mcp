"""
基金持仓管理系统 - 数据库操作层
"""
import json
import sqlite3
from datetime import datetime, date
from pathlib import Path
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

from src.models import (
    FundHolding, FundInfo, FundHoldingsDetail,
    StockHolding, BondHolding, FundType
)
from src.config import get_db_path


class Database:
    """SQLite数据库操作类"""

    def __init__(self, db_path: str = None):
        self.db_path = db_path if db_path is not None else get_db_path()
        self._init_database()

    def _init_database(self):
        """初始化数据库表结构"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # 公募基金持有信息表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS fund_holdings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fund_code TEXT NOT NULL,
                    fund_name TEXT NOT NULL,
                    share_class TEXT,
                    fund_manager TEXT,
                    fund_account TEXT NOT NULL,
                    sales_agency TEXT,
                    trade_account TEXT NOT NULL,
                    holding_shares REAL NOT NULL,
                    share_date TEXT NOT NULL,
                    nav REAL NOT NULL,
                    nav_date TEXT NOT NULL,
                    asset_value REAL NOT NULL,
                    settlement_currency TEXT,
                    dividend_method TEXT,
                    fund_type TEXT DEFAULT 'public',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(fund_account, trade_account, fund_code)
                )
            """)

            # 基金基础信息表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS fund_info (
                    fund_code TEXT PRIMARY KEY,
                    fund_name TEXT NOT NULL,
                    fund_invest_type TEXT,
                    risk_5_level INTEGER,
                    nav REAL,
                    nav_date TEXT,
                    net_asset REAL,
                    setup_date TEXT,
                    yearly_roe REAL,
                    one_year_return REAL,
                    setup_day_return REAL,
                    manager_names TEXT,
                    stock_ratio REAL,
                    bond_ratio REAL,
                    cash_ratio REAL,
                    data_update_time TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 基金持仓详情表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS fund_holdings_detail (
                    fund_code TEXT PRIMARY KEY,
                    report_date TEXT,
                    stock_invest_ratio REAL,
                    bond_invest_ratio REAL,
                    top_stocks TEXT,
                    top_bonds TEXT,
                    data_update_time TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 创建索引
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_fund_holdings_code
                ON fund_holdings(fund_code)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_fund_holdings_account
                ON fund_holdings(fund_account)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_fund_holdings_manager
                ON fund_holdings(fund_manager)
            """)

            conn.commit()

    @contextmanager
    def _get_connection(self):
        """获取数据库连接的上下文管理器"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    # ==================== FundHolding 操作 ====================

    def upsert_fund_holding(self, holding: FundHolding) -> bool:
        """插入或更新基金持有信息"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO fund_holdings (
                    fund_code, fund_name, share_class, fund_manager,
                    fund_account, sales_agency, trade_account,
                    holding_shares, share_date, nav, nav_date,
                    asset_value, settlement_currency, dividend_method,
                    fund_type, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(fund_account, trade_account, fund_code)
                DO UPDATE SET
                    fund_name = excluded.fund_name,
                    share_class = excluded.share_class,
                    fund_manager = excluded.fund_manager,
                    sales_agency = excluded.sales_agency,
                    holding_shares = excluded.holding_shares,
                    share_date = excluded.share_date,
                    nav = excluded.nav,
                    nav_date = excluded.nav_date,
                    asset_value = excluded.asset_value,
                    settlement_currency = excluded.settlement_currency,
                    dividend_method = excluded.dividend_method,
                    fund_type = excluded.fund_type,
                    updated_at = CURRENT_TIMESTAMP
            """, (
                holding.fund_code, holding.fund_name, holding.share_class,
                holding.fund_manager, holding.fund_account, holding.sales_agency,
                holding.trade_account, holding.holding_shares,
                holding.share_date.isoformat(), holding.nav,
                holding.nav_date.isoformat(), holding.asset_value,
                holding.settlement_currency, holding.dividend_method,
                holding.fund_type.value
            ))
            conn.commit()
            return True

    def get_fund_holdings(self, fund_account: Optional[str] = None) -> List[FundHolding]:
        """获取基金持有列表"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if fund_account:
                cursor.execute("""
                    SELECT * FROM fund_holdings
                    WHERE fund_account = ?
                    ORDER BY asset_value DESC
                """, (fund_account,))
            else:
                cursor.execute("""
                    SELECT * FROM fund_holdings
                    ORDER BY asset_value DESC
                """)

            return [self._row_to_fund_holding(row) for row in cursor.fetchall()]

    def get_fund_holding(self, fund_account: str, trade_account: str, fund_code: str) -> Optional[FundHolding]:
        """获取单条基金持有记录"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM fund_holdings
                WHERE fund_account = ? AND trade_account = ? AND fund_code = ?
            """, (fund_account, trade_account, fund_code))
            row = cursor.fetchone()
            return self._row_to_fund_holding(row) if row else None

    def clear_all_holdings(self) -> int:
        """清空所有持仓记录，返回删除的数量"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM fund_holdings")
            count = cursor.fetchone()['count']
            cursor.execute("DELETE FROM fund_holdings")
            conn.commit()
            return count

    def _row_to_fund_holding(self, row: sqlite3.Row) -> FundHolding:
        """将数据库行转换为FundHolding对象"""
        return FundHolding(
            id=row['id'],
            fund_code=row['fund_code'],
            fund_name=row['fund_name'],
            share_class=row['share_class'] or '',
            fund_manager=row['fund_manager'] or '',
            fund_account=row['fund_account'],
            sales_agency=row['sales_agency'] or '',
            trade_account=row['trade_account'],
            holding_shares=row['holding_shares'],
            share_date=date.fromisoformat(row['share_date']),
            nav=row['nav'],
            nav_date=date.fromisoformat(row['nav_date']),
            asset_value=row['asset_value'],
            settlement_currency=row['settlement_currency'] or '人民币',
            dividend_method=row['dividend_method'] or '',
            fund_type=FundType(row['fund_type'])
        )

    # ==================== FundInfo 操作 ====================

    def upsert_fund_info(self, info: FundInfo) -> bool:
        """插入或更新基金基础信息"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO fund_info (
                    fund_code, fund_name, fund_invest_type, risk_5_level,
                    nav, nav_date, net_asset, setup_date, yearly_roe,
                    one_year_return, setup_day_return, manager_names,
                    stock_ratio, bond_ratio, cash_ratio, data_update_time,
                    updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(fund_code)
                DO UPDATE SET
                    fund_name = excluded.fund_name,
                    fund_invest_type = excluded.fund_invest_type,
                    risk_5_level = excluded.risk_5_level,
                    nav = excluded.nav,
                    nav_date = excluded.nav_date,
                    net_asset = excluded.net_asset,
                    setup_date = excluded.setup_date,
                    yearly_roe = excluded.yearly_roe,
                    one_year_return = excluded.one_year_return,
                    setup_day_return = excluded.setup_day_return,
                    manager_names = excluded.manager_names,
                    stock_ratio = excluded.stock_ratio,
                    bond_ratio = excluded.bond_ratio,
                    cash_ratio = excluded.cash_ratio,
                    data_update_time = excluded.data_update_time,
                    updated_at = CURRENT_TIMESTAMP
            """, (
                info.fund_code, info.fund_name, info.fund_invest_type,
                info.risk_5_level, info.nav,
                info.nav_date.isoformat() if info.nav_date else None,
                info.net_asset,
                info.setup_date.isoformat() if info.setup_date else None,
                info.yearly_roe, info.one_year_return, info.setup_day_return,
                info.manager_names, info.stock_ratio, info.bond_ratio,
                info.cash_ratio,
                info.data_update_time.isoformat() if info.data_update_time else None
            ))
            conn.commit()
            return True

    def get_fund_info(self, fund_code: str) -> Optional[FundInfo]:
        """获取单条基金基础信息"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM fund_info WHERE fund_code = ?", (fund_code,))
            row = cursor.fetchone()
            return self._row_to_fund_info(row) if row else None

    def get_fund_infos(self, fund_codes: List[str] = None) -> List[FundInfo]:
        """获取基金基础信息列表"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if fund_codes:
                placeholders = ','.join('?' * len(fund_codes))
                cursor.execute(f"""
                    SELECT * FROM fund_info WHERE fund_code IN ({placeholders})
                """, fund_codes)
            else:
                cursor.execute("SELECT * FROM fund_info ORDER BY fund_code")

            return [self._row_to_fund_info(row) for row in cursor.fetchall()]

    def _row_to_fund_info(self, row: sqlite3.Row) -> FundInfo:
        """将数据库行转换为FundInfo对象"""
        return FundInfo(
            fund_code=row['fund_code'],
            fund_name=row['fund_name'],
            fund_invest_type=row['fund_invest_type'],
            risk_5_level=row['risk_5_level'],
            nav=row['nav'],
            nav_date=date.fromisoformat(row['nav_date']) if row['nav_date'] else None,
            net_asset=row['net_asset'],
            setup_date=date.fromisoformat(row['setup_date']) if row['setup_date'] else None,
            yearly_roe=row['yearly_roe'],
            one_year_return=row['one_year_return'],
            setup_day_return=row['setup_day_return'],
            manager_names=row['manager_names'],
            stock_ratio=row['stock_ratio'],
            bond_ratio=row['bond_ratio'],
            cash_ratio=row['cash_ratio'],
            data_update_time=datetime.fromisoformat(row['data_update_time']) if row['data_update_time'] else None
        )

    # ==================== FundHoldingsDetail 操作 ====================

    def upsert_fund_holdings_detail(self, detail: FundHoldingsDetail) -> bool:
        """插入或更新基金持仓详情"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # 序列化股票和债券持仓
            top_stocks_json = json.dumps([
                {'code': s.stock_code, 'name': s.stock_name,
                 'ratio': s.holding_ratio, 'amount': s.holding_amount}
                for s in detail.top_stocks
            ]) if detail.top_stocks else None

            top_bonds_json = json.dumps([
                {'code': b.bond_code, 'name': b.bond_name,
                 'ratio': b.holding_ratio, 'amount': b.holding_amount}
                for b in detail.top_bonds
            ]) if detail.top_bonds else None

            cursor.execute("""
                INSERT INTO fund_holdings_detail (
                    fund_code, report_date, stock_invest_ratio, bond_invest_ratio,
                    top_stocks, top_bonds, data_update_time, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(fund_code)
                DO UPDATE SET
                    report_date = excluded.report_date,
                    stock_invest_ratio = excluded.stock_invest_ratio,
                    bond_invest_ratio = excluded.bond_invest_ratio,
                    top_stocks = excluded.top_stocks,
                    top_bonds = excluded.top_bonds,
                    data_update_time = excluded.data_update_time,
                    updated_at = CURRENT_TIMESTAMP
            """, (
                detail.fund_code,
                detail.report_date.isoformat() if detail.report_date else None,
                detail.stock_invest_ratio, detail.bond_invest_ratio,
                top_stocks_json, top_bonds_json,
                detail.data_update_time.isoformat() if detail.data_update_time else None
            ))
            conn.commit()
            return True

    def get_fund_holdings_detail(self, fund_code: str) -> Optional[FundHoldingsDetail]:
        """获取基金持仓详情"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM fund_holdings_detail WHERE fund_code = ?
            """, (fund_code,))
            row = cursor.fetchone()
            return self._row_to_fund_holdings_detail(row) if row else None

    def _row_to_fund_holdings_detail(self, row: sqlite3.Row) -> FundHoldingsDetail:
        """将数据库行转换为FundHoldingsDetail对象"""
        top_stocks = []
        if row['top_stocks']:
            stocks_data = json.loads(row['top_stocks'])
            top_stocks = [
                StockHolding(
                    stock_code=s['code'],
                    stock_name=s['name'],
                    holding_ratio=s['ratio'],
                    holding_amount=s.get('amount')
                ) for s in stocks_data
            ]

        top_bonds = []
        if row['top_bonds']:
            bonds_data = json.loads(row['top_bonds'])
            top_bonds = [
                BondHolding(
                    bond_code=b['code'],
                    bond_name=b['name'],
                    holding_ratio=b['ratio'],
                    holding_amount=b.get('amount')
                ) for b in bonds_data
            ]

        return FundHoldingsDetail(
            fund_code=row['fund_code'],
            report_date=date.fromisoformat(row['report_date']) if row['report_date'] else None,
            stock_invest_ratio=row['stock_invest_ratio'],
            bond_invest_ratio=row['bond_invest_ratio'],
            top_stocks=top_stocks,
            top_bonds=top_bonds,
            data_update_time=datetime.fromisoformat(row['data_update_time']) if row['data_update_time'] else None
        )

    # ==================== 统计查询 ====================

    def get_statistics(self) -> Dict[str, Any]:
        """获取统计数据"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # 总资产
            cursor.execute("""
                SELECT COALESCE(SUM(asset_value), 0) as total
                FROM fund_holdings
            """)
            total_asset = cursor.fetchone()['total']

            # 基金数量
            cursor.execute("""
                SELECT COUNT(DISTINCT fund_code) as count FROM fund_holdings
            """)
            fund_count = cursor.fetchone()['count']

            # 持仓记录数
            cursor.execute("""
                SELECT COUNT(*) as count FROM fund_holdings
            """)
            holding_count = cursor.fetchone()['count']

            # 基金管理人分布
            cursor.execute("""
                SELECT fund_manager, COUNT(*) as count, SUM(asset_value) as total
                FROM fund_holdings
                GROUP BY fund_manager
                ORDER BY total DESC
            """)
            manager_distribution = {
                row['fund_manager']: {'count': row['count'], 'total': row['total']}
                for row in cursor.fetchall()
            }

            # 销售机构分布
            cursor.execute("""
                SELECT sales_agency, COUNT(*) as count, SUM(asset_value) as total
                FROM fund_holdings
                GROUP BY sales_agency
                ORDER BY total DESC
            """)
            sales_agency_distribution = {
                row['sales_agency']: {'count': row['count'], 'total': row['total']}
                for row in cursor.fetchall()
            }

            # 获取已有基础信息的基金代码
            cursor.execute("""
                SELECT COUNT(*) as count FROM fund_info
            """)
            info_count = cursor.fetchone()['count']

            # 获取已有持仓详情的基金代码
            cursor.execute("""
                SELECT COUNT(*) as count FROM fund_holdings_detail
            """)
            detail_count = cursor.fetchone()['count']

            # 投资类型分布（从fund_info表获取）
            cursor.execute("""
                SELECT
                    COALESCE(i.fund_invest_type, '未知') as invest_type,
                    COUNT(*) as count,
                    SUM(h.asset_value) as total
                FROM fund_holdings h
                LEFT JOIN fund_info i ON h.fund_code = i.fund_code
                GROUP BY i.fund_invest_type
                ORDER BY total DESC
            """)
            invest_type_distribution = {
                row['invest_type']: {'count': row['count'], 'total': row['total']}
                for row in cursor.fetchall()
            }

            return {
                'total_asset_value': total_asset,
                'fund_count': fund_count,
                'holding_count': holding_count,
                'manager_distribution': manager_distribution,
                'sales_agency_distribution': sales_agency_distribution,
                'invest_type_distribution': invest_type_distribution,
                'info_count': info_count,
                'detail_count': detail_count
            }

    def get_fund_codes_from_holdings(self) -> List[str]:
        """获取所有持仓中的基金代码"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT fund_code FROM fund_holdings ORDER BY fund_code
            """)
            return [row['fund_code'] for row in cursor.fetchall()]

    def get_missing_fund_info_codes(self) -> List[str]:
        """获取没有基础信息的基金代码"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT h.fund_code
                FROM fund_holdings h
                LEFT JOIN fund_info i ON h.fund_code = i.fund_code
                WHERE i.fund_code IS NULL
            """)
            return [row['fund_code'] for row in cursor.fetchall()]

    def get_missing_fund_detail_codes(self) -> List[str]:
        """获取没有持仓详情的基金代码"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT h.fund_code
                FROM fund_holdings h
                LEFT JOIN fund_holdings_detail d ON h.fund_code = d.fund_code
                WHERE d.fund_code IS NULL
            """)
            return [row['fund_code'] for row in cursor.fetchall()]