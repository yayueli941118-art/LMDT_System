import streamlit as st
import sys, os

sys.path.insert(0, os.path.dirname(__file__))
from shared import COLOR, SHARED_CSS, SCHOOL_NAME, DEPARTMENT, AUTHOR_NAME

st.set_page_config(
    page_title="LMDT - 黎雅月老师教学平台",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 视觉样式
# ==========================================
st.markdown(SHARED_CSS(), unsafe_allow_html=True)
st.markdown("""
<style>
    .school-banner {
        background: linear-gradient(120deg, #1e3a8a 0%, #2563eb 100%);
        padding: 30px; border-radius: 15px; color: white;
        margin-bottom: 30px; box-shadow: 0 10px 20px rgba(37, 99, 235, 0.2);
        display: flex; flex-direction: row; align-items: center; justify-content: space-between;
    }
    .school-name { font-size: 22px; opacity: 0.9; font-weight: 400; letter-spacing: 1px; }
    .system-title { font-size: 48px; font-weight: 900; margin: 10px 0; letter-spacing: 2px; text-shadow: 2px 2px 4px rgba(0,0,0,0.2); }
    .author-badge {
        background-color: rgba(255,255,255,0.2); padding: 8px 15px;
        border-radius: 50px; font-size: 16px; border: 1px solid rgba(255,255,255,0.4);
    }
    .nav-card {
        background-color: white; padding: 22px; border-radius: 12px;
        border: 2px solid #e2e8f0; transition: all 0.3s ease; height: 100%;
    }
    .nav-card:hover {
        border-color: #3b82f6; box-shadow: 0 10px 30px rgba(0,0,0,0.08); transform: translateY(-4px);
    }
    .card-icon { font-size: 36px; margin-bottom: 10px; display: block; }
    .card-title { font-size: 20px; font-weight: 800; color: #1e3a8a; display: block; margin-bottom: 8px; }
    .card-desc { font-size: 15px; color: #64748b; margin-bottom: 12px; }
    .card-tag {
        display: inline-block; background: #eff6ff; color: #2563eb;
        padding: 3px 9px; border-radius: 4px; font-size: 13px; font-weight: bold; margin: 2px 3px;
    }
    .mini-card {
        background: white; border: 1px solid #e2e8f0; border-radius: 10px;
        padding: 16px; margin-bottom: 10px; transition: all 0.2s;
    }
    .mini-card:hover { border-color: #3b82f6; transform: translateX(3px); }
</style>
""", unsafe_allow_html=True)

# ==========================================
# Banner
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
        <div style="margin-top:10px; font-size:14px; opacity:0.8;">《劳动经济学》核心课程教学平台</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 三大核心实验室
# ==========================================
st.markdown("## 📍 核心实验模块")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="nav-card">
        <span class="card-icon">👤</span>
        <span class="card-title">个体职业实验室</span>
        <p class="card-desc">
            明瑟收入方程 · 教育投资回报 · 盈亏平衡分析 · 中国工资基准对比
        </p>
        <div style="margin-top:10px;">
            <span class="card-tag">第四章 人力资本</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="nav-card">
        <span class="card-icon">🏭</span>
        <span class="card-title">企业市场实验室</span>
        <p class="card-desc">
            CES生产函数 · 边际生产力 · 条件要素需求 · 要素替代弹性 · 挑战模式
        </p>
        <div style="margin-top:10px;">
            <span class="card-tag">第三章 劳动力需求</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="nav-card">
        <span class="card-icon">🌍</span>
        <span class="card-title">宏观政策实验室</span>
        <p class="card-desc">
            贝弗里奇曲线 · 新质生产力 · 乡村振兴 · 结构性失业 · 财政/货币政策沙盘
        </p>
        <div style="margin-top:10px;">
            <span class="card-tag">第八章 失业</span>
            <span class="card-tag">宏观政策</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 八大深度教学专题
# ==========================================
st.markdown("## 🔬 深度教学专题（按教材章节）")

row1_col1, row1_col2, row1_col3 = st.columns(3)

with row1_col1:
    st.markdown("""
    <div class="mini-card" style="border-left: 4px solid #06b6d4;">
        <strong style="font-size:16px;">⚖️ 第二章 劳动供给决策</strong>
        <p style="font-size:14px; color:#475569; margin:4px 0;">
            收入效应 vs 替代效应 · Cobb-Douglas 效用 · 连续进度滑块 · 希克斯补偿
        </p>
    </div>
    """, unsafe_allow_html=True)

with row1_col2:
    st.markdown("""
    <div class="mini-card" style="border-left: 4px solid #06b6d4;">
        <strong style="font-size:16px;">🏗️ 第三章 要素配置沙盘</strong>
        <p style="font-size:14px; color:#475569; margin:4px 0;">
            替代效应 vs 规模效应 · Cobb-Douglas 生产 · 等成本线旋转 · 稳岗补贴模拟
        </p>
    </div>
    """, unsafe_allow_html=True)

with row1_col3:
    st.markdown("""
    <div class="mini-card" style="border-left: 4px solid #8b5cf6;">
        <strong style="font-size:16px;">✈️ 第五章 劳动力流动</strong>
        <p style="font-size:14px; color:#475569; margin:4px 0;">
            迁徙决策 NPV · 户籍制度壁垒 · 人才引进补贴 · 三种人生情景对比
        </p>
    </div>
    """, unsafe_allow_html=True)

row2_col1, row2_col2, row2_col3 = st.columns(3)

with row2_col1:
    st.markdown("""
    <div class="mini-card" style="border-left: 4px solid #f59e0b;">
        <strong style="font-size:16px;">💰 第六章 工资决定与收入差距</strong>
        <p style="font-size:14px; color:#475569; margin:4px 0;">
            补偿性工资差异 · 效率工资 (NSC) · 最低工资权衡 · 洛伦兹曲线 · 技能溢价
        </p>
    </div>
    """, unsafe_allow_html=True)

with row2_col2:
    st.markdown("""
    <div class="mini-card" style="border-left: 4px solid #ef4444;">
        <strong style="font-size:16px;">🚫 第七章 劳动力市场歧视</strong>
        <p style="font-size:14px; color:#475569; margin:4px 0;">
            贝克尔偏见模型 · 统计性歧视螺旋 · 中国四维歧视 · 政策组合实验
        </p>
    </div>
    """, unsafe_allow_html=True)

with row2_col3:
    st.markdown("""
    <div class="mini-card" style="border-left: 4px solid #6366f1;">
        <strong style="font-size:16px;">📉 第八章 失业经济学</strong>
        <p style="font-size:14px; color:#475569; margin:4px 0;">
            失业类型诊断 · 职业搜寻 (保留工资) · 贝弗里奇曲线 · 自然失业率
        </p>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 教材覆盖矩阵
# ==========================================
st.markdown("---")
st.markdown("## 📊 教材全覆盖 · 八章对应矩阵")

st.markdown("""
| 教材章节 | 核心内容 | 仿真页面 | 色系 |
|---------|---------|---------|------|
| 第一章 | 劳动力市场导论 | 🏠 门户首页（概念框架） | — |
| 第二章 | 劳动力供给分析 | ⚖️ 劳动供给决策 → `1b` | 青 |
| 第三章 | 劳动力需求分析 | 🏭 企业实验室 → `2` + 🏗️ 要素配置沙盘 → `2b` | 青 |
| 第四章 | 人力资本投资 | 👤 个体实验室 → `1` | 蓝 |
| 第五章 | 劳动力流动 | ✈️ 迁移决策仿真 → `1c` | 紫 |
| 第六章 | 工资决定与收入差距 | 💰 工资决定与收入差距 → `1e` | 金 |
| 第七章 | 劳动力市场歧视 | 🚫 歧视经济学实验 → `1d` | 红 |
| 第八章 | 失业 | 📉 失业经济学 → `1f` + 🌍 宏观政策 → `3` | 靛 |
""")

# ==========================================
# 版底
# ==========================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748b; padding: 20px;">
    <h4>🎓 教学理念：Data-Driven Learning (DDL)</h4>
    <p>本平台旨在通过<b>数字孪生技术</b>，将抽象的经济学模型转化为可视化、可交互的实验场景。</p>
    <p>让 HR 专业的学生从"死记硬背公式"转向"理解市场逻辑"，培养数据洞察力与决策思维。</p>
    <p style="font-size:14px; margin-top:20px; opacity:0.6;">
        11 个交互式实验模块 · 8 章教材全覆盖 · 🇨🇳 融入「新质生产力」「乡村振兴」「共同富裕」等国家战略
    </p>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 侧边栏
# ==========================================
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/teacher.png", width=80)
    st.markdown(f"### 👩‍🏫 {AUTHOR_NAME}")
    st.info(f"**{SCHOOL_NAME}**\n\n人力资源管理专业核心课\n《劳动经济学》教学团队")
    st.divider()
    st.markdown("#### 🔗 快捷入口")
    st.page_link("pages/📈_教师看板.py", label="📈 教师看板 →")
    st.divider()
    st.markdown("#### 🎯 教材章节总览")
    st.caption("第一章 导论 → 🏠 首页")
    st.caption("第二章 供给 → ⚖️ 劳动供给决策")
    st.caption("第三章 需求 → 🏭 企业 + 🏗️ 要素配置")
    st.caption("第四章 人力资本 → 👤 个体实验室")
    st.caption("第五章 流动 → ✈️ 迁移决策")
    st.caption("第六章 工资 → 💰 工资与差距")
    st.caption("第七章 歧视 → 🚫 歧视实验")
    st.caption("第八章 失业 → 📉 + 🌍")
    st.divider()
    st.caption("v2.0 · 教材全覆盖教学版")
    st.caption("2026.05 · 教材全覆盖")
