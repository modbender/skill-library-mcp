"""
基金持仓管理系统 - MCP数据获取服务
通过mcporter CLI调用qieman-mcp服务器获取基金数据
"""
import json
import subprocess
from datetime import datetime, date
from typing import List, Optional, Tuple

from src.models import FundInfo, FundHoldingsDetail, StockHolding, BondHolding


class MCPService:
    """MCP数据服务类"""

    def __init__(self, mcporter_path: str = "mcporter", batch_size: int = 10):
        self.mcporter_path = mcporter_path
        self.batch_size = min(batch_size, 10)

    def _execute_mcporter(self, tool: str, args: dict) -> Optional[dict]:
        """执行mcporter命令"""
        try:
            cmd = [
                self.mcporter_path, "call",
                f"qieman-mcp.{tool}",
                "--args", json.dumps(args),
                "--output", "json"
            ]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                print(f"Error calling {tool}: {result.stderr}")
                return None
        except subprocess.TimeoutExpired:
            print(f"Timeout calling {tool}")
            return None
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            return None
        except Exception as e:
            print(f"Exception calling {tool}: {e}")
            return None

    def get_funds_detail(self, fund_codes: List[str]) -> List[FundInfo]:
        """
        批量获取基金详细信息

        Args:
            fund_codes: 基金代码列表，最多10个每批

        Returns:
            FundInfo列表
        """
        if not fund_codes:
            return []

        results = []
        batch_size = self.batch_size

        for i in range(0, len(fund_codes), batch_size):
            batch = fund_codes[i:i + batch_size]
            data = self._execute_mcporter("BatchGetFundsDetail", {"fundCodes": batch})

            if data:
                for item in data:
                    if item.get("data"):
                        fund_info = self._parse_fund_detail(item["data"])
                        if fund_info:
                            results.append(fund_info)

        return results

    def _parse_fund_detail(self, data: dict) -> Optional[FundInfo]:
        """解析基金详情数据"""
        try:
            summary = data.get("summary", {})

            # 解析基金经理
            manager_names = ""
            managers = data.get("managers", [])
            if managers:
                manager_names = ",".join([m.get("fundManagerName", "") for m in managers])

            # 解析资产配置
            asset_portfolios = data.get("assetPortfolios", [])
            stock_ratio = None
            bond_ratio = None
            cash_ratio = None

            for ap in asset_portfolios:
                name = ap.get("name", "")
                ratio = ap.get("ratio")
                if name == "股票":
                    stock_ratio = ratio
                elif name == "债券":
                    bond_ratio = ratio
                elif name == "现金":
                    cash_ratio = ratio

            # 解析日期
            nav_date = None
            if summary.get("navDate"):
                try:
                    nav_date_str = summary["navDate"].replace("年", "-").replace("月", "-").replace("日", "")
                    nav_date = date.fromisoformat(nav_date_str)
                except:
                    pass

            setup_date = None
            if summary.get("setupDate"):
                try:
                    setup_date = date.fromtimestamp(summary["setupDate"] / 1000)
                except:
                    pass

            # 解析收益率（去掉%符号）
            yearly_roe = None
            if summary.get("yearlyRoe"):
                try:
                    yearly_roe = float(summary["yearlyRoe"].replace("%", ""))
                except:
                    pass

            one_year_return = None
            if summary.get("oneYearReturn"):
                try:
                    one_year_return = float(summary["oneYearReturn"].replace("%", ""))
                except:
                    pass

            setup_day_return = None
            if summary.get("setupDayReturn"):
                try:
                    setup_day_return = float(summary["setupDayReturn"].replace("%", ""))
                except:
                    pass

            # 解析基金规模
            net_asset = None
            if summary.get("netAsset"):
                try:
                    na = summary["netAsset"]
                    if "亿" in str(na):
                        net_asset = float(str(na).replace("亿", ""))
                except:
                    pass

            return FundInfo(
                fund_code=summary.get("fundCode", ""),
                fund_name=summary.get("fundName", ""),
                fund_invest_type=summary.get("fundInvestType"),
                risk_5_level=summary.get("risk5Level"),
                nav=summary.get("nav"),
                nav_date=nav_date,
                net_asset=net_asset,
                setup_date=setup_date,
                yearly_roe=yearly_roe,
                one_year_return=one_year_return,
                setup_day_return=setup_day_return,
                manager_names=manager_names,
                stock_ratio=stock_ratio,
                bond_ratio=bond_ratio,
                cash_ratio=cash_ratio,
                data_update_time=datetime.now()
            )
        except Exception as e:
            print(f"Error parsing fund detail: {e}")
            return None

    def get_funds_holding(self, fund_codes: List[str], fund_report_date: Optional[int] = None) -> List[FundHoldingsDetail]:
        """
        批量获取基金持仓情况

        Args:
            fund_codes: 基金代码列表，最多10个每批
            fund_report_date: 报告日期（可选）

        Returns:
            FundHoldingsDetail列表
        """
        if not fund_codes:
            return []

        results = []
        batch_size = self.batch_size

        for i in range(0, len(fund_codes), batch_size):
            batch = fund_codes[i:i + batch_size]
            args = {"fundCodes": batch}
            if fund_report_date:
                args["fundReportDate"] = fund_report_date

            data = self._execute_mcporter("BatchGetFundsHolding", args)

            if data:
                for item in data:
                    if item.get("data"):
                        detail = self._parse_fund_holding(item["data"])
                        if detail:
                            results.append(detail)

        return results

    def _parse_fund_holding(self, data: dict) -> Optional[FundHoldingsDetail]:
        """解析基金持仓数据"""
        try:
            # 解析报告日期
            report_date = None
            if data.get("reportDate"):
                try:
                    report_date_str = data["reportDate"].replace("年", "-").replace("月", "-").replace("日", "")
                    report_date = date.fromisoformat(report_date_str)
                except:
                    pass

            # 解析股票投资比例
            stock_invest_ratio = None
            if data.get("stockInvestRatio"):
                try:
                    stock_invest_ratio = float(data["stockInvestRatio"].replace("%", ""))
                except:
                    pass

            # 解析债券投资比例
            bond_invest_ratio = None
            if data.get("bondInvestRatio"):
                try:
                    bond_invest_ratio = float(data["bondInvestRatio"].replace("%", ""))
                except:
                    pass

            # 解析十大重仓股
            top_stocks = []
            for stock in data.get("stockInvests", []):
                try:
                    ratio = None
                    if stock.get("ratio"):
                        ratio = float(stock["ratio"].replace("%", ""))

                    amount = None
                    if stock.get("amount"):
                        try:
                            amount = float(stock["amount"].replace("亿", ""))
                        except:
                            pass

                    top_stocks.append(StockHolding(
                        stock_code=stock.get("code", ""),
                        stock_name=stock.get("name", ""),
                        holding_ratio=ratio,
                        holding_amount=amount
                    ))
                except Exception as e:
                    print(f"Error parsing stock holding: {e}")

            # 解析十大重仓债
            top_bonds = []
            for bond in data.get("bondInvests", []):
                try:
                    ratio = None
                    if bond.get("ratio"):
                        ratio = float(bond["ratio"].replace("%", ""))

                    amount = None
                    if bond.get("amount"):
                        try:
                            amount = float(bond["amount"].replace("亿", ""))
                        except:
                            pass

                    top_bonds.append(BondHolding(
                        bond_code=bond.get("code", ""),
                        bond_name=bond.get("name", ""),
                        holding_ratio=ratio,
                        holding_amount=amount
                    ))
                except Exception as e:
                    print(f"Error parsing bond holding: {e}")

            return FundHoldingsDetail(
                fund_code=data.get("fundCode", ""),
                report_date=report_date,
                stock_invest_ratio=stock_invest_ratio,
                bond_invest_ratio=bond_invest_ratio,
                top_stocks=top_stocks,
                top_bonds=top_bonds,
                data_update_time=datetime.now()
            )
        except Exception as e:
            print(f"Error parsing fund holding: {e}")
            return None

    def sync_fund_info(self, fund_codes: List[str], database) -> Tuple[int, int]:
        """
        同步基金基础信息到数据库

        Args:
            fund_codes: 基金代码列表
            database: 数据库实例

        Returns:
            (成功数量, 失败数量)
        """
        success_count = 0
        fail_count = 0

        fund_infos = self.get_funds_detail(fund_codes)

        for info in fund_infos:
            try:
                database.upsert_fund_info(info)
                success_count += 1
            except Exception as e:
                print(f"Error saving fund info {info.fund_code}: {e}")
                fail_count += 1

        # 计算未成功获取的数量
        fail_count += len(fund_codes) - len(fund_infos)

        return success_count, fail_count

    def sync_fund_holdings(self, fund_codes: List[str], database) -> Tuple[int, int]:
        """
        同步基金持仓信息到数据库

        Args:
            fund_codes: 基金代码列表
            database: 数据库实例

        Returns:
            (成功数量, 失败数量)
        """
        success_count = 0
        fail_count = 0

        details = self.get_funds_holding(fund_codes)

        for detail in details:
            try:
                database.upsert_fund_holdings_detail(detail)
                success_count += 1
            except Exception as e:
                print(f"Error saving fund holdings detail {detail.fund_code}: {e}")
                fail_count += 1

        fail_count += len(fund_codes) - len(details)

        return success_count, fail_count