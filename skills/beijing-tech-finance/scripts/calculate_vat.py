#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
北京市科技公司增值税计算脚本

功能：
- 计算一般纳税人增值税应纳税额
- 计算小规模纳税人增值税应纳税额  
- 处理软件企业即征即退计算
- 生成增值税申报表基础数据
"""

import sys
import json
from decimal import Decimal, ROUND_HALF_UP

def calculate_general_vat(sales_amount, input_tax, export_sales=0):
    """
    计算一般纳税人增值税
    
    Args:
        sales_amount (Decimal): 销项税额（含税销售额）
        input_tax (Decimal): 进项税额
        export_sales (Decimal): 免税出口销售额（默认0）
    
    Returns:
        dict: 包含应纳税额、销项税、进项税等信息
    """
    # 销项税额计算（假设税率13%）
    output_tax = sales_amount * Decimal('0.13')
    
    # 应纳税额 = 销项税额 - 进项税额
    payable_tax = output_tax - input_tax
    
    if payable_tax < 0:
        # 形成留抵税额
        carry_forward = abs(payable_tax)
        payable_tax = Decimal('0')
    else:
        carry_forward = Decimal('0')
    
    return {
        'output_tax': float(output_tax.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
        'input_tax': float(input_tax.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
        'payable_tax': float(payable_tax.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
        'carry_forward': float(carry_forward.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
        'export_sales': float(export_sales.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
    }

def calculate_small_scale_vat(sales_amount, quarterly=True):
    """
    计算小规模纳税人增值税
    
    Args:
        sales_amount (Decimal): 季度/月度销售额
        quarterly (bool): 是否为季度计算（默认True）
    
    Returns:
        dict: 增值税计算结果
    """
    # 小规模纳税人免税政策：季度销售额≤30万（月度≤10万）免征增值税
    threshold = Decimal('300000') if quarterly else Decimal('100000')
    
    if sales_amount <= threshold:
        return {
            'sales_amount': float(sales_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'tax_rate': 0.01,  # 名义税率1%
            'payable_tax': 0.0,
            'is_exempt': True,
            'threshold': float(threshold.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
        }
    else:
        # 超过免税额度，按1%征收率计算
        payable_tax = sales_amount * Decimal('0.01')
        return {
            'sales_amount': float(sales_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'tax_rate': 0.01,
            'payable_tax': float(payable_tax.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'is_exempt': False,
            'threshold': float(threshold.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
        }

def calculate_software_refund(sales_amount, actual_tax_burden):
    """
    计算软件企业增值税即征即退
    
    Args:
        sales_amount (Decimal): 软件产品销售额
        actual_tax_burden (Decimal): 实际税负率（如0.05表示5%）
    
    Returns:
        dict: 即征即退计算结果
    """
    # 增值税销项税额（13%税率）
    output_tax = sales_amount * Decimal('0.13')
    
    # 实际缴纳增值税
    actual_vat = sales_amount * actual_tax_burden
    
    # 即征即退金额（超过3%部分）
    if actual_tax_burden > Decimal('0.03'):
        refund_amount = actual_vat - (sales_amount * Decimal('0.03'))
    else:
        refund_amount = Decimal('0')
    
    return {
        'sales_amount': float(sales_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
        'output_tax': float(output_tax.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
        'actual_vat': float(actual_vat.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
        'actual_tax_burden': float(actual_tax_burden),
        'refund_amount': float(refund_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
        'refund_eligible': actual_tax_burden > Decimal('0.03')
    }

def main():
    """命令行接口"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python calculate_vat.py general <sales> <input_tax> [export_sales]")
        print("  python calculate_vat.py small <sales> [--monthly]")
        print("  python calculate_vat.py software <sales> <tax_burden>")
        sys.exit(1)
    
    mode = sys.argv[1]
    
    try:
        if mode == "general":
            if len(sys.argv) < 4:
                print("需要提供销售额和进项税额")
                sys.exit(1)
            sales = Decimal(sys.argv[2])
            input_tax = Decimal(sys.argv[3])
            export_sales = Decimal(sys.argv[4]) if len(sys.argv) > 4 else Decimal('0')
            result = calculate_general_vat(sales, input_tax, export_sales)
            
        elif mode == "small":
            if len(sys.argv) < 3:
                print("需要提供销售额")
                sys.exit(1)
            sales = Decimal(sys.argv[2])
            quarterly = "--monthly" not in sys.argv
            result = calculate_small_scale_vat(sales, quarterly)
            
        elif mode == "software":
            if len(sys.argv) < 4:
                print("需要提供销售额和实际税负率")
                sys.exit(1)
            sales = Decimal(sys.argv[2])
            tax_burden = Decimal(sys.argv[3])
            result = calculate_software_refund(sales, tax_burden)
            
        else:
            print(f"不支持的模式: {mode}")
            sys.exit(1)
        
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    except Exception as e:
        print(f"计算错误: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()