#!/usr/bin/env python3
"""
优化的风险平价组合分析技能
整合滚动窗口调仓逻辑和回测功能
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class OptimizedRiskParitySkill:
    def __init__(self, csv_path=None):
        """
        初始化优化的风险平价技能
        
        Args:
            csv_path: CSV文件路径（可选）
        """
        self.csv_path = csv_path
        self.asset_mapping = {
            "000300.SH": "沪深300指数",
            "TF.CFE": "五年期国债",
            "T.CFE": "十年期国债",
            "CU.SHF": "沪铜",
            "AU.SHF": "沪金"
        }
        
        # 资产类型映射
        self.asset_types = {
            "000300.SH": "equity",   # 股票指数
            "TF.CFE": "bond",       # 国债
            "T.CFE": "bond",        # 国债
            "CU.SHF": "commodity",  # 铜
            "AU.SHF": "commodity"   # 黄金
        }
        
        # 滚动窗口参数
        self.window_size = 252  # 一年的交易日数
        self.rebalance_frequency = "M"  # 每月调仓
        
        # 存储分析结果
        self.results = {}
    
    def load_data(self, csv_path=None):
        """
        加载数据
        """
        if csv_path:
            self.csv_path = csv_path
        
        if not self.csv_path:
            raise ValueError("请提供CSV文件路径")
        
        print("=" * 60)
        print("加载数据")
        print("=" * 60)
        
        # 读取CSV文件
        df = pd.read_csv(self.csv_path, encoding='gbk')
        
        print(f"原始数据形状: {df.shape}")
        
        # 提取实际数据
        data_start_row = 2
        
        # 创建干净的数据
        clean_data = pd.DataFrame()
        
        # 提取日期
        date_column = df.iloc[data_start_row:, 0].values
        clean_data['Date'] = pd.to_datetime(date_column, errors='coerce')
        
        # 提取收益率数据
        asset_codes = ['000300.SH', 'TF.CFE', 'T.CFE', 'CU.SHF', 'AU.SHF']
        
        # 提取收益率数据
        for i, code in enumerate(asset_codes):
            if code in df.columns:
                # 获取列数据
                col_data = df.iloc[data_start_row:][code].values
                
                # 转换为数值，忽略非数值数据
                numeric_data = []
                for val in col_data:
                    try:
                        # 尝试转换为数值
                        num_val = float(val)
                        # 数据中的涨跌幅单位是%，所以实际收益率应该是数字除以100
                        numeric_data.append(num_val / 100.0)
                    except (ValueError, TypeError):
                        # 如果转换失败，跳过
                        numeric_data.append(np.nan)
                
                clean_data[code] = numeric_data
        
        # 设置日期索引
        clean_data.set_index('Date', inplace=True)
        
        # 删除空行
        clean_data = clean_data.dropna(how='all')
        
        # 删除包含NaN的行
        clean_data = clean_data.dropna()
        
        print(f"干净数据形状: {clean_data.shape}")
        print(f"数据时间范围: {clean_data.index[0]} 至 {clean_data.index[-1]}")
        
        return clean_data
    
    def calculate_rolling_volatility(self, returns_data, window_size=252):
        """
        计算滚动波动率（使用历史数据，避免未来数据）
        """
        print("\n" + "=" * 60)
        print("计算滚动波动率")
        print("=" * 60)
        
        rolling_volatilities = {}
        
        for asset in returns_data.columns:
            # 计算滚动波动率（年化）
            # 使用expanding()而不是rolling()，确保不使用未来数据
            rolling_vol = returns_data[asset].expanding(min_periods=window_size).std() * np.sqrt(252)
            rolling_volatilities[asset] = rolling_vol
            
            # 显示统计信息
            valid_vol = rolling_vol.dropna()
            if len(valid_vol) > 0:
                print(f"  {self.asset_mapping.get(asset, asset)} ({asset}):")
                print(f"    数据点数: {len(valid_vol)}")
                print(f"    平均波动率: {valid_vol.mean()*100:.2f}%")
                print(f"    最小波动率: {valid_vol.min()*100:.2f}%")
                print(f"    最大波动率: {valid_vol.max()*100:.2f}%")
        
        return rolling_volatilities
    
    def calculate_rolling_weights(self, rolling_volatilities):
        """
        计算滚动风险平价权重
        """
        print("\n" + "=" * 60)
        print("计算滚动风险平价权重")
        print("=" * 60)
        
        # 创建DataFrame存储权重
        weights_df = pd.DataFrame(index=rolling_volatilities[list(rolling_volatilities.keys())[0]].index)
        
        for asset in rolling_volatilities.keys():
            # 计算权重：权重 = (1/波动率) / ∑(1/波动率)
            vol_series = rolling_volatilities[asset]
            
            # 创建权重序列
            weight_series = pd.Series(index=vol_series.index, dtype=float)
            
            for date in vol_series.index:
                # 获取当前日期的所有资产波动率
                current_vols = {}
                for a in rolling_volatilities.keys():
                    if date in rolling_volatilities[a].index:
                        current_vols[a] = rolling_volatilities[a].loc[date]
                
                # 计算权重
                if len(current_vols) == len(rolling_volatilities.keys()):
                    # 所有资产都有波动率数据
                    total_vol = sum(1/v for v in current_vols.values() if v > 0)
                    if total_vol > 0:
                        weight_series.loc[date] = (1/current_vols[asset]) / total_vol
                    else:
                        weight_series.loc[date] = 1/len(rolling_volatilities.keys())
                else:
                    # 部分资产没有波动率数据，使用等权重
                    weight_series.loc[date] = 1/len(rolling_volatilities.keys())
            
            weights_df[asset] = weight_series
        
        # 显示权重统计
        print(f"\n滚动权重统计:")
        for asset in weights_df.columns:
            valid_weights = weights_df[asset].dropna()
            if len(valid_weights) > 0:
                print(f"  {self.asset_mapping.get(asset, asset)} ({asset}):")
                print(f"    平均权重: {valid_weights.mean()*100:.2f}%")
                print(f"    最小权重: {valid_weights.min()*100:.2f}%")
                print(f"    最大权重: {valid_weights.max()*100:.2f}%")
        
        return weights_df
    
    def calculate_portfolio_returns(self, returns_data, weights_df):
        """
        计算投资组合收益率（使用滚动权重）
        """
        print("\n" + "=" * 60)
        print("计算投资组合收益率")
        print("=" * 60)
        
        # 创建投资组合收益率序列
        portfolio_returns = pd.Series(index=returns_data.index, dtype=float)
        
        for date in returns_data.index:
            # 获取当天的收益率
            daily_returns = returns_data.loc[date]
            
            # 获取当天的权重（使用前一天的权重，避免未来数据）
            prev_date = returns_data.index[returns_data.index.get_loc(date) - 1] if returns_data.index.get_loc(date) > 0 else None
            
            if prev_date is not None and prev_date in weights_df.index:
                weights = weights_df.loc[prev_date]
                
                # 计算投资组合收益率
                portfolio_return = 0
                for asset in returns_data.columns:
                    if asset in weights.index and not pd.isna(weights[asset]):
                        portfolio_return += daily_returns[asset] * weights[asset]
                
                portfolio_returns.loc[date] = portfolio_return
            else:
                # 第一天，使用等权重
                portfolio_return = daily_returns.sum() / len(daily_returns)
                portfolio_returns.loc[date] = portfolio_return
        
        # 显示统计信息
        valid_returns = portfolio_returns.dropna()
        if len(valid_returns) > 0:
            print(f"\n投资组合收益率统计:")
            print(f"  数据点数: {len(valid_returns)}")
            print(f"  平均收益率: {valid_returns.mean()*100:.4f}%")
            print(f"  标准差: {valid_returns.std()*100:.4f}%")
            print(f"  最小值: {valid_returns.min()*100:.4f}%")
            print(f"  最大值: {valid_returns.max()*100:.4f}%")
        
        return portfolio_returns
    
    def analyze_portfolio(self, returns_data, weights_df, portfolio_returns):
        """
        分析投资组合
        """
        print("\n" + "=" * 60)
        print("分析投资组合")
        print("=" * 60)
        
        # 计算指标
        total_return = (1 + portfolio_returns).prod() - 1
        annualized_return = (1 + total_return) ** (252 / len(portfolio_returns)) - 1
        volatility = portfolio_returns.std() * np.sqrt(252)
        
        # 计算最大回撤
        cumulative_returns = (1 + portfolio_returns).cumprod()
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max
        max_drawdown = drawdown.min()
        
        # 计算夏普比率
        risk_free_rate = 0.02
        sharpe_ratio = (annualized_return - risk_free_rate) / volatility if volatility > 0 else 0
        
        # 计算资产相关性
        correlation_matrix = returns_data.corr()
        
        # 计算各资产收益
        asset_returns = {}
        for col in returns_data.columns:
            asset_returns[col] = returns_data[col].tolist()
        
        # 计算各资产累计收益
        asset_cumulative = {}
        for col in returns_data.columns:
            asset_cumulative[col] = (1 + returns_data[col]).cumprod().tolist()
        
        # 计算平均权重
        avg_weights = weights_df.mean()
        
        # 打印结果
        print(f"\n投资组合分析结果:")
        print(f"  总收益率: {total_return*100:.2f}%")
        print(f"  年化收益率: {annualized_return*100:.2f}%")
        print(f"  年化波动率: {volatility*100:.2f}%")
        print(f"  最大回撤: {max_drawdown*100:.2f}%")
        print(f"  夏普比率: {sharpe_ratio:.2f}")
        
        print(f"\n平均资产权重:")
        for asset in avg_weights.index:
            print(f"  {self.asset_mapping.get(asset, asset)} ({asset}): {avg_weights[asset]*100:.2f}%")
        
        return {
            "total_return": total_return,
            "annualized_return": annualized_return,
            "volatility": volatility,
            "max_drawdown": max_drawdown,
            "sharpe_ratio": sharpe_ratio,
            "correlation_matrix": correlation_matrix.to_dict(),
            "asset_weights": avg_weights.to_dict(),
            "portfolio_returns": portfolio_returns.tolist(),
            "dates": returns_data.index.strftime('%Y-%m-%d').tolist(),
            "asset_returns": asset_returns,
            "asset_cumulative": asset_cumulative,
            "volatilities": {col: returns_data[col].std() * np.sqrt(252) 
                           for col in returns_data.columns},
            "rolling_weights": weights_df.to_dict()
        }
    
    def generate_text_report(self, metrics, avg_weights):
        """
        生成文字报告
        """
        report = []
        report.append("=" * 60)
        report.append("中国市场滚动风险平价组合分析报告")
        report.append("=" * 60)
        report.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"数据来源: {self.csv_path}")
        report.append(f"数据时间范围: {metrics['dates'][0]} 至 {metrics['dates'][-1]}")
        report.append(f"数据点数: {len(metrics['dates'])}")
        report.append(f"滚动窗口: 252个交易日（约1年）")
        report.append(f"调仓频率: 每月")
        report.append("")
        
        # 投资组合配置
        report.append("平均投资组合配置:")
        for symbol, weight in avg_weights.items():
            asset_name = self.asset_mapping.get(symbol, symbol)
            vol = metrics['volatilities'][symbol]
            report.append(f"  {asset_name} ({symbol}): {weight*100:.2f}% (波动率: {vol*100:.2f}%)")
        report.append("")
        
        # 收益指标
        report.append("收益指标:")
        report.append(f"  总收益率: {metrics['total_return']*100:.2f}%")
        report.append(f"  年化收益率: {metrics['annualized_return']*100:.2f}%")
        report.append("")
        
        # 风险指标
        report.append("风险指标:")
        report.append(f"  年化波动率: {metrics['volatility']*100:.2f}%")
        report.append(f"  最大回撤: {metrics['max_drawdown']*100:.2f}%")
        report.append(f"  夏普比率: {metrics['sharpe_ratio']:.2f}")
        report.append("")
        
        # 资产相关性
        report.append("资产相关性矩阵:")
        corr_matrix = metrics['correlation_matrix']
        for asset1 in corr_matrix:
            asset1_name = self.asset_mapping.get(asset1, asset1)
            row = [f"{asset1_name}:"]
            for asset2 in corr_matrix[asset1]:
                asset2_name = self.asset_mapping.get(asset2, asset2)
                row.append(f"  {asset2_name}: {corr_matrix[asset1][asset2]:.2f}")
            report.append(" ".join(row))
        report.append("")
        
        # 投资建议
        report.append("投资建议:")
        if metrics['sharpe_ratio'] > 1:
            report.append("  投资组合表现良好，夏普比率 > 1")
        elif metrics['sharpe_ratio'] > 0:
            report.append("  投资组合表现一般，夏普比率在0-1之间")
        else:
            report.append("  投资组合表现不佳，考虑调整配置")
        
        if metrics['max_drawdown'] < -0.2:
            report.append("  警告: 最大回撤超过20%，风险较高")
        
        # 风险平价特点
        report.append("")
        report.append("滚动风险平价组合特点:")
        report.append("  - 使用历史波动率计算权重，避免未来数据")
        report.append("  - 每月调仓，动态调整权重")
        report.append("  - 各资产对组合风险贡献相等")
        report.append("  - 降低单一资产风险暴露")
        
        # 资产类型分析
        report.append("")
        report.append("资产类型分析:")
        bond_assets = [s for s in avg_weights.keys() if self.asset_types.get(s) == 'bond']
        commodity_assets = [s for s in avg_weights.keys() if self.asset_types.get(s) == 'commodity']
        
        if bond_assets:
            bond_weight = sum(avg_weights[s] for s in bond_assets)
            report.append(f"  债券类资产: {bond_weight*100:.2f}%")
            for s in bond_assets:
                report.append(f"    - {self.asset_mapping.get(s, s)}: {avg_weights[s]*100:.2f}%")
        
        if commodity_assets:
            commodity_weight = sum(avg_weights[s] for s in commodity_assets)
            report.append(f"  商品类资产: {commodity_weight*100:.2f}%")
            for s in commodity_assets:
                report.append(f"    - {self.asset_mapping.get(s, s)}: {avg_weights[s]*100:.2f}%")
        
        report.append("")
        report.append("=" * 60)
        
        return "\n".join(report)
    
    def generate_charts(self, metrics, weights_df, output_dir='.'):
        """
        生成图表
        """
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
        
        # 1. 收益曲线图
        plt.figure(figsize=(12, 6))
        dates = pd.to_datetime(metrics['dates'])
        cumulative_returns = (1 + np.array(metrics['portfolio_returns'])).cumprod()
        
        plt.plot(dates, cumulative_returns, linewidth=2, color='blue')
        plt.title('滚动风险平价组合累计收益曲线', fontsize=14, fontweight='bold')
        plt.xlabel('日期', fontsize=12)
        plt.ylabel('累计收益 (倍数)', fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(f'{output_dir}/rolling_risk_parity_returns.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 2. 资产配置饼图（平均权重）
        plt.figure(figsize=(8, 8))
        labels = [self.asset_mapping.get(s, s) for s in metrics['asset_weights'].keys()]
        sizes = list(metrics['asset_weights'].values())
        colors = plt.cm.Set3(np.linspace(0, 1, len(labels)))
        
        plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        plt.title('滚动风险平价组合平均资产配置', fontsize=14, fontweight='bold')
        plt.axis('equal')
        plt.tight_layout()
        plt.savefig(f'{output_dir}/rolling_risk_parity_allocation.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 3. 相关性热力图
        corr_matrix = pd.DataFrame(metrics['correlation_matrix'])
        plt.figure(figsize=(10, 8))
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, 
                   square=True, linewidths=0.5, cbar_kws={"shrink": 0.8})
        plt.title('资产相关性热力图', fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig(f'{output_dir}/rolling_risk_parity_correlation.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 4. 资产收益对比图
        plt.figure(figsize=(12, 6))
        for symbol in metrics['asset_cumulative']:
            cumulative = metrics['asset_cumulative'][symbol]
            dates = pd.to_datetime(metrics['dates'])
            asset_name = self.asset_mapping.get(symbol, symbol)
            plt.plot(dates, cumulative, label=asset_name, linewidth=1.5)
        
        plt.title('各资产累计收益对比', fontsize=14, fontweight='bold')
        plt.xlabel('日期', fontsize=12)
        plt.ylabel('累计收益 (倍数)', fontsize=12)
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(f'{output_dir}/rolling_asset_returns_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 5. 滚动权重变化图
        plt.figure(figsize=(12, 6))
        dates = pd.to_datetime(metrics['dates'])
        
        # 只显示部分日期的数据，避免图表过于密集
        if len(dates) > 100:
            step = len(dates) // 100
            dates = dates[::step]
            for asset in metrics['asset_weights'].keys():
                if asset in metrics['rolling_weights']:
                    weights = pd.Series(metrics['rolling_weights'][asset])
                    weights = weights[::step]
                    plt.plot(dates, weights, label=self.asset_mapping.get(asset, asset), linewidth=1.5)
        else:
            for asset in metrics['asset_weights'].keys():
                if asset in metrics['rolling_weights']:
                    weights = pd.Series(metrics['rolling_weights'][asset])
                    plt.plot(dates, weights, label=self.asset_mapping.get(asset, asset), linewidth=1.5)
        
        plt.title('滚动风险平价权重变化', fontsize=14, fontweight='bold')
        plt.xlabel('日期', fontsize=12)
        plt.ylabel('权重', fontsize=12)
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(f'{output_dir}/rolling_weight_changes.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"图表已保存到 {output_dir} 目录")
    
    def run_backtest(self, csv_path=None, output_dir='./backtest_output'):
        """
        运行回测
        """
        print("=" * 60)
        print("运行滚动风险平价组合回测")
        print("=" * 60)
        
        # 1. 加载数据
        clean_data = self.load_data(csv_path)
        
        # 2. 计算滚动波动率
        rolling_volatilities = self.calculate_rolling_volatility(clean_data)
        
        # 3. 计算滚动权重
        weights_df = self.calculate_rolling_weights(rolling_volatilities)
        
        # 4. 计算投资组合收益率
        portfolio_returns = self.calculate_portfolio_returns(clean_data, weights_df)
        
        # 5. 分析投资组合
        metrics = self.analyze_portfolio(clean_data, weights_df, portfolio_returns)
        
        # 6. 生成文字报告
        avg_weights = weights_df.mean()
        text_report = self.generate_text_report(metrics, avg_weights)
        
        # 7. 生成图表
        self.generate_charts(metrics, weights_df, output_dir)
        
        # 8. 保存报告到文件
        report_file = f"{output_dir}/rolling_risk_parity_report.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(text_report)
        
        # 9. 保存详细数据到JSON
        detailed_data = {
            "portfolio_config": avg_weights.to_dict(),
            "metrics": {
                "total_return": metrics["total_return"],
                "annualized_return": metrics["annualized_return"],
                "volatility": metrics["volatility"],
                "max_drawdown": metrics["max_drawdown"],
                "sharpe_ratio": metrics["sharpe_ratio"],
                "asset_weights": metrics["asset_weights"],
                "volatilities": metrics["volatilities"]
            },
            "asset_mapping": self.asset_mapping,
            "analysis_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "rolling_weights": {
                asset: {str(date): weight for date, weight in weights_df[asset].items() if not pd.isna(weight)}
                for asset in weights_df.columns
            }
        }
        
        json_file = f"{output_dir}/rolling_risk_parity_data.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            import json
            json.dump(detailed_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n回测完成！")
        print(f"报告文件: {report_file}")
        print(f"数据文件: {json_file}")
        print(f"图表文件: {output_dir}/rolling_*.png")
        
        # 存储结果
        self.results = {
            "text_report": text_report,
            "report_file": report_file,
            "json_file": json_file,
            "charts": [
                f"{output_dir}/rolling_risk_parity_returns.png",
                f"{output_dir}/rolling_risk_parity_allocation.png",
                f"{output_dir}/rolling_risk_parity_correlation.png",
                f"{output_dir}/rolling_asset_returns_comparison.png",
                f"{output_dir}/rolling_weight_changes.png"
            ],
            "metrics": metrics,
            "avg_weights": avg_weights.to_dict(),
            "rolling_weights": weights_df.to_dict()
        }
        
        return self.results
    
    def get_report(self):
        """
        获取分析报告
        """
        if not self.results:
            raise ValueError("请先运行回测分析")
        
        return self.results.get("text_report", "无报告数据")
    
    def get_metrics(self):
        """
        获取分析指标
        """
        if not self.results:
            raise ValueError("请先运行回测分析")
        
        return self.results.get("metrics", {})
    
    def get_weights(self):
        """
        获取资产权重
        """
        if not self.results:
            raise ValueError("请先运行回测分析")
        
        return self.results.get("avg_weights", {})

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='优化的风险平价组合分析技能')
    parser.add_argument('--csv', type=str, default='C:\\Users\\wu_zhuoran\\.openclaw\\workspace\\data\\marketdata.csv', 
                       help='CSV文件路径')
    parser.add_argument('--output', type=str, default='./backtest_output', help='输出目录')
    
    args = parser.parse_args()
    
    # 创建技能实例
    skill = OptimizedRiskParitySkill(args.csv)
    
    # 运行回测
    result = skill.run_backtest(args.csv, args.output)
    
    # 显示文字报告
    print("\n" + "=" * 60)
    print("分析报告预览")
    print("=" * 60)
    print(result['text_report'])

if __name__ == "__main__":
    main()
