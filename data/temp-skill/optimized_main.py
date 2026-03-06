#!/usr/bin/env python3
"""
优化的金融分析技能主脚本
整合滚动窗口调仓逻辑和回测功能
"""

import argparse
import sys
import os
from datetime import datetime

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from optimized_risk_parity_skill import OptimizedRiskParitySkill

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='优化的金融分析技能 - 滚动窗口风险平价组合分析',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  # 运行回测分析
  python optimized_main.py --csv "C:\path\to\marketdata.csv" --output ./backtest_output
  
  # 使用默认数据路径
  python optimized_main.py
  
  # 自定义输出目录
  python optimized_main.py --output ./my_backtest
        '''
    )
    
    parser.add_argument('--csv', type=str, 
                       default=r'C:\Users\wu_zhuoran\.openclaw\workspace\data\marketdata.csv',
                       help='CSV文件路径（包含收益率数据）')
    
    parser.add_argument('--output', type=str, default='./backtest_output',
                       help='输出目录（用于保存报告和图表）')
    
    parser.add_argument('--show-report', action='store_true',
                       help='显示分析报告')
    
    parser.add_argument('--show-metrics', action='store_true',
                       help='显示分析指标')
    
    parser.add_argument('--show-weights', action='store_true',
                       help='显示资产权重')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("优化的金融分析技能 - 滚动窗口风险平价组合分析")
    print("=" * 60)
    print(f"数据文件: {args.csv}")
    print(f"输出目录: {args.output}")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("")
    
    # 创建技能实例
    skill = OptimizedRiskParitySkill(args.csv)
    
    try:
        # 运行回测
        result = skill.run_backtest(args.csv, args.output)
        
        print("\n" + "=" * 60)
        print("分析完成！")
        print("=" * 60)
        
        # 显示分析报告
        if args.show_report:
            print("\n" + "=" * 60)
            print("分析报告")
            print("=" * 60)
            print(result['text_report'])
        
        # 显示分析指标
        if args.show_metrics:
            print("\n" + "=" * 60)
            print("分析指标")
            print("=" * 60)
            metrics = skill.get_metrics()
            if metrics:
                print(f"总收益率: {metrics.get('total_return', 0)*100:.2f}%")
                print(f"年化收益率: {metrics.get('annualized_return', 0)*100:.2f}%")
                print(f"年化波动率: {metrics.get('volatility', 0)*100:.2f}%")
                print(f"最大回撤: {metrics.get('max_drawdown', 0)*100:.2f}%")
                print(f"夏普比率: {metrics.get('sharpe_ratio', 0):.2f}")
        
        # 显示资产权重
        if args.show_weights:
            print("\n" + "=" * 60)
            print("资产权重")
            print("=" * 60)
            weights = skill.get_weights()
            if weights:
                for asset, weight in weights.items():
                    asset_name = skill.asset_mapping.get(asset, asset)
                    print(f"{asset_name} ({asset}): {weight*100:.2f}%")
        
        # 显示输出文件信息
        print("\n" + "=" * 60)
        print("输出文件")
        print("=" * 60)
        print(f"报告文件: {result['report_file']}")
        print(f"数据文件: {result['json_file']}")
        print(f"图表文件: {result['charts']}")
        
        print("\n" + "=" * 60)
        print("完成时间: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        print("=" * 60)
        
    except Exception as e:
        print(f"\n错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
