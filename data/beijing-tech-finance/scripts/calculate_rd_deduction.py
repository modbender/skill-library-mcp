#!/usr/bin/env python3
"""
北京市科技公司研发费用加计扣除计算器
支持高新技术企业100%加计扣除计算
"""

def calculate_rd_deduction(revenue, rd_expenses, company_type="tech_sme"):
    """
    计算研发费用加计扣除金额
    
    Args:
        revenue: 年度销售收入（元）
        rd_expenses: 研发费用总额（元）
        company_type: 企业类型 ("tech_sme"=科技型中小企业, "high_tech"=高新技术企业)
    
    Returns:
        dict: 包含扣除限额、实际可扣除金额等信息
    """
    # 确定扣除比例
    if company_type == "tech_sme":
        deduction_rate = 1.0  # 100%加计扣除
    elif company_type == "high_tech":
        deduction_rate = 1.0  # 高新技术企业也是100%
    else:
        deduction_rate = 0.75  # 一般企业75%
    
    # 计算最低研发投入要求
    if revenue <= 50_000_000:
        min_rd_ratio = 0.05
    elif revenue <= 200_000_000:
        min_rd_ratio = 0.04
    else:
        min_rd_ratio = 0.03
    
    required_rd = revenue * min_rd_ratio
    actual_rd_ratio = rd_expenses / revenue if revenue > 0 else 0
    
    # 计算可加计扣除金额
    # 注意：其他相关费用不超过研发费用总额的10%
    # 这里简化处理，假设所有费用都符合要求
    
    deductible_amount = rd_expenses * deduction_rate
    
    return {
        "revenue": revenue,
        "rd_expenses": rd_expenses,
        "actual_rd_ratio": actual_rd_ratio,
        "required_rd_ratio": min_rd_ratio,
        "required_rd_amount": required_rd,
        "meets_requirement": rd_expenses >= required_rd,
        "deduction_rate": deduction_rate,
        "deductible_amount": deductible_amount,
        "total_tax_benefit": deductible_amount * 0.25  # 按25%税率计算节税金额
    }

def format_result(result):
    """格式化输出结果"""
    print("=" * 50)
    print("研发费用加计扣除计算结果")
    print("=" * 50)
    print(f"年度销售收入: ¥{result['revenue']:,.2f}")
    print(f"研发费用总额: ¥{result['rd_expenses']:,.2f}")
    print(f"实际研发费用占比: {result['actual_rd_ratio']:.2%}")
    print(f"要求最低占比: {result['required_rd_ratio']:.2%}")
    print(f"要求最低金额: ¥{result['required_rd_amount']:,.2f}")
    print(f"是否满足要求: {'是' if result['meets_requirement'] else '否'}")
    print("-" * 50)
    print(f"加计扣除比例: {result['deduction_rate']:.0%}")
    print(f"可加计扣除金额: ¥{result['deductible_amount']:,.2f}")
    print(f"预计节税金额: ¥{result['total_tax_benefit']:,.2f}")
    print("=" * 50)

if __name__ == "__main__":
    # 示例使用
    import sys
    
    if len(sys.argv) != 4:
        print("用法: python calculate_rd_deduction.py <销售收入> <研发费用> <企业类型>")
        print("企业类型: tech_sme (科技型中小企业), high_tech (高新技术企业), normal (一般企业)")
        sys.exit(1)
    
    try:
        revenue = float(sys.argv[1])
        rd_expenses = float(sys.argv[2])
        company_type = sys.argv[3]
        
        result = calculate_rd_deduction(revenue, rd_expenses, company_type)
        format_result(result)
        
    except ValueError:
        print("错误: 请输入有效的数字")
        sys.exit(1)