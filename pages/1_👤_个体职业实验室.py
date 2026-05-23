"""
个体职业发展实验室 — 人力资本投资与职业决策仿真
教学竞赛级：预测-验证脚手架 + 一生收益折现 + 中国真实数据基准 + 课程思政
"""

import streamlit as st
import numpy as np
import plotly.graph_objects as go
import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from shared import (
    calc_mincer, calc_migration_npv,
    CHINA_WAGE_BY_EDU_2024, CHINA_MIGRANT_WAGE_2024,
    EDUCATION_LABELS, DATA_SOURCES,
    SCHOOL_NAME, AUTHOR_NAME,
)

st.set_page_config(page_title="个体职业实验室", page_icon="👤", layout="wide")

# ==========================================
# 赛博暗色 UI
# ==========================================
st.markdown("""
<style>
    .stApp { background-color: #0b0f19 !important; }
    section[data-testid="stSidebar"] {
        background-color: #090d16 !important;
        border-right: 1px solid rgba(59, 130, 246, 0.1) !important;
    }
    .stApp,
    .stApp p, .stApp span, .stApp div,
    .stApp li, .stApp strong, .stApp b,
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
    div[data-testid="stMarkdownContainer"],
    div[data-testid="stMarkdownContainer"] * {
        color: #e2e8f0 !important;
    }
    .stMarkdown table th, .stMarkdown table td {
        border-color: rgba(148, 163, 184, 0.3) !important;
        color: #cbd5e1 !important;
    }
    section[data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }
    div[data-testid="stSlider"] label, div[data-testid="stRadio"] label {
        color: #38bdf8 !important; font-weight: 600 !important;
    }
    div[data-testid="stRadio"] label[data-selected="true"] {
        color: #00f2fe !important; font-weight: 700 !important;
    }
    .tech-card {
        background: linear-gradient(145deg, rgba(30, 41, 59, 0.6) 0%, rgba(15, 23, 42, 0.8) 100%) !important;
        border: 1px solid rgba(59, 130, 246, 0.15) !important;
        box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.6) !important;
        backdrop-filter: blur(12px);
        border-radius: 12px; padding: 24px; margin-bottom: 24px;
    }
    .cyber-header {
        font-size: 20px; font-weight: 700; color: #ffffff !important;
        margin-bottom: 20px; display: flex; align-items: center;
    }
    .cyber-header::before {
        content: ''; display: inline-block; width: 6px; height: 24px;
        background: #3b82f6; margin-right: 12px; border-radius: 3px;
        box-shadow: 0 0 8px #3b82f6;
    }
    .predict-card {
        background: linear-gradient(135deg, rgba(30, 58, 138, 0.3) 0%, rgba(37, 99, 235, 0.1) 100%);
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-radius: 12px; padding: 20px; margin-bottom: 18px;
    }
    .highlight-num {
        font-size: 28px; font-weight: 900; color: #38bdf8;
        font-family: 'JetBrains Mono', monospace;
    }
    .block-container { padding-top: 2rem !important; padding-bottom: 3rem !important; max-width: 98% !important; }
    header {visibility: hidden;} #MainMenu {visibility: hidden;} footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# Banner
# ==========================================
st.markdown(f"""
<div style="margin-bottom: 20px;">
    <h1 style="color: #ffffff; font-weight: 900; margin-bottom: 5px;">👤 个体职业发展实验室</h1>
    <h4 style="color: #38bdf8; font-weight: 600; letter-spacing: 1px;">
        你的人生 · 你的选择 — 人力资本投资回报仿真
    </h4>
    <p style="color: #64748b; font-size: 14px; margin-top: 4px;">
        {SCHOOL_NAME} · 课程负责人：{AUTHOR_NAME} | 基于明瑟收入方程 (Mincer Equation)
    </p>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 情境代入
# ==========================================
with st.expander("📋 你的故事（点击展开）", expanded=False):
    st.markdown("""
    **🎓 假设你正站在人生的十字路口——**
    
    你刚高中毕业，面前有三条路：
    - 📚 **继续读书**（本科 → 硕士 → 博士），但意味着 4~10 年没有全职收入
    - 🏭 **直接工作**，早早开始赚钱，但起薪低、天花板有限
    - 🏙️ **去大城市闯荡**，高薪但房租贵、压力大
    
    **你要做一个可能会影响你未来 40 年的决定。**
    
    这个实验室将用经济学模型帮你模拟「如果……会怎样？」——  
    但不是替你选择，而是让你看见选择背后的**数字逻辑**。
    """)

# ==========================================
# 预测验证 - 脚手架第一步
# ==========================================
st.markdown("<div class='predict-card'>", unsafe_allow_html=True)
st.markdown("##### 🔮 先预测，再实验")

predict_done = "micro_pred_done" in st.session_state

if not predict_done:
    st.markdown("*在你调整任何参数之前，先做一个直觉判断：*")
    pred_q = st.radio(
        "**你认为：读 4 年本科（vs 高中毕业直接工作），一生的总收入会增加多少？**",
        ["A. 不到 10%（差不多）",
         "B. 约 20~50%（有明显提升）",
         "C. 超过 100%（翻倍以上）",
         "D. 不一定，还要看培训投入和歧视因素"],
        key="micro_pred"
    )
    def _confirm_pred():
        st.session_state.micro_pred_done = True
        st.session_state.micro_pred_answer = st.session_state.micro_pred
    st.button("✅ 这是我的直觉，开始实验！", key="micro_pred_btn", on_click=_confirm_pred)
else:
    user_pred = st.session_state.get("micro_pred_answer", "")
    st.info(f"📝 你的预测：**{user_pred}** — 实验结果出来后，看看你的直觉准不准！")
    
st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 参数面板
# ==========================================
col_ctrl, col_graph = st.columns([1, 2.2])

with col_ctrl:
    st.markdown("<div class='tech-card'>", unsafe_allow_html=True)
    st.markdown("<div class='cyber-header'>🎛️ 你的人生参数</div>", unsafe_allow_html=True)
    
    edu = st.slider("🎓 受教育年限", 9, 22, 16, key="edu",
                    help=f"9=初中 | 12=高中 | 16=本科 | 19=硕士 | 22=博士")
    edu_label = EDUCATION_LABELS.get(edu, f"{edu}年")
    st.caption(f"当前：**{edu_label}**")
    
    exp_peak = st.slider("📈 职业生涯观察年限", 5, 40, 40, 5, key="exp",
                         help="你想看未来多少年的收入曲线？")
    
    st.markdown("---")
    st.markdown("**🏋️ 培训投资类型**")
    train_type = st.radio("", ["无额外培训", "一般培训 (通用技能)", "特殊培训 (企业专属技能)"],
                          key="train", horizontal=False,
                          help="一般培训→工资曲线整体上移 | 特殊培训→前期低、后期陡")
    
    gen_t = 5 if "一般" in train_type else 0
    spec_t = 3 if "特殊" in train_type else 0
    
    st.markdown("---")
    st.markdown("**🏙️ 城市迁移决策**")
    migrate = st.checkbox("考虑迁移至一二线城市？", key="migrate",
                          help="高薪但高成本，值得吗？")
    
    if migrate:
        w_diff = st.slider("城市月薪优势 (k)", 2, 30, 10, key="wdiff")
        c_move = st.slider("一次性搬迁成本 (k)", 5, 80, 25, key="cmove")
        c_psych = st.slider("年度心理成本 (k)", 0, 30, 8, key="cpsych")
    else:
        w_diff, c_move, c_psych = 0, 0, 0
    
    st.markdown("---")
    st.markdown("**⚖️ 市场环境**")
    disc = st.slider("劳动力市场歧视 (%)", 0, 40, 10, key="disc",
                     help="非生产率因素（性别/户籍等）导致的工资折损")
    
    st.markdown("---")
    st.caption("📊 快捷预设")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        def _preset_phd(): st.session_state.edu = 22; st.session_state.train = "无额外培训"
        st.button("🎓 博士", key="phd", on_click=_preset_phd, use_container_width=True)
    with col_b:
        def _preset_master(): st.session_state.edu = 19; st.session_state.train = "一般培训 (通用技能)"
        st.button("📚 硕士", key="master", on_click=_preset_master, use_container_width=True)
    with col_c:
        def _preset_worker(): st.session_state.edu = 12; st.session_state.migrate = True
        st.button("🏭 打工", key="worker", on_click=_preset_worker, use_container_width=True)
    
    st.markdown("---")
    st.page_link("pages/1c_✈️_迁移决策仿真.py", label="✈️ 深度迁移决策仿真 →", use_container_width=True)
    st.page_link("pages/1b_⚖️_劳动供给决策.py", label="⚖️ 收入/替代效应分解 →", use_container_width=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 核心计算
# ==========================================
exp_vec = np.linspace(0, exp_peak, 120)
w_exp, w_disc = calc_mincer(edu, exp_vec, gen_t, spec_t, disc)
w_base, _ = calc_mincer(12, exp_vec, 0, 0, 0)  # 高中对照组

# 真实数据基准
real_wage = CHINA_WAGE_BY_EDU_2024.get(edu)
edu_label_full = EDUCATION_LABELS.get(edu, f"{edu}年")

# 迁移 NPV
migrate_years, migrate_npv = None, None
if migrate and w_diff > 0:
    migrate_years, migrate_npv = calc_migration_npv(5, 5 + w_diff, c_move, c_psych)

# 一生累计收入（简化）
lifetime_edu = np.trapezoid(w_exp, exp_vec)
lifetime_base = np.trapezoid(w_base, exp_vec)
premium = (lifetime_edu / lifetime_base - 1) * 100

# ==========================================
# Plotly 可视化
# ==========================================
fig1 = go.Figure()

# 对照组（高中）
fig1.add_trace(go.Scatter(
    x=exp_vec, y=w_base, name="对照组 (高中毕业)",
    line=dict(color='rgba(148, 163, 184, 0.5)', width=2, dash='dot'),
    hovertemplate='工龄: %{x:.0f}年<br>工资: %{y:.1f}<br>高中对照组<extra></extra>'
))

# 实验组
fig1.add_trace(go.Scatter(
    x=exp_vec, y=w_exp, name=f'你的选择 ({edu_label})',
    line=dict(color='#3b82f6', width=4),
    fill='tonexty', fillcolor='rgba(59, 130, 246, 0.08)',
    hovertemplate=(
        f'<b>工龄: %{{x:.0f}}年</b><br>'
        f'工资: %{{y:.1f}}<br>'
        f'💡 教育投资提升了整条曲线<br>'
        f'<extra></extra>'
    )
))

# 歧视后工资
if disc > 0:
    fig1.add_trace(go.Scatter(
        x=exp_vec, y=w_disc, name=f'歧视影响 (-{disc}%)',
        line=dict(color='#ef4444', width=2, dash='dot'),
        hovertemplate='工龄: %{x:.0f}年<br>歧视后工资: %{y:.1f}<extra></extra>'
    ))
    # 歧视损失面积
    fig1.add_trace(go.Scatter(
        x=np.concatenate([exp_vec, exp_vec[::-1]]),
        y=np.concatenate([w_disc, w_exp[::-1]]),
        fill='toself', fillcolor='rgba(239, 68, 68, 0.08)',
        line=dict(width=0), hoverinfo='skip', name='歧视损失'
    ))

# 盈亏平衡标注：教育组追上高中组总收入的位置
cum_edu = np.cumsum(w_exp)
cum_base = np.cumsum(w_base)
diff_cum = cum_edu - cum_base
breakeven_idx = None
for i, d in enumerate(diff_cum):
    if d > 0 and (i == 0 or diff_cum[i-1] <= 0):
        breakeven_idx = i
        break
if breakeven_idx and diff_cum[-1] > 0:
    fig1.add_vline(
        x=exp_vec[breakeven_idx], line_dash="dash", line_color="#10b981",
        annotation_text=f"盈亏平衡 ≈{exp_vec[breakeven_idx]:.0f}年",
        annotation_font=dict(color="#10b981", size=12),
        annotation_position="top"
    )
    fig1.add_trace(go.Scatter(
        x=[exp_vec[breakeven_idx]], y=[w_exp[breakeven_idx]],
        mode='markers', name='📌 回本点',
        marker=dict(size=14, color='#10b981', symbol='star', line=dict(width=2, color='white')),
        hovertemplate=f'<b>盈亏平衡点</b><br>此时教育投资累计收益 = 累计成本<br>工龄 ≈{exp_vec[breakeven_idx]:.0f}年<extra></extra>'
    ))

# 真实数据基准线
if real_wage:
    fig1.add_hline(
        y=real_wage, line_dash="dash", line_color="#fbbf24",
        annotation_text=f"🇨🇳 2024年{edu_label_full}实际均值 ≈{real_wage}元/月",
        annotation_position="bottom right",
        annotation_font=dict(size=11, color="#fbbf24")
    )

fig1.update_layout(
    xaxis_title="工龄 (年)", yaxis_title="月工资指数",
    xaxis=dict(gridcolor="rgba(51, 65, 85, 0.3)"),
    yaxis=dict(gridcolor="rgba(51, 65, 85, 0.3)"),
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#e2e8f0", size=13),
    height=420, margin=dict(l=40, r=20, t=30, b=40),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                font=dict(color="#e2e8f0")),
    hovermode='x unified'
)

with col_graph:
    st.markdown("<div class='tech-card'>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📈 工资曲线", "🏙️ 迁移分析"])
    
    with tab1:
        st.plotly_chart(fig1, use_container_width=True)
        if real_wage:
            st.caption(f"📊 {DATA_SOURCES['wage_2024']}")
    
    with tab2:
        if migrate and migrate_npv is not None:
            fig2 = go.Figure()
            colors_m = ['#ef4444' if v < 0 else '#10b981' for v in migrate_npv]
            fig2.add_trace(go.Bar(
                x=migrate_years, y=migrate_npv, marker_color=colors_m,
                hovertemplate='第%{x}年<br>累计NPV: %{y:.1f}k<extra></extra>',
                name='累计净收益'
            ))
            fig2.update_layout(
                xaxis_title="年份", yaxis_title="累计净收益 (k)",
                xaxis=dict(gridcolor="rgba(51, 65, 85, 0.3)"),
                yaxis=dict(gridcolor="rgba(51, 65, 85, 0.3)"),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#e2e8f0", size=13),
                height=380, margin=dict(l=40, r=20, t=10, b=40),
                legend=dict(font=dict(color="#e2e8f0"))
            )
            st.plotly_chart(fig2, use_container_width=True)
            st.caption(f"📊 {DATA_SOURCES['migrant']}：农民工月均收入 {CHINA_MIGRANT_WAGE_2024} 元")
            
            be_arr = np.where(migrate_npv > 0)[0]
            if len(be_arr) > 0:
                st.success(f"✅ **值得迁移** — 在第 **{be_arr[0]+1}** 年收回成本，累计净收益 **{migrate_npv[-1]:+.0f}k**")
            else:
                st.error(f"❌ **不建议迁移** — 成本过高，{len(migrate_years)} 年内无法回本")
        else:
            st.info("🏠 **你选择了留在家乡**。开启上方「城市迁移决策」开关，探索外出闯荡的收益与代价。")
    
    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 关键指标面板
# ==========================================
st.markdown("<div class='tech-card'>", unsafe_allow_html=True)
st.markdown("<div class='cyber-header'>📊 你的决策数据面板</div>", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)

with c1:
    delta_color = "normal" if premium > 0 else "inverse"
    st.metric("一生总收入提升", f"{premium:+.1f}%",
              delta=f"vs 高中毕业", delta_color=delta_color)

with c2:
    if disc > 0:
        st.metric("歧视导致的损失", f"-{disc}%",
                  delta=f"工资被压低", delta_color="inverse")
    else:
        st.metric("市场公平度", "无歧视", delta="✅")

with c3:
    if real_wage:
        dev = (w_exp[0] / real_wage - 1) * 100
        dev_color = "normal" if dev < 0 else "inverse"
        st.metric("vs 中国实际基准", f"{dev:+.1f}%",
                  delta=f"{edu_label_full}实际均值{real_wage}元", delta_color=dev_color)
    else:
        st.metric("数据基准", "无对应数据", delta="—")

with c4:
    if breakeven_idx:
        st.metric("投资回本年限", f"≈{exp_vec[breakeven_idx]:.0f}年",
                  delta=f"之后全是净收益")
    else:
        st.metric("回本评估", "未达回本点", delta="教育投入过大？")

st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# AI 诊断报告
# ==========================================
st.markdown("<div class='tech-card'>", unsafe_allow_html=True)
st.markdown("<div class='cyber-header'>💡 你的职业决策诊断</div>", unsafe_allow_html=True)

col_d1, col_d2 = st.columns([3, 2])

with col_d1:
    # 构建诊断文案
    diagnosis_parts = []
    
    # 教育投资诊断
    if premium > 80:
        diagnosis_parts.append(
            f"🎓 **教育回报极高**：选择 **{edu_label_full}** 使你的预期终身收入提升 **{premium:.0f}%**。"
            f"这是一个非常显著的人力资本溢价，说明在当前劳动力市场中，你的学历信号价值很高。"
        )
    elif premium > 30:
        diagnosis_parts.append(
            f"📚 **教育回报可观**：选择 **{edu_label_full}** 带来 **{premium:.0f}%** 的终身收入提升。"
            f"投资的回报是正向的，但要关注回本年限。"
        )
    else:
        diagnosis_parts.append(
            f"⚠️ **教育回报有限**：{edu_label_full} 仅带来 {premium:.0f}% 的提升。"
            f"可能是教育年限过长（机会成本太高），或者培训投资不足。"
        )
    
    # 培训诊断
    if "一般" in train_type:
        diagnosis_parts.append(
            "🏋️ **一般培训**已在你的工资曲线中生效——可迁移技能使整条曲线向上平移，"
            "无论你跳槽到哪家公司，这个溢价都会跟着你。"
        )
    elif "特殊" in train_type:
        diagnosis_parts.append(
            "🔧 **特殊培训**让你前期工资较低（你在'交学费'），但后期曲线更陡——"
            "前提是你不能离开这家公司，否则专业技能会贬值。"
        )
    
    # 迁移诊断
    if migrate and migrate_npv is not None:
        be_arr = np.where(migrate_npv > 0)[0]
        if len(be_arr) > 0:
            diagnosis_parts.append(
                f"🏙️ **城市迁移是理性的**：在考虑了搬迁成本 ({c_move}k) 和心理成本 ({c_psych}k/年) 后，"
                f"你将在第 **{be_arr[0]+1}** 年实现净收益。"
            )
        else:
            diagnosis_parts.append(
                f"🏠 **留在家乡更明智**：虽然城市工资高出 {w_diff}k/月，"
                f"但高昂的搬迁和心理成本让你的 NPV 始终为负。"
            )
    
    # 歧视诊断
    if disc > 15:
        diagnosis_parts.append(
            f"🚨 **市场存在显著歧视**（{disc}%），你的实际工资被非生产率因素压低。"
            f"这意味着即使相同的人力资本，你也面临不公平竞争——这不是你的问题，是市场的问题。"
        )
    
    # 真实数据对比
    if real_wage:
        dev = (w_exp[0] / real_wage - 1) * 100
        if abs(dev) > 20:
            diagnosis_parts.append(
                f"📊 **模型与现实偏离较大**：你的仿真起薪与 **{edu_label_full}** 中国实际均值偏差 **{dev:+.0f}%**。"
                f"这可能是因为：模型未考虑行业差异、地域差异、学校层级、或非货币收益（如编制、福利）。"
                f"这也正是明瑟方程的局限性——真实世界远比模型复杂。"
            )
    
    for part in diagnosis_parts:
        st.markdown(part)
        st.markdown("")

with col_d2:
    st.markdown("##### 🔮 你的预测 vs 现实")
    if predict_done:
        user_pred = st.session_state.get("micro_pred_answer", "")
        # 简单判断
        if premium > 100:
            truth = "C. 超过 100%（翻倍以上）"
        elif premium > 20:
            truth = "B. 约 20~50%（有明显提升）"
        elif premium > 5:
            truth = "A. 不到 10%（差不多）"
        else:
            truth = "A. 不到 10%（差不多）"
        
        # 如果考虑了培训/歧视，应该是D
        if disc > 10 or "特殊" in train_type:
            truth += "（真正答案更接近 D——还要看培训和歧视）"
        
        if "D" in user_pred or user_pred[0] == truth[0]:
            st.success(f"✅ **你的直觉很准！**\n\n预测：{user_pred}\n实际：教育溢价 {premium:.0f}%")
        else:
            st.warning(f"🤔 **有意思的偏差！**\n\n预测：{user_pred}\n实际：教育溢价 {premium:.0f}%\n\n这说明直觉和模型之间存在差距——这正是经济学要教你的。")
    else:
        st.info("🔮 回到顶部先做预测，这里会显示你的预测 vs 实际的对比")
    
    st.markdown("---")
    st.markdown("##### 📋 你的参数速览")
    st.markdown(f"""
    - 学历：{edu_label_full} ({edu} 年)
    - 培训：{train_type}
    - 歧视：{disc}%
    - 迁移：{"是" if migrate else "否"}
    """)

st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 课程思政
# ==========================================
st.markdown("<div class='tech-card'>", unsafe_allow_html=True)
st.markdown("<div class='cyber-header'>🏛️ 深度思考：人力资本投资的社会意义</div>", unsafe_allow_html=True)

st.markdown("""
**1. 个体职业韧性 (Career Resilience)**
> 你今天的教育投资，不仅是未来工资条上的数字变化，更是你面对技术变革时的「抗风险能力」。
> 当 AI 替代低技能岗位时，受过高等教育、拥有可迁移技能的劳动者，
> 有更强的能力转型、适应、甚至创造新的岗位——这正是**职业韧性**的核心。

**2. 乡村振兴的人才命题**
> 如果每个受过高等教育的人都涌入大城市，县城的产业谁来支撑？
> 乡村振兴不仅是修路盖房，更是**人才的回流与在地化**。
> 当你的迁移 NPV 为负时，也许那不是失败——而是家乡的发展潜力正在追赶城市。
> 一个经济学视角之外的问题是：你想成为「逃离家乡的赢家」，还是「改变家乡的建设者」？

**3. 超越明瑟方程**
> 明瑟方程衡量的只是**可货币化的工资回报**，但教育的价值远不止于此——
> 认知边界的拓展、社交网络的质量、对下一代的文化传递……
> 这些「非货币收益」无法用模型计算，但它们可能才是教育最深的红利。
""")

st.markdown("</div>", unsafe_allow_html=True)
