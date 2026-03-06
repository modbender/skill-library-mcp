"""
基金持仓管理系统 - 统计视图功能
"""
from datetime import datetime
from typing import Dict, List, Any, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from src.database import Database
from src.models import FundHolding, FundInfo, FundHoldingsDetail


class Statistics:
    """统计视图类"""

    def __init__(self, database: Database):
        self.database = database
        self.console = Console()

    def show_overview(self):
        """显示总览视图"""
        stats = self.database.get_statistics()

        # 创建总览面板
        total_asset = stats['total_asset_value']
        fund_count = stats['fund_count']
        holding_count = stats['holding_count']

        overview_text = f"""
[bold cyan]总资产价值:[/] ¥{total_asset:,.2f}
[bold cyan]持仓基金数:[/] {fund_count} 只
[bold cyan]持仓记录数:[/] {holding_count} 条
[bold cyan]基金基础信息:[/] {stats['info_count']} 条
[bold cyan]基金持仓详情:[/] {stats['detail_count']} 条
"""
        self.console.print(Panel(overview_text, title="[bold green]投资组合总览[/]", border_style="green"))

    def show_manager_distribution(self, limit: int = 10):
        """显示基金管理人分布"""
        stats = self.database.get_statistics()
        manager_dist = stats['manager_distribution']

        if not manager_dist:
            self.console.print("[yellow]暂无基金管理人分布数据[/]")
            return

        table = Table(title=f"基金管理人分布 (Top {limit})", show_header=True, header_style="bold cyan")
        table.add_column("基金管理人", style="cyan")
        table.add_column("持仓数", justify="right", style="blue")
        table.add_column("资产价值", justify="right", style="green")
        table.add_column("占比", justify="right", style="yellow")

        total = sum(m['total'] for m in manager_dist.values())
        sorted_managers = sorted(manager_dist.items(), key=lambda x: x[1]['total'], reverse=True)[:limit]

        for manager, data in sorted_managers:
            percentage = (data['total'] / total * 100) if total > 0 else 0
            table.add_row(
                manager or "未知",
                str(data['count']),
                f"¥{data['total']:,.2f}",
                f"{percentage:.2f}%"
            )

        self.console.print(table)

    def show_sales_agency_distribution(self, limit: int = 10):
        """显示销售机构分布"""
        stats = self.database.get_statistics()
        agency_dist = stats['sales_agency_distribution']

        if not agency_dist:
            self.console.print("[yellow]暂无销售机构分布数据[/]")
            return

        table = Table(title=f"销售机构分布 (Top {limit})", show_header=True, header_style="bold cyan")
        table.add_column("销售机构", style="cyan")
        table.add_column("持仓数", justify="right", style="blue")
        table.add_column("资产价值", justify="right", style="green")
        table.add_column("占比", justify="right", style="yellow")

        total = sum(a['total'] for a in agency_dist.values())
        sorted_agencies = sorted(agency_dist.items(), key=lambda x: x[1]['total'], reverse=True)[:limit]

        for agency, data in sorted_agencies:
            percentage = (data['total'] / total * 100) if total > 0 else 0
            table.add_row(
                agency or "未知",
                str(data['count']),
                f"¥{data['total']:,.2f}",
                f"{percentage:.2f}%"
            )

        self.console.print(table)

    def show_invest_type_distribution(self):
        """显示投资类型分布"""
        stats = self.database.get_statistics()
        invest_dist = stats.get('invest_type_distribution', {})

        if not invest_dist:
            self.console.print("[yellow]暂无投资类型分布数据，请先运行 sync --info 同步基金信息[/]")
            return

        table = Table(title="投资类型分布", show_header=True, header_style="bold cyan")
        table.add_column("投资类型", style="cyan")
        table.add_column("持仓数", justify="right", style="blue")
        table.add_column("资产价值", justify="right", style="green")
        table.add_column("占比", justify="right", style="yellow")

        total = sum(i['total'] for i in invest_dist.values())
        sorted_types = sorted(invest_dist.items(), key=lambda x: x[1]['total'], reverse=True)

        for invest_type, data in sorted_types:
            percentage = (data['total'] / total * 100) if total > 0 else 0
            table.add_row(
                invest_type or "未知",
                str(data['count']),
                f"¥{data['total']:,.2f}",
                f"{percentage:.2f}%"
            )

        self.console.print(table)

    def show_holdings_list(self, fund_account: str = None, limit: int = 20):
        """显示持仓列表"""
        holdings = self.database.get_fund_holdings(fund_account)

        if not holdings:
            self.console.print("[yellow]暂无持仓数据[/]")
            return

        table = Table(title=f"持仓列表 (共{len(holdings)}条)", show_header=True, header_style="bold cyan")
        table.add_column("基金代码", style="cyan", width=10)
        table.add_column("基金名称", style="white", width=25)
        table.add_column("持有份额", justify="right", style="blue", width=12)
        table.add_column("净值", justify="right", style="yellow", width=8)
        table.add_column("资产价值", justify="right", style="green", width=12)
        table.add_column("销售机构", style="magenta", width=18)

        for holding in holdings[:limit]:
            table.add_row(
                holding.fund_code,
                holding.fund_name[:25] if len(holding.fund_name) > 25 else holding.fund_name,
                f"{holding.holding_shares:,.2f}",
                f"{holding.nav:.4f}",
                f"¥{holding.asset_value:,.2f}",
                holding.sales_agency[:18] if len(holding.sales_agency) > 18 else holding.sales_agency
            )

        if len(holdings) > limit:
            self.console.print(f"[dim]... 还有 {len(holdings) - limit} 条记录未显示[/]")

        self.console.print(table)

    def show_fund_detail(self, fund_code: str):
        """显示单个基金的详细信息"""
        # 获取基础信息
        fund_info = self.database.get_fund_info(fund_code)
        # 获取持仓详情
        holdings_detail = self.database.get_fund_holdings_detail(fund_code)
        # 获取用户持仓
        user_holdings = []
        all_holdings = self.database.get_fund_holdings()
        for h in all_holdings:
            if h.fund_code == fund_code:
                user_holdings.append(h)

        if not fund_info and not user_holdings:
            self.console.print(f"[red]未找到基金: {fund_code}[/]")
            return

        # 显示基金基础信息
        if fund_info:
            info_text = f"""
[bold cyan]基金代码:[/] {fund_info.fund_code}
[bold cyan]基金名称:[/] {fund_info.fund_name}
[bold cyan]投资类型:[/] {fund_info.fund_invest_type or '未知'}
[bold cyan]风险等级:[/] {fund_info.risk_5_level or '未知'}
[bold cyan]最新净值:[/] {fund_info.nav or '未知'} ({fund_info.nav_date or '未知'})
[bold cyan]基金规模:[/] {fund_info.net_asset}亿 ({fund_info.fund_invest_type or ''})
[bold cyan]成立日期:[/] {fund_info.setup_date or '未知'}
"""
            if fund_info.yearly_roe:
                info_text += f"[bold cyan]七日年化:[/] {fund_info.yearly_roe}%\n"
            if fund_info.one_year_return:
                info_text += f"[bold cyan]近一年收益:[/] {fund_info.one_year_return}%\n"
            if fund_info.manager_names:
                info_text += f"[bold cyan]基金经理:[/] {fund_info.manager_names}\n"

            self.console.print(Panel(info_text, title="[bold green]基金基础信息[/]", border_style="green"))

        # 显示用户持仓
        if user_holdings:
            table = Table(title="我的持仓", show_header=True, header_style="bold cyan")
            table.add_column("基金账户", style="cyan")
            table.add_column("交易账户", style="blue")
            table.add_column("持有份额", justify="right", style="green")
            table.add_column("资产价值", justify="right", style="yellow")

            for h in user_holdings:
                table.add_row(
                    h.fund_account,
                    h.trade_account,
                    f"{h.holding_shares:,.2f}",
                    f"¥{h.asset_value:,.2f}"
                )

            self.console.print(table)

        # 显示持仓详情
        if holdings_detail:
            detail_text = f"\n[bold cyan]报告日期:[/] {holdings_detail.report_date or '未知'}\n"
            if holdings_detail.stock_invest_ratio:
                detail_text += f"[bold cyan]股票仓位:[/] {holdings_detail.stock_invest_ratio}%\n"
            if holdings_detail.bond_invest_ratio:
                detail_text += f"[bold cyan]债券仓位:[/] {holdings_detail.bond_invest_ratio}%\n"

            self.console.print(Panel(detail_text, title="[bold green]持仓分析[/]", border_style="green"))

            # 显示十大重仓股
            if holdings_detail.top_stocks:
                stock_table = Table(title="十大重仓股", show_header=True, header_style="bold cyan")
                stock_table.add_column("代码", style="cyan", width=12)
                stock_table.add_column("名称", style="white", width=20)
                stock_table.add_column("占比", justify="right", style="green")
                stock_table.add_column("金额(亿)", justify="right", style="yellow")

                for stock in holdings_detail.top_stocks[:10]:
                    stock_table.add_row(
                        stock.stock_code,
                        stock.stock_name,
                        f"{stock.holding_ratio}%" if stock.holding_ratio else "-",
                        f"{stock.holding_amount}" if stock.holding_amount else "-"
                    )

                self.console.print(stock_table)

            # 显示十大重仓债
            if holdings_detail.top_bonds:
                bond_table = Table(title="十大重仓债", show_header=True, header_style="bold cyan")
                bond_table.add_column("代码", style="cyan", width=12)
                bond_table.add_column("名称", style="white", width=20)
                bond_table.add_column("占比", justify="right", style="green")
                bond_table.add_column("金额(亿)", justify="right", style="yellow")

                for bond in holdings_detail.top_bonds[:10]:
                    bond_table.add_row(
                        bond.bond_code,
                        bond.bond_name,
                        f"{bond.holding_ratio}%" if bond.holding_ratio else "-",
                        f"{bond.holding_amount}" if bond.holding_amount else "-"
                    )

                self.console.print(bond_table)

    def export_report(self, output_path: str = "report.txt"):
        """导出统计报告"""
        stats = self.database.get_statistics()

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("=" * 60 + "\n")
            f.write("基金持仓统计报告\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")

            f.write(f"总资产价值: ¥{stats['total_asset_value']:,.2f}\n")
            f.write(f"持仓基金数: {stats['fund_count']} 只\n")
            f.write(f"持仓记录数: {stats['holding_count']} 条\n\n")

            f.write("-" * 40 + "\n")
            f.write("基金管理人分布:\n")
            f.write("-" * 40 + "\n")
            for manager, data in sorted(stats['manager_distribution'].items(),
                                       key=lambda x: x[1]['total'], reverse=True):
                f.write(f"  {manager}: {data['count']}只, ¥{data['total']:,.2f}\n")

            f.write("\n" + "-" * 40 + "\n")
            f.write("销售机构分布:\n")
            f.write("-" * 40 + "\n")
            for agency, data in sorted(stats['sales_agency_distribution'].items(),
                                      key=lambda x: x[1]['total'], reverse=True):
                f.write(f"  {agency}: {data['count']}只, ¥{data['total']:,.2f}\n")

            f.write("\n" + "-" * 40 + "\n")
            f.write("投资类型分布:\n")
            f.write("-" * 40 + "\n")
            invest_dist = stats.get('invest_type_distribution', {})
            for invest_type, data in sorted(invest_dist.items(),
                                           key=lambda x: x[1]['total'], reverse=True):
                f.write(f"  {invest_type}: {data['count']}只, ¥{data['total']:,.2f}\n")

        self.console.print(f"[green]报告已导出到: {output_path}[/]")

    def show_all_stats(self):
        """显示所有统计视图"""
        self.console.print("\n" + "=" * 60 + "\n")
        self.show_overview()
        self.console.print("\n")
        self.show_invest_type_distribution()
        self.console.print("\n")
        self.show_manager_distribution()
        self.console.print("\n")
        self.show_sales_agency_distribution()