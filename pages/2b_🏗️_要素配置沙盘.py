"""
🏗️ 要素配置沙盘 — 长期劳动需求：替代效应 vs 规模效应
教学竞赛级：Cobb-Douglas生产函数 + 等产量线/等成本线 + 三步探究
情境：某新能源车企的"AI机器人 vs 产业工人"产能博弈
"""

import streamlit as st
import numpy as np
import plotly.graph_objects as go
import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from shared import render_metric_card

st.set_page_config(page_title="要素配置沙盘", page_icon="🏗️", layout="wide")

# ==========================================
# 赛博暗色 UI
# ==========================================
st.markdown("""
<style>
    .stApp { background-color: #0b0f19 !important; }
    section[data-testid="stSidebar"] {
        background-color: #090d16 !important;
        border-right: 1px solid rgba(16, 185, 129, 0.1) !important;
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
        color: #10b981 !important; font-weight: 600 !important;
    }
    div[data-testid="stRadio"] label[data-selected="true"] {
        color: #34d399 !important; font-weight: 700 !important;
    }
    .tech-card {
        background: linear-gradient(145deg, rgba(30, 41, 59, 0.6) 0%, rgba(15, 23, 42, 0.8) 100%) !important;
        border: 1px solid rgba(16, 185, 129, 0.15) !important;
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
        background: #10b981; margin-right: 12px; border-radius: 3px;
        box-shadow: 0 0 8px #10b981;
    }
    .block-container { padding-top: 2rem !important; padding-bottom: 3rem !important; max-width: 98% !important; }
    header {visibility: hidden;} #MainMenu {visibility: hidden;} footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 顶部 Banner
# ==========================================
st.markdown("""
<div style="margin-bottom: 20px;">
    <h1 style="color: #ffffff; font-weight: 900; margin-bottom: 5px;">🏗️ 要素配置战略沙盘</h1>
    <h4 style="color: #10b981; font-weight: 600; letter-spacing: 1px;">
        长期劳动需求：替代效应 vs 规模效应 <span style="color:#64748b; font-weight:400;">— 某新能源车企产能博弈</span>
    </h4>
</div>
""", unsafe_allow_html=True)

# 情境设定
with st.expander("📋 场景背景（点击展开）", expanded=False):
    st.markdown("""
    **🏭 模拟情境：** 你是一家新能源车企的生产总监。公司准备新建一条电池产线。
    
    - 🤖 **资本 K**：工业机器人 / AI 质检系统（每台年租金 r）
    - 👷 **劳动 L**：传统产业工人（每人年薪 w）
    
    技术约束：产线遵循 **Cobb-Douglas 生产函数**
    """)
    st.latex(r"Q = K^{\alpha} \times L^{(1-\alpha)}")
    st.markdown("""
    你将面对一个关键决策：当地政府出台了**稳岗补贴政策**（工人工资 w 下降 30%），
    这会对你的要素配置产生什么影响？背后有两股力量在博弈——
    
    - ⚡ **替代效应**：人便宜了 → 在产量不变的前提下，用人替代机器（沿着同一条等产量线滑行）
    - 📈 **规模效应**：总成本降低了 → CEO 决定扩大产能 → 人和机器一起增加（跃迁到更高的等产量线）
    """)

# ==========================================
# 参数控制台
# ==========================================
# ==========================================
# 3. 参数控制台 + 进度滑块
# ==========================================
col_ctrl, col_graph = st.columns([1, 2.5])

with col_ctrl:
    st.markdown("<div class='tech-card'>", unsafe_allow_html=True)
    st.markdown("<div class='cyber-header'>🎛️ 生产参数控制</div>", unsafe_allow_html=True)
    
    w0 = st.slider("初始工人年工资 w₀ (万元)", 5, 30, 15, key="w0",
                   help="传统产业工人年薪（万元），含五险一金")
    r = st.slider("机器人年租金 r (万元/台)", 5, 50, 20, key="r",
                  help="工业机器人+AI系统年化成本")
    alpha = st.slider("资本密集度 α", 0.1, 0.6, 0.3, 0.05, key="alpha",
                      help="α越大，机器人越重要（技术密集型）；α越小，人力越重要（劳动密集型）")
    w_drop = st.slider("稳岗补贴导致工资降幅 (%)", 5, 60, 30, 5, key="w_drop",
                       help="地方政府稳岗补贴使企业实际工资成本下降")
    
    w1 = w0 * (1 - w_drop / 100)
    
    st.markdown("<hr style='border-color: rgba(16, 185, 129, 0.2);'>", unsafe_allow_html=True)
    st.markdown("<div class='cyber-header'>🎚️ 补贴生效进度</div>", unsafe_allow_html=True)
    
    progress = st.slider("拖动滑块，亲手推演要素重组 👇", 0, 100, 0, 1, key="progress",
                         help="0% = 初始规划 → 100% = 稳岗补贴完全生效")
    
    if progress < 5:
        st.info("📍 **初始规划** — 补贴尚未生效")
    elif progress < 50:
        st.warning(f"⚡ **替代效应区** — 工资下降 {progress:.0f}%，人比机器划算了！")
    else:
        st.success(f"📈 **规模效应区** — 成本大幅下降，CEO 拍板扩产！")
    
    st.markdown("<hr style='border-color: rgba(16, 185, 129, 0.2);'>", unsafe_allow_html=True)
    st.caption("📊 快捷情景")
    col_a, col_b = st.columns(2)
    with col_a:
        def _preset_robot():
            st.session_state.w0 = 8; st.session_state.r = 30
            st.session_state.alpha = 0.5; st.session_state.w_drop = 30
        st.button("🤖 机器人主导", use_container_width=True, key="preset_robot", on_click=_preset_robot)
    with col_b:
        def _preset_labor():
            st.session_state.w0 = 20; st.session_state.r = 10
            st.session_state.alpha = 0.2; st.session_state.w_drop = 40
        st.button("👷 劳动密集型", use_container_width=True, key="preset_labor", on_click=_preset_labor)
    
    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 4. 核心算法 (Cobb-Douglas)
# ==========================================
def optimal_inputs(Q, w, r, a):
    K_opt = Q * (a / (1 - a) * w / r) ** (1 - a)
    L_opt = Q * ((1 - a) / a * r / w) ** a
    return K_opt, L_opt

def max_output(C, w, r, a):
    K_opt = a * C / r
    L_opt = (1 - a) * C / w
    Q_max = (K_opt ** a) * (L_opt ** (1 - a))
    return K_opt, L_opt, Q_max

def isoquant(Q, L_range, a):
    return (Q / (L_range ** (1 - a))) ** (1 / a)

# ==========================================
# 5. 三步解算
# ==========================================
Q0_guess = 100
K_tmp, L_tmp = optimal_inputs(Q0_guess, w0, r, alpha)
while L_tmp > 200: Q0_guess /= 2; K_tmp, L_tmp = optimal_inputs(Q0_guess, w0, r, alpha)
while L_tmp < 30: Q0_guess *= 2; K_tmp, L_tmp = optimal_inputs(Q0_guess, w0, r, alpha)
Q0 = Q0_guess
C0 = w0 * L_tmp + r * K_tmp

K_A, L_A = optimal_inputs(Q0, w0, r, alpha)
K_B, L_B = optimal_inputs(Q0, w1, r, alpha)
K_C, L_C, Q1 = max_output(C0, w1, r, alpha)

# ==========================================
# 6. 连续插值解算
# ==========================================
t = progress / 100.0
w_current = w0 + (w1 - w0) * t

if t < 0.4:
    t_sub = t / 0.4
    K_cur, L_cur = optimal_inputs(Q0, w_current, r, alpha)
    phase = "sub"
else:
    t_inc = (t - 0.4) / 0.6
    K_cur = K_B + (K_C - K_B) * t_inc
    L_cur = L_B + (L_C - L_B) * t_inc
    phase = "inc"

# ==========================================
# 7. Plotly 动态可视化
# ==========================================
L_plot = np.linspace(1, max(L_A, L_B, L_C) * 1.6, 300)

fig = go.Figure()

# 等产量线 Q₀
K_iso_A = isoquant(Q0, L_plot, alpha)
fig.add_trace(go.Scatter(
    x=L_plot, y=K_iso_A,
    mode='lines', name="等产量线 Q₀",
    line=dict(color='rgba(59, 130, 246, 0.5)', width=2, dash='dot'),
    hovertemplate=f'产量 Q₀={Q0:.0f}<extra></extra>'
))

# 初始等成本线
L_cost0 = np.array([0, C0 / w0])
K_cost0 = np.array([C0 / r, 0])
fig.add_trace(go.Scatter(
    x=L_cost0, y=K_cost0,
    mode='lines', name="初始等成本线",
    line=dict(color='rgba(148, 163, 184, 0.4)', width=1.5, dash='dot'),
    hovertemplate='初始预算 C₀<extra></extra>'
))

# 点 A
fig.add_trace(go.Scatter(
    x=[L_A], y=[K_A],
    mode='markers+text', name="规划点 A",
    text=["A"], textposition="top right",
    textfont=dict(size=16, color='#3b82f6', family='Arial Black'),
    marker=dict(size=14, color='#3b82f6', line=dict(width=2, color='white')),
    hovertemplate=f'<b>点A：初始规划</b><br>工人: {L_A:.0f} | 机器人: {K_A:.1f}<br>产量 Q₀ | 成本 {C0:.0f}万<extra></extra>'
))

# 当前等成本线（随补贴生效旋转）
C_cur = w_current * L_cur + r * K_cur
L_cost_cur = np.array([0, C0 / w_current])
K_cost_cur = np.array([C0 / r, 0])
fig.add_trace(go.Scatter(
    x=L_cost_cur, y=K_cost_cur,
    mode='lines', name=f"当前等成本线",
    line=dict(color='#10b981', width=3.5),
    hovertemplate=f'补贴后工资 {w_current:.0f}万<br>预算 C₀={C0:.0f}万<extra></extra>'
))

# B 点（替代效应终点）
if progress > 5:
    fig.add_trace(go.Scatter(
        x=[L_B], y=[K_B],
        mode='markers+text', name="替代点 B",
        text=["B"], textposition="bottom right",
        textfont=dict(size=14, color='#fbbf24', family='Arial Black'),
        marker=dict(size=12, color='#fbbf24', symbol='diamond', line=dict(width=2, color='white')),
        hovertemplate=f'<b>点B：纯替代效应</b><br>工人 +{L_B-L_A:.0f} | 机器人 -{K_A-K_B:.1f}<br>产量不变 Q₀<extra></extra>'
    ))

# Q₁ 等产量线 + C 点
if progress > 40:
    K_iso_C = isoquant(Q1, L_plot, alpha)
    fig.add_trace(go.Scatter(
        x=L_plot, y=K_iso_C,
        mode='lines', name=f"等产量线 Q₁",
        line=dict(color='rgba(52, 211, 153, 0.5)', width=2, dash='dot'),
        hovertemplate=f'产量 Q₁={Q1:.0f} (+{(Q1/Q0-1)*100:.0f}%)<extra></extra>'
    ))
    fig.add_trace(go.Scatter(
        x=[L_C], y=[K_C],
        mode='markers+text', name="扩张点 C",
        text=["C"], textposition="top right",
        textfont=dict(size=16, color='#34d399', family='Arial Black'),
        marker=dict(size=16, color='#34d399', symbol='star', line=dict(width=2, color='white')),
        hovertemplate=f'<b>点C：规模效应</b><br>工人 +{L_C-L_B:.0f} | 机器人 +{K_C-K_B:.1f}<br>产量 Q₁={Q1:.0f}<extra></extra>'
    ))

# 当前点（拖动的球）
fig.add_trace(go.Scatter(
    x=[L_cur], y=[K_cur],
    mode='markers', name="📍 当前位置",
    marker=dict(size=22, color='#00f2fe', symbol='circle',
                line=dict(width=4, color='white'), opacity=0.9),
    hovertemplate=(
        f'<b>🎚️ 当前位置 (进度 {progress}%)</b><br>'
        f'工人: {L_cur:.0f} | 机器人: {K_cur:.1f}<br>'
        f'工资: {w_current:.0f}万<extra></extra>'
    )
))

# 拖尾轨迹
trail_L, trail_K = [], []
for ti in np.linspace(0, t, min(30, max(2, progress // 3 + 2))):
    w_ti = w0 + (w1 - w0) * ti
    if ti < 0.4:
        t_sub_i = ti / 0.4
        Ki, Li = optimal_inputs(Q0, w0 + (w1 - w0) * t_sub_i, r, alpha)
    else:
        t_inc_i = (ti - 0.4) / 0.6
        Ki = K_B + (K_C - K_B) * t_inc_i
        Li = L_B + (L_C - L_B) * t_inc_i
    trail_L.append(Li); trail_K.append(Ki)

if len(trail_L) > 1:
    fig.add_trace(go.Scatter(
        x=trail_L, y=trail_K,
        mode='lines', name="运动轨迹",
        line=dict(color='rgba(0, 242, 254, 0.4)', width=2),
        hoverinfo='skip'
    ))

# 效应标注
if progress > 5:
    fig.add_annotation(
        x=(L_A + L_B) / 2, y=(K_A + K_B) / 2,
        text=f"替代效应<br>人替机器",
        showarrow=True, arrowhead=2, arrowcolor="#fbbf24", arrowsize=1,
        font=dict(size=11, color="#fbbf24"), bgcolor="rgba(0,0,0,0.6)", borderpad=4
    )
if progress > 50:
    fig.add_annotation(
        x=(L_B + L_C) / 2, y=(K_B + K_C) / 2,
        text=f"规模效应<br>全要素扩张",
        showarrow=True, arrowhead=2, arrowcolor="#34d399", arrowsize=1,
        font=dict(size=11, color="#34d399"), bgcolor="rgba(0,0,0,0.6)", borderpad=4
    )

fig.update_layout(
    xaxis_title="产业工人 L (人/年)",
    yaxis_title="工业机器人 K (台/年)",
    xaxis=dict(range=[0, max(L_A, L_B, L_C) * 1.7], gridcolor="rgba(51, 65, 85, 0.3)"),
    yaxis=dict(range=[0, max(K_A, K_B, K_C) * 1.7], gridcolor="rgba(51, 65, 85, 0.3)"),
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#e2e8f0", size=13),
    height=550, margin=dict(l=40, r=20, t=40, b=40),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color="#e2e8f0")),
    hovermode='closest'
)

with col_graph:
    st.markdown("<div class='tech-card'>", unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 8. 动态诊断报告
# ==========================================
st.markdown("<div class='tech-card'>", unsafe_allow_html=True)
st.markdown("<div class='cyber-header'>💡 孪生系统智能诊断报告</div>", unsafe_allow_html=True)

sub_K = K_A - K_B; sub_L = L_B - L_A
scale_K = K_C - K_B; scale_L = L_C - L_B

col_r1, col_r2 = st.columns(2)

with col_r1:
    if progress < 20:
        st.info(
            f"📍 **补贴尚未显著生效** (工资 {w_current:.0f} 万)\n\n"
            f"当前配置：👷 {L_cur:.0f} 人 + 🤖 {K_cur:.1f} 台\n"
            f"产量 Q₀ = {Q0:.0f} | 总成本 = {C0:.0f} 万元\n\n"
            f"👈 **向右拖动滑块**，让稳岗补贴逐步生效！"
        )
    elif progress < 60:
        st.warning(
            f"⚡ **替代效应主导** — 工资 {w0}→{w_current:.0f} 万\n\n"
            f"沿等产量线 Q₀ 滑动：\n"
            f"🤖 机器人 **-{sub_K:.1f} 台** ({sub_K/K_A*100:.0f}%)\n"
            f"👷 工人 **+{sub_L:.0f} 人** ({sub_L/L_A*100:.0f}%)\n\n"
            f"人比机器划算了，在产量不变下用人替机器。"
        )
    else:
        st.success(
            f"📈 **规模效应爆发** — 成本节省 {C0 - r*K_B - w1*L_B:.0f} 万\n\n"
            f"CEO 决定用原预算扩产：\n"
            f"👷 再招 **+{scale_L:.0f} 人** | 🤖 再加 **+{scale_K:.1f} 台**\n"
            f"📦 产量 Q₀ → **Q₁ ({Q1:.0f})** 提升 **{(Q1/Q0-1)*100:.0f}%**"
        )

with col_r2:
    if progress > 20:
        c1, c2 = st.columns(2)
        with c1:
            st.metric("替代效应", f"L +{sub_L:.0f}, K -{sub_K:.1f}",
                     delta="要素替代")
        with c2:
            st.metric("规模效应", f"L +{scale_L:.0f}, K +{scale_K:.1f}",
                     delta="产能扩张")
        if progress > 60:
            st.metric("总效应",
                     f"L +{sub_L+scale_L:.0f}, K {K_C-K_A:+.1f}",
                     delta=f"产量 {(Q1/Q0-1)*100:.0f}%↑")

st.markdown("---")

# 课程思政判断
if w_drop > 50:
    st.error(
        f"⚠️ **孪生系统风控提示**\n\n"
        f"当前工资降幅 **{w_drop}%**，虽然短期靠替代效应增加了 {sub_L:.0f} 个岗位，"
        f"但过度压低劳动力成本不可持续：\n\n"
        f"1. 压缩了劳动者的人力资本积累空间，透支「人口红利」\n"
        f"2. 高质量发展应依靠**规模效应**——技术创新降低成本、扩大产能\n"
        f"3. 稳岗补贴的初衷是「保就业而不压工资」\n\n"
        f"🏛️ **新质生产力战略**强调从「人口红利」转向「人才红利」，"
        f"政府补贴应激励企业通过技术创新实现产业升级与高质量就业的双赢。"
    )
else:
    st.success(
        f"✅ **良性扩张诊断** — 补贴降幅 {w_drop}% 处于合理区间\n\n"
        f"规模效应不仅增加了劳动需求（+{scale_L:.0f} 人），"
        f"还带动了资本投入同步增长（+{scale_K:.1f} 台机器人），"
        f"实现了「产业升级 + 就业增长」双赢。\n\n"
        f"📚 **希克斯-马歇尔定理**：当规模效应 > 替代效应时，"
        f"工资下降带来的总就业增长更加显著。"
    )

# 数值对比表
st.markdown(f"""
| | 工人 L | 机器人 K | 产量 Q | 成本 |
|------|--------|---------|--------|------|
| **A (初始)** | {L_A:.0f} | {K_A:.1f} | {Q0:.0f} | {C0:.0f} |
| **B (替代)** | {L_B:.0f} | {K_B:.1f} | {Q0:.0f} | {w1*L_B + r*K_B:.0f} |
| **C (规模)** | {L_C:.0f} | {K_C:.1f} | {Q1:.0f} | {C0:.0f} |
""")

st.markdown("</div>", unsafe_allow_html=True)
