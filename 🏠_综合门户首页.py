import streamlit as st
import sys, os

sys.path.insert(0, os.path.dirname(__file__))
from shared import COLOR, SHARED_CSS, SCHOOL_NAME, DEPARTMENT, AUTHOR_NAME, COMPETITION_INFO

# ==========================================
# 1. 门户配置
# ==========================================
st.set_page_config(
    page_title="LMDT - 黎雅月老师教学平台",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. 视觉样式
# ==========================================
st.markdown("""
<style>
    html, body, [class*="css"] {
        font-family: 'Microsoft YaHei', 'Heiti SC', sans-serif !important;
        color: #0f172a;
    }
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
        max-width: 95% !important;
    }
    p, .stMarkdown, li {
        font-size: 18px !important;
        line-height: 1.7 !important;
    }
    h1 { font-size: 42px !important; font-weight: 900 !important; color: #1e3a8a !important; letter-spacing: 2px; }
    h2 { font-size: 32px !important; font-weight: 800 !important; color: #1e40af !important; border-left: 8px solid #3b82f6; padding-left: 15px; }
    h3 { font-size: 24px !important; font-weight: 700 !important; }

    /* Banner */
    .school-banner {
        background: linear-gradient(120deg, #1e3a8a 0%, #2563eb 100%);
        padding: 30px;
        border-radius: 15px;
        color: white;
        margin-bottom: 30px;
        box-shadow: 0 10px 20px rgba(37, 99, 235, 0.2);
        display: flex;
        flex-direction: row;
        align-items: center;
        justify-content: space-between;
    }
    .school-name { font-size: 22px; opacity: 0.9; font-weight: 400; letter-spacing: 1px; }
    .system-title { font-size: 48px; font-weight: 900; margin: 10px 0; letter-spacing: 2px; text-shadow: 2px 2px 4px rgba(0,0,0,0.2); }
    .author-badge { 
        background-color: rgba(255,255,255,0.2); 
        padding: 8px 15px; 
        border-radius: 50px; 
        font-size: 16px; 
        border: 1px solid rgba(255,255,255,0.4);
    }

    /* 导航卡片 */
    .nav-card {
        background-color: white;
        padding: 25px;
        border-radius: 12px;
        border: 2px solid #e2e8f0;
        transition: all 0.3s ease;
        height: 100%;
    }
    .nav-card:hover {
        border-color: #3b82f6;
        box-shadow: 0 10px 30px rgba(0,0,0,0.08);
        transform: translateY(-5px);
    }
    .card-icon { font-size: 40px; margin-bottom: 15px; display: block; }
    .card-title { font-size: 24px; font-weight: 800; color: #1e3a8a; display: block; margin-bottom: 10px; }
    .card-desc { font-size: 16px; color: #64748b; margin-bottom: 15px; }
    .card-tag { 
        display: inline-block; 
        background: #eff6ff; 
        color: #2563eb; 
        padding: 4px 10px; 
        border-radius: 4px; 
        font-size: 14px; 
        font-weight: bold; 
        margin: 2px 4px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. Banner
# ==========================================
st.markdown(f"""
<div class="school-banner">
    <div>
        <div class="school-name">🏛️ {SCHOOL_NAME} · {DEPARTMENT}</div>
        <div class="system-title">劳动力市场数字孪生实验平台</div>
        <div style="font-size: 20px; font-weight: 600; margin-top:10px;">
            Designed for: <span style="border-bottom: 2px solid #fbbf24;">人力资源管理专业 (HRM)</span>
        </div>
    </div>
    <div style="text-align: right;">
        <div class="author-badge">👩‍🏫 课程负责人：{AUTHOR_NAME}</div>
        <div style="margin-top:10px; font-size:14px; opacity:0.8;">{COMPETITION_INFO}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 4. 核心导航区
# ==========================================
st.markdown("## 📍 请选择实验模块")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="nav-card">
        <span class="card-icon">👤</span>
        <span class="card-title">个体职业实验室</span>
        <p class="card-desc">
            模拟劳动者从求学、求职到流动的全生命周期。探索<b>人力资本投资</b>回报与<b>职业流动</b>决策。
        </p>
        <div style="margin-top:20px;">
            <span class="card-tag">Ch1/2 供给</span>
            <span class="card-tag">Ch5 人力资本</span>
            <span class="card-tag">Ch6 流动</span>
            <span class="card-tag" style="background:#f3e8ff; color:#7c3aed; border:1px solid #a78bfa;">★ 迁徙仿真</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="nav-card">
        <span class="card-icon">🏭</span>
        <span class="card-title">企业市场实验室</span>
        <p class="card-desc">
            扮演企业管理者，进行<b>生产要素配置</b>与<b>薪酬制度设计</b>。体验CES派生需求与效率工资理论。
        </p>
        <div style="margin-top:20px;">
            <span class="card-tag">Ch3 需求</span>
            <span class="card-tag">Ch4 均衡</span>
            <span class="card-tag">Ch8 薪酬</span>
            <span class="card-tag" style="background:#ecfdf5; color:#059669; border:1px solid #10b981;">★ 替代vs规模效应</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="nav-card">
        <span class="card-icon">🌍</span>
        <span class="card-title">宏观政策实验室</span>
        <p class="card-desc">
            扮演政策制定者，应对<b>AI技术冲击</b>，诊断<b>结构性失业</b>，制定干预政策。
        </p>
        <div style="margin-top:20px;">
            <span class="card-tag">Ch9 失业</span>
            <span class="card-tag">AI 冲击</span>
            <span class="card-tag">政策沙盘</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# 新增模块：劳动供给决策
st.markdown("---")
st.markdown("## 🆕 深度教学模块")

col4, col5 = st.columns([1, 2])

with col4:
    st.markdown("""
    <div class="nav-card" style="border-color: #8b5cf6;">
        <span class="card-icon">⚖️</span>
        <span class="card-title">劳动供给决策实验室</span>
        <p class="card-desc">
            <b>收入效应 vs 替代效应</b>分步分解。解决劳动经济学中最抽象的概念——向后弯曲的劳动供给曲线。
        </p>
        <div style="margin-top:20px;">
            <span class="card-tag">Ch2 供给决策</span>
            <span class="card-tag">收入/替代效应</span>
            <span class="card-tag">★ 国赛亮点</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #ede9fe 0%, #f3e8ff 100%); border: 1px solid #8b5cf6; border-radius: 12px; padding: 25px; height: 100%;">
        <h4 style="color:#5b21b6;">💡 为什么这个模块重要？</h4>
        <p style="font-size:16px; color:#4c1d95;">
            当工资上涨时，人们是更愿意工作还是更想休息？<br>
            这取决于<strong>替代效应</strong>（闲暇变贵→多工作）与<strong>收入效应</strong>（睡后收入够花→少工作）的博弈。<br><br>
            本模块通过<strong>三步可视化分解</strong>（初始均衡 → 替代效应 → 收入效应），
            让抽象的微观经济学概念变得触手可及。
        </p>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 5. 底部信息
# ==========================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748b; padding: 20px;">
    <h4>🎓 教学理念：Data-Driven Learning (DDL)</h4>
    <p>本平台旨在通过<b>数字孪生技术</b>，将抽象的经济学模型转化为可视化、可交互的实验场景。</p>
    <p>让 HR 专业的学生从"死记硬背公式"转向"理解市场逻辑"，培养数据洞察力与决策思维。</p>
    <p style="font-size:14px; margin-top:20px; opacity:0.6;">
        🇨🇳 融入「新质生产力」「乡村振兴」等国家战略 · 体现课程思政与时代热点
    </p>
</div>
""", unsafe_allow_html=True)

# 侧边栏
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/teacher.png", width=80)
    st.markdown(f"### 👩‍🏫 课程负责人：{AUTHOR_NAME}")
    st.info(f"**{SCHOOL_NAME}**\n\n人力资源管理专业核心课\n《劳动经济学》教学团队")
    st.divider()
    st.markdown("#### 🔗 快捷入口")
    st.page_link("pages/📈_教师看板.py", label="📈 教师看板 →", use_container_width=True)
    st.divider()
    st.markdown("#### 📌 平台版本")
    st.caption("v2.0 · 国赛优化版")
    st.caption("2025.05 · 第七届全国高校教师技能创新大赛")
