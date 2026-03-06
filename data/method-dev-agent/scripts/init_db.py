# 初始化数据库脚本
import sys
sys.path.insert(0, 'src')

from database import Database

def init_database():
    """初始化数据库"""
    print("正在初始化数据库...")
    db = Database()
    
    # 添加示例数据
    from models import Compound, ChromatographicMethod
    
    # 添加示例化合物
    aspirin = Compound(
        name="阿司匹林",
        cas_number="50-78-2",
        molecular_formula="C9H8O4",
        mw=180.16,
        notes="常用解热镇痛药"
    )
    db.add_compound(aspirin)
    
    # 添加示例方法
    method = ChromatographicMethod(
        name="阿司匹林含量测定-UPLC法",
        description="参考药典方法",
        column_type="C18",
        column_model="Waters ACQUITY UPLC BEH",
        column_dimensions="2.1×100mm, 1.7μm",
        mobile_phase_a="0.1% 磷酸水溶液",
        mobile_phase_b="乙腈",
        gradient_program="10-90%B (0-5min)",
        flow_rate=0.4,
        column_temperature=35.0,
        injection_volume=2.0,
        detection_wavelength=228.0,
        detection_method="UV",
        target_compound="阿司匹林",
        sample_matrix="片剂",
        created_by="Teagee",
        tags="含量测定,药典,UPLC"
    )
    db.add_method(method)
    
    print("[OK] 数据库初始化完成！")
    print(f"[STATS] 统计：{db.get_stats()}")

if __name__ == '__main__':
    init_database()
