"""
Streamlit主应用
Method Development Agent - MVP
"""
import streamlit as st
import pandas as pd
from datetime import datetime
import json

try:
    from database import Database
    from models import Compound, ChromatographicMethod, Experiment
except ImportError:
    from src.database import Database
    from src.models import Compound, ChromatographicMethod, Experiment

# 页面配置
st.set_page_config(
    page_title="方法开发助手Agent",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化数据库
@st.cache_resource
def get_db():
    return Database()

db = get_db()

# 侧边栏导航
st.sidebar.title("🧪 方法开发助手")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "导航",
    ["🏠 首页", "➕ 新建实验", "📋 实验记录", "📊 方法库", "🔍 数据分析"]
)

st.sidebar.markdown("---")
st.sidebar.info("💡 **提示**：从'新建实验'开始记录您的色谱方法开发过程")

# ========== 首页 ==========
if page == "🏠 首页":
    st.title("🎯 方法开发助手Agent - MVP")
    
    col1, col2, col3, col4 = st.columns(4)
    
    stats = db.get_stats()
    
    with col1:
        st.metric("化合物", stats['compounds'])
    with col2:
        st.metric("方法", stats['methods'])
    with col3:
        st.metric("实验记录", stats['experiments'])
    with col4:
        st.metric("已完成", stats['completed_experiments'])
    
    st.markdown("---")
    
    st.markdown("""
    ## 🚀 快速开始
    
    这个Agent帮助您：
    - 📝 **记录实验** - 系统记录每次方法开发的参数和结果
    - 🔍 **检索方法** - 快速查找历史方法和实验记录
    - 📊 **分析趋势** - 追踪方法优化过程和关键参数
    - 💾 **知识沉淀** - 积累方法开发知识，团队共享
    
    ### 📖 使用流程
    1. 点击左侧「➕ 新建实验」创建实验记录
    2. 填写色谱条件、样品信息、结果数据
    3. 在「📋 实验记录」中查看和管理所有记录
    4. 使用「🔍 数据分析」查看趋势和统计
    """)
    
    # 显示最近的实验
    st.markdown("---")
    st.subheader("🕐 最近实验记录")
    
    recent_exps = db.get_experiments()[:5]
    if recent_exps:
        for exp in recent_exps:
            with st.container():
                col1, col2, col3 = st.columns([2, 2, 1])
                with col1:
                    st.write(f"**{exp.experiment_number}**: {exp.title}")
                with col2:
                    st.write(f"样品: {exp.sample_name} | 状态: {exp.status}")
                with col3:
                    if st.button("查看详情", key=f"view_{exp.id}"):
                        st.session_state['view_exp_id'] = exp.id
                        st.rerun()
                st.markdown("---")
    else:
        st.info("暂无实验记录，点击左侧「➕ 新建实验」开始")

# ========== 新建实验 ==========
elif page == "➕ 新建实验":
    st.title("➕ 新建实验记录")
    
    tab1, tab2, tab3 = st.tabs(["📝 基本信息", "⚗️ 色谱条件", "📊 结果数据"])
    
    with tab1:
        st.subheader("基本信息")
        
        col1, col2 = st.columns(2)
        with col1:
            exp_number = st.text_input(
                "实验编号",
                value=f"EXP-{datetime.now().strftime('%Y%m%d')}-001",
                help="格式：EXP-YYYYMMDD-XXX"
            )
            title = st.text_input("实验标题", placeholder="例如：XX药物含量测定方法优化")
            objective = st.text_area("实验目的", placeholder="描述本次实验的目标...")
        
        with col2:
            operator = st.text_input("实验人员", value="Teagee")
            sample_name = st.text_input("样品名称")
            sample_batch = st.text_input("样品批号")
            sample_prep = st.text_area("样品前处理", placeholder="描述样品前处理方法...")
    
    with tab2:
        st.subheader("色谱条件")
        
        # 选择或创建方法
        use_existing = st.checkbox("使用已有方法模板")
        
        if use_existing:
            methods = db.get_methods()
            if methods:
                method_options = {f"{m.name} ({m.target_compound})": m.id for m in methods}
                selected_method = st.selectbox("选择方法", list(method_options.keys()))
                method_id = method_options[selected_method]
                method = db.get_method_by_id(method_id)
                
                # 显示方法详情
                st.info(f"**方法**: {method.name}\n\n**色谱柱**: {method.column_model} {method.column_dimensions}\n\n**流动相**: A: {method.mobile_phase_a} | B: {method.mobile_phase_b}")
            else:
                st.warning("暂无方法模板，请先去'📊 方法库'创建")
                method_id = None
        else:
            method_id = None
            st.markdown("#### 色谱条件设置")
            
            col1, col2 = st.columns(2)
            with col1:
                column_type = st.selectbox(
                    "色谱柱类型",
                    ["C18", "C8", "苯基柱", "HILIC", "正相", "其他"]
                )
                column_model = st.text_input("色谱柱型号", placeholder="例如：Agilent Zorbax SB-C18")
                column_dims = st.text_input("色谱柱规格", placeholder="例如：4.6×150mm, 5μm")
            
            with col2:
                mp_a = st.text_input("流动相A", placeholder="例如：0.1% TFA水溶液")
                mp_b = st.text_input("流动相B", placeholder="例如：乙腈")
                gradient = st.text_input("梯度程序", placeholder="例如：10-90%B (0-20min)")
        
        st.markdown("---")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            flow_rate = st.number_input("流速 (mL/min)", min_value=0.1, max_value=5.0, value=1.0, step=0.1)
        with col2:
            column_temp = st.number_input("柱温 (°C)", min_value=20.0, max_value=60.0, value=30.0, step=1.0)
        with col3:
            injection_vol = st.number_input("进样量 (μL)", min_value=1.0, max_value=100.0, value=10.0, step=1.0)
        with col4:
            detection_wl = st.number_input("检测波长 (nm)", min_value=190.0, max_value=800.0, value=254.0, step=1.0)
    
    with tab3:
        st.subheader("结果数据")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 性能指标")
            retention_time = st.number_input("保留时间 (min)", min_value=0.0, value=0.0, step=0.1)
            resolution = st.number_input("分离度 (Rs)", min_value=0.0, value=0.0, step=0.1)
            theoretical_plates = st.number_input("理论塔板数", min_value=0, value=0, step=100)
        
        with col2:
            st.markdown("#### 峰形指标")
            tailing_factor = st.number_input("拖尾因子", min_value=0.0, value=1.0, step=0.1)
            sn_ratio = st.number_input("信噪比 (S/N)", min_value=0.0, value=0.0, step=1.0)
            
            st.markdown("#### 评估")
            success_rating = st.slider("成功评分", 1, 5, 3)
            status = st.selectbox("状态", ["draft", "completed", "failed"])
        
        st.markdown("---")
        
        observations = st.text_area("观察记录", placeholder="记录实验观察、问题、改进想法...")
        next_steps = st.text_area("下一步计划", placeholder="描述后续实验计划...")
        
        chromatogram_file = st.text_input("色谱图文件路径", placeholder="例如：C:\\Data\\chromatogram.pdf")
    
    # 保存按钮
    st.markdown("---")
    
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("💾 保存实验记录", type="primary", use_container_width=True):
            try:
                # 创建实验对象
                exp = Experiment(
                    method_id=method_id if use_existing else None,
                    experiment_number=exp_number,
                    title=title,
                    objective=objective,
                    operator=operator,
                    sample_name=sample_name,
                    sample_batch=sample_batch,
                    sample_preparation=sample_prep,
                    retention_time=retention_time if retention_time > 0 else None,
                    resolution=resolution if resolution > 0 else None,
                    theoretical_plates=theoretical_plates if theoretical_plates > 0 else None,
                    tailing_factor=tailing_factor if tailing_factor != 1.0 else None,
                    sn_ratio=sn_ratio if sn_ratio > 0 else None,
                    status=status,
                    success_rating=success_rating,
                    observations=observations,
                    next_steps=next_steps,
                    chromatogram_file=chromatogram_file
                )
                
                # 如果有新方法，保存方法
                if not use_existing and column_model:
                    method = ChromatographicMethod(
                        name=f"{sample_name}方法",
                        column_type=column_type,
                        column_model=column_model,
                        column_dimensions=column_dims,
                        mobile_phase_a=mp_a,
                        mobile_phase_b=mp_b,
                        gradient_program=gradient,
                        flow_rate=flow_rate,
                        column_temperature=column_temp,
                        injection_volume=injection_vol,
                        detection_wavelength=detection_wl,
                        target_compound=sample_name,
                        created_by=operator
                    )
                    method_id = db.add_method(method)
                    exp.method_id = method_id
                
                # 保存实验
                exp_id = db.add_experiment(exp)
                
                st.success(f"✅ 实验记录已保存！ID: {exp_id}")
                
            except Exception as e:
                st.error(f"❌ 保存失败：{str(e)}")

# ========== 实验记录 ==========
elif page == "📋 实验记录":
    st.title("📋 实验记录管理")
    
    # 搜索和筛选
    col1, col2, col3 = st.columns(3)
    with col1:
        search = st.text_input("🔍 搜索", placeholder="搜索标题、样品、实验人员...")
    with col2:
        status_filter = st.selectbox("状态筛选", ["全部", "draft", "completed", "failed"])
    with col3:
        st.write("")  # 占位
    
    # 获取实验记录
    status = None if status_filter == "全部" else status_filter
    experiments = db.get_experiments(search=search if search else None, status=status)
    
    st.markdown(f"**共找到 {len(experiments)} 条记录**")
    st.markdown("---")
    
    if experiments:
        # 转换为DataFrame显示
        data = []
        for exp in experiments:
            data.append({
                '编号': exp.experiment_number,
                '标题': exp.title,
                '样品': exp.sample_name,
                '实验人员': exp.operator,
                '状态': exp.status,
                '评分': '⭐' * exp.success_rating if exp.success_rating else '-',
                '创建时间': exp.created_at[:10] if exp.created_at else '-',
                'ID': exp.id
            })
        
        df = pd.DataFrame(data)
        st.dataframe(df.drop('ID', axis=1), use_container_width=True)
        
        # 查看详情
        st.markdown("---")
        st.subheader("📄 查看详情")
        
        exp_ids = [f"{e.experiment_number} - {e.title}" for e in experiments]
        selected = st.selectbox("选择实验记录", exp_ids)
        
        if selected:
            selected_id = [e.id for e in experiments if f"{e.experiment_number} - {e.title}" == selected][0]
            exp = db.get_experiment_by_id(selected_id)
            
            if exp:
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**基本信息**")
                    st.write(f"编号：{exp.experiment_number}")
                    st.write(f"标题：{exp.title}")
                    st.write(f"目的：{exp.objective}")
                    st.write(f"样品：{exp.sample_name} ({exp.sample_batch})")
                    st.write(f"实验人员：{exp.operator}")
                
                with col2:
                    st.markdown("**结果数据**")
                    if exp.retention_time:
                        st.write(f"保留时间：{exp.retention_time} min")
                    if exp.resolution:
                        st.write(f"分离度：{exp.resolution}")
                    if exp.theoretical_plates:
                        st.write(f"理论塔板数：{exp.theoretical_plates}")
                    if exp.tailing_factor:
                        st.write(f"拖尾因子：{exp.tailing_factor}")
                    st.write(f"状态：{exp.status}")
                    st.write(f"评分：{'⭐' * exp.success_rating if exp.success_rating else '-'}")
                
                st.markdown("**观察记录**")
                st.info(exp.observations if exp.observations else "无观察记录")
                
                if exp.next_steps:
                    st.markdown("**下一步计划**")
                    st.success(exp.next_steps)
    else:
        st.info("暂无实验记录")

# ========== 方法库 ==========
elif page == "📊 方法库":
    st.title("📊 方法库")
    
    tab1, tab2 = st.tabs(["📚 查看方法", "➕ 新建方法"])
    
    with tab1:
        col1, col2 = st.columns([2, 1])
        with col1:
            search = st.text_input("🔍 搜索方法", placeholder="搜索方法名称、目标化合物...")
        with col2:
            column_filter = st.selectbox(
                "色谱柱类型",
                ["全部", "C18", "C8", "苯基柱", "HILIC", "正相"]
            )
        
        column_type = None if column_filter == "全部" else column_filter
        methods = db.get_methods(search=search if search else None, column_type=column_type)
        
        st.markdown(f"**共找到 {len(methods)} 个方法**")
        
        for method in methods:
            with st.expander(f"🧪 {method.name} - {method.target_compound}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**色谱柱**：{method.column_model}")
                    st.write(f"**规格**：{method.column_dimensions}")
                    st.write(f"**流动相A**：{method.mobile_phase_a}")
                    st.write(f"**流动相B**：{method.mobile_phase_b}")
                with col2:
                    st.write(f"**流速**：{method.flow_rate} mL/min")
                    st.write(f"**柱温**：{method.column_temperature} °C")
                    st.write(f"**检测**：{method.detection_method} {method.detection_wavelength}nm")
                    st.write(f"**创建时间**：{method.created_at[:10] if method.created_at else '-'}")
                
                if method.gradient_program:
                    st.write(f"**梯度程序**：{method.gradient_program}")
                if method.tags:
                    st.write(f"**标签**：{method.tags}")
    
    with tab2:
        st.subheader("创建新方法")
        
        with st.form("new_method"):
            method_name = st.text_input("方法名称", placeholder="例如：阿司匹林含量测定-UPLC法")
            method_desc = st.text_area("方法描述")
            
            col1, col2 = st.columns(2)
            with col1:
                column_type = st.selectbox("色谱柱类型", ["C18", "C8", "苯基柱", "HILIC", "正相"])
                column_model = st.text_input("色谱柱型号")
                column_dims = st.text_input("规格", value="4.6×150mm, 5μm")
            with col2:
                target_compound = st.text_input("目标化合物")
                sample_matrix = st.text_input("样品基质")
                tags = st.text_input("标签（逗号分隔）")
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            with col1:
                mp_a = st.text_input("流动相A")
                flow_rate = st.number_input("流速", value=1.0)
                column_temp = st.number_input("柱温", value=30.0)
            with col2:
                mp_b = st.text_input("流动相B")
                gradient = st.text_input("梯度程序")
                detection_wl = st.number_input("检测波长", value=254.0)
            
            submitted = st.form_submit_button("💾 保存方法", use_container_width=True)
            
            if submitted and method_name:
                method = ChromatographicMethod(
                    name=method_name,
                    description=method_desc,
                    column_type=column_type,
                    column_model=column_model,
                    column_dimensions=column_dims,
                    mobile_phase_a=mp_a,
                    mobile_phase_b=mp_b,
                    gradient_program=gradient,
                    flow_rate=flow_rate,
                    column_temperature=column_temp,
                    detection_wavelength=detection_wl,
                    target_compound=target_compound,
                    sample_matrix=sample_matrix,
                    tags=tags,
                    created_by="Teagee"
                )
                method_id = db.add_method(method)
                st.success(f"✅ 方法已创建！ID: {method_id}")

# ========== 数据分析 ==========
elif page == "🔍 数据分析":
    st.title("🔍 数据分析")
    
    st.info("📊 数据分析功能 - 基础版限制")
    
    # 付费功能提示
    with st.expander("🔓 升级专业版解锁更多功能"):
        st.markdown("""
        ### 专业版功能 (0.03 ETH/月)
        - ✅ 无限制历史数据分析
        - ✅ AI智能方法推荐
        - ✅ 色谱文件自动解析 (ChemStation/Empower)
        - ✅ 方法优化趋势预测
        - ✅ 高级统计报告
        - ✅ 团队协作功能
        
        ### 企业版 (定制价格)
        - 本地部署
        - 定制开发
        - 培训服务
        
        **支付方式**: Base链 ETH  
        **钱包地址**: `0x93554a80034237151Cc0904e6884C1f758975c1c`
        
        支付后请联系 Teagee Li 激活账户
        """)
    
    # 简单的统计图表
    import plotly.express as px
    
    experiments = db.get_experiments()
    
    if experiments:
        # 实验状态分布
        status_counts = {}
        for exp in experiments:
            status_counts[exp.status] = status_counts.get(exp.status, 0) + 1
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("实验状态分布")
            fig = px.pie(
                values=list(status_counts.values()),
                names=list(status_counts.keys()),
                title="实验状态"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("成功评分分布")
            rating_counts = {}
            for exp in experiments:
                if exp.success_rating > 0:
                    rating_counts[exp.success_rating] = rating_counts.get(exp.success_rating, 0) + 1
            
            if rating_counts:
                fig2 = px.bar(
                    x=list(rating_counts.keys()),
                    y=list(rating_counts.values()),
                    title="评分分布",
                    labels={'x': '评分', 'y': '数量'}
                )
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.write("暂无评分数据")
    else:
        st.info("暂无数据，请先添加实验记录")
