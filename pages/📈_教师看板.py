"""
📈 教师看板 — 学生实验日志汇总与分析
支持上传学生报告(.md)并自动解析参数，生成班级统计
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import re
from datetime import datetime
from io import StringIO
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from shared import COLOR, SHARED_CSS, render_page_banner, render_card_header

st.set_page_config(page_title="教师看板", page_icon="📈", layout="wide")
st.markdown(SHARED_CSS.format(color="#64748b", dark="#334155", light="#94a3b8"), unsafe_allow_html=True)

render_page_banner("📈", "教师看板 · 实验数据汇总", "Teaching Dashboard", "blue")

# ==========================================
# 侧边栏
# ==========================================
with st.sidebar:
    st.header("📂 数据管理")
    st.markdown("""
    ### 使用说明
    1. 学生完成实验后，下载实验报告 (.md)
    2. 将报告上传至此处批量解析
    3. 系统自动提取参数并生成统计图表
    
    ---
    ### 支持的报告类型
    - 个体职业发展仿真实验报告
    - 企业决策仿真实验报告
    - 宏观政策仿真实验报告
    - 劳动供给决策仿真实验报告
    """)
    st.page_link("🏠_综合门户首页.py", label="🏠 返回门户", use_container_width=True)

# ==========================================
# 上传与解析
# ==========================================
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown("""
<div style="display:flex; align-items:center; gap:10px; margin-bottom:15px;">
    <span style="font-size:36px;">📤</span>
    <span style="font-size:22px; font-weight:700; color:#334155;">批量上传学生实验报告</span>
</div>
""", unsafe_allow_html=True)

uploaded_files = st.file_uploader(
    "拖放或选择学生实验报告 (.md 文件)",
    type=["md", "txt"],
    accept_multiple_files=True,
    help="支持批量上传多个学生的实验报告"
)

# 解析函数
def parse_micro_report(content: str) -> dict:
    """解析个体职业实验室报告"""
    data = {"实验类型": "个体职业实验室"}
    patterns = {
        "受教育年限": r"\*\*受教育年限\*\*: (\d+)",
        "一般培训": r"\*\*一般培训\*\*: (\d+)",
        "特殊培训": r"\*\*特殊培训\*\*: (\d+)",
        "歧视系数": r"\*\*歧视系数\*\*: (\d+)%",
        "城乡月薪差": r"\*\*城乡月薪差\*\*: (\d+)",
        "乡村振兴补贴": r"\*\*乡村振兴补贴\*\*: (.+)",
    }
    for key, pat in patterns.items():
        m = re.search(pat, content)
        if m:
            val = m.group(1)
            try:
                data[key] = int(val)
            except ValueError:
                data[key] = val
    return data

def parse_market_report(content: str) -> dict:
    """解析企业实验室报告"""
    data = {"实验类型": "企业市场实验室"}
    patterns = {
        "资本存量": r"\*\*资本存量\*\*: (\d+)",
        "产品价格": r"\*\*产品价格\*\*: ([\d.]+)",
        "技术类型": r"\*\*技术类型\*\*: (.+)",
        "薪酬模式": r"\*\*薪酬模式\*\*: (.+)",
    }
    for key, pat in patterns.items():
        m = re.search(pat, content)
        if m:
            val = m.group(1)
            try:
                data[key] = int(val)
            except ValueError:
                try:
                    data[key] = float(val)
                except ValueError:
                    data[key] = val
    return data

def parse_macro_report(content: str) -> dict:
    """解析宏观政策实验室报告"""
    data = {"实验类型": "宏观政策实验室"}
    patterns = {
        "AI替代冲击": r"\*\*AI替代冲击\*\*: (\d+)%",
        "技能错配指数": r"\*\*技能错配指数\*\*: ([\d.]+)",
        "实施政策": r"\*\*实施政策\*\*: (.+)",
    }
    for key, pat in patterns.items():
        m = re.search(pat, content)
        if m:
            val = m.group(1)
            try:
                data[key] = int(val)
            except ValueError:
                try:
                    data[key] = float(val)
                except ValueError:
                    data[key] = val
    return data

def parse_labor_supply_report(content: str) -> dict:
    """解析劳动供给决策报告"""
    data = {"实验类型": "劳动供给决策"}
    patterns = {
        "初始工资率": r"\*\*初始工资率\*\*: (\d+)",
        "新工资率": r"\*\*新工资率\*\*: (\d+)",
        "闲暇偏好": r"\*\*闲暇偏好 β\*\*: ([\d.]+)",
    }
    for key, pat in patterns.items():
        m = re.search(pat, content)
        if m:
            val = m.group(1)
            try:
                data[key] = int(val)
            except ValueError:
                try:
                    data[key] = float(val)
                except ValueError:
                    data[key] = val
    return data

def extract_student_name(content: str) -> str:
    """提取学生姓名（从填空题取值）"""
    # 如果学生在报告中填了名字
    m = re.search(r'\*\*学生姓名\*\*:\s*_{3,}', content)
    if m:
        return "(未填写)"
    # 尝试找非下划线名字
    m = re.search(r'\*\*学生姓名\*\*:\s*([^\n_]+)', content)
    if m:
        name = m.group(1).strip()
        if name and "___" not in name:
            return name
    return "(未填写)"

def extract_time(content: str) -> str:
    """提取实验时间"""
    m = re.search(r'\*\*实验时间\*\*:\s*(\d{4}-\d{2}-\d{2}.+)', content)
    if m:
        return m.group(1)
    return "未知"

# 解析所有文件
all_data = []
if uploaded_files:
    for f in uploaded_files:
        content = f.read().decode("utf-8", errors="ignore")
        student = extract_student_name(content)
        time_str = extract_time(content)
        filename = f.name
        
        # 判断报告类型
        if "个体职业" in content:
            parsed = parse_micro_report(content)
        elif "企业决策" in content:
            parsed = parse_market_report(content)
        elif "宏观政策" in content:
            parsed = parse_macro_report(content)
        elif "劳动供给" in content:
            parsed = parse_labor_supply_report(content)
        else:
            parsed = {"实验类型": "无法识别"}
        
        parsed["学生姓名"] = student
        parsed["实验时间"] = time_str
        parsed["文件名"] = filename
        all_data.append(parsed)

st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 汇总分析
# ==========================================
if all_data:
    df = pd.DataFrame(all_data)
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("""
    <div style="display:flex; align-items:center; gap:10px; margin-bottom:15px;">
        <span style="font-size:36px;">📊</span>
        <span style="font-size:22px; font-weight:700; color:#334155;">班级汇总统计</span>
    </div>
    """, unsafe_allow_html=True)
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("上传报告数", len(all_data))
    with c2:
        types = df["实验类型"].value_counts()
        main_type = types.index[0] if len(types) > 0 else "—"
        st.metric("主要实验类型", main_type)
    with c3:
        filled = sum(1 for n in df["学生姓名"] if n != "(未填写)")
        st.metric("已署名", f"{filled}/{len(all_data)}")
    with c4:
        if "教育溢价" not in df.columns and "AI替代冲击" in df.columns:
            high_risk = sum(1 for v in df["AI替代冲击"].dropna() if v > 70)
            st.metric("高AI冲击实验组", f"{high_risk}/{len(all_data)}")
        else:
            st.metric("报告类型数", len(types))
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 按类型展示统计
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("""
    <div style="display:flex; align-items:center; gap:10px; margin-bottom:15px;">
        <span style="font-size:36px;">📋</span>
        <span style="font-size:22px; font-weight:700; color:#334155;">详细数据与图表</span>
    </div>
    """, unsafe_allow_html=True)
    
    # 按实验类型分组
    for lab_type in df["实验类型"].unique():
        sub = df[df["实验类型"] == lab_type]
        st.markdown(f"### {lab_type} ({len(sub)} 份)")
        
        if lab_type == "个体职业实验室":
            col_a, col_b = st.columns(2)
            with col_a:
                if "受教育年限" in sub.columns:
                    edu_counts = sub["受教育年限"].value_counts().sort_index()
                    fig = px.bar(x=edu_counts.index, y=edu_counts.values,
                                labels={'x': '受教育年限', 'y': '人数'},
                                title='受教育年限分布',
                                color_discrete_sequence=[COLOR["primary_light"]])
                    st.plotly_chart(fig, use_container_width=True)
            with col_b:
                if "歧视系数" in sub.columns:
                    fig = px.histogram(sub, x="歧视系数", title='歧视系数设置分布',
                                      color_discrete_sequence=[COLOR["danger"]])
                    st.plotly_chart(fig, use_container_width=True)
            
            if "乡村振兴补贴" in sub.columns:
                rural_yes = sum(1 for v in sub["乡村振兴补贴"] if "已开启" in str(v))
                st.metric("开启乡村振兴补贴", f"{rural_yes}/{len(sub)} ({100*rural_yes//max(1,len(sub))}%)")
        
        elif lab_type == "企业市场实验室":
            col_a, col_b = st.columns(2)
            with col_a:
                if "技术类型" in sub.columns:
                    tech_counts = sub["技术类型"].value_counts()
                    fig = px.pie(values=tech_counts.values, names=tech_counts.index,
                                title='技术类型选择分布',
                                color_discrete_sequence=[COLOR["market"], COLOR["primary_light"], COLOR["neutral"]])
                    st.plotly_chart(fig, use_container_width=True)
            with col_b:
                if "薪酬模式" in sub.columns:
                    pay_counts = sub["薪酬模式"].value_counts()
                    fig = px.pie(values=pay_counts.values, names=pay_counts.index,
                                title='薪酬模式选择分布',
                                color_discrete_sequence=[COLOR["primary_light"], COLOR["market"], COLOR["warning"]])
                    st.plotly_chart(fig, use_container_width=True)
        
        elif lab_type == "宏观政策实验室":
            col_a, col_b = st.columns(2)
            with col_a:
                if "AI替代冲击" in sub.columns:
                    fig = px.histogram(sub, x="AI替代冲击", title='AI冲击参数分布',
                                      color_discrete_sequence=[COLOR["macro"]])
                    st.plotly_chart(fig, use_container_width=True)
            with col_b:
                # 统计政策选择
                all_policies = []
                for p_str in sub["实施政策"].dropna():
                    if p_str != "无":
                        for p in p_str.split(", "):
                            all_policies.append(p.strip())
                if all_policies:
                    from collections import Counter
                    policy_counts = Counter(all_policies)
                    fig = px.bar(x=list(policy_counts.keys()), y=list(policy_counts.values()),
                                labels={'x': '政策', 'y': '选择次数'},
                                title='政策工具选择频次',
                                color_discrete_sequence=[COLOR["macro"]])
                    st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 原始数据表
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("""
    <div style="display:flex; align-items:center; gap:10px; margin-bottom:15px;">
        <span style="font-size:36px;">📋</span>
        <span style="font-size:22px; font-weight:700; color:#334155;">原始数据表</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # 导出
    csv = df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 导出全班数据 (CSV)",
        data=csv,
        file_name=f"LMDT_Class_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv",
        type="primary"
    )
    
    st.markdown('</div>', unsafe_allow_html=True)

else:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.info("""
    ### 📭 暂无数据
    
    **操作步骤：**
    1. 请学生在各实验室完成实验后，点击「📥 下载实验报告 (.md)」按钮
    2. 收集学生提交的 .md 文件
    3. 在此页面拖放上传，系统将自动解析
    
    *支持批量上传，一次可解析全班报告*
    """)
    st.markdown('</div>', unsafe_allow_html=True)
