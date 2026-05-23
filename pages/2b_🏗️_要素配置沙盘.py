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
    .stApp label, .stApp p, .stApp span,
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
    .stApp li, .stApp strong, .stApp b, .stApp em, .stMarkdown {
        color: #e2e8f0 !important;
    }
    .stMarkdown table th, .stMarkdown table td {
        border-color: rgba(148, 163, 184, 0.3) !important;
        color: #cbd5e1 !important;
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
    
    技术约束：产线遵循 **Cobb-Douglas 生产函数** `Q = K^α × L^(1-α)`
    
    你将面对一个关键决策：当地政府出台了**稳岗补贴政策**（工人工资 w 下降 30%），
    这会对你的要素配置产生什么影响？背后有两股力量在博弈——
    
    - ⚡ **替代效应**：人便宜了 → 在产量不变的前提下，用人替代机器（沿着同一条等产量线滑行）
    - 📈 **规模效应**：总成本降低了 → CEO 决定扩大产能 → 人和机器一起增加（跃迁到更高的等产量线）
    """)

# ==========================================
# 参数控制台
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
    
    w1 = w0 * (1 - w_drop / 100)  # 补贴后实际工资
    
    st.markdown("<hr style='border-color: rgba(16, 185, 129, 0.2);'>", unsafe_allow_html=True)
    st.markdown("<div class='cyber-header'>👣 探究进度控制</div>", unsafe_allow_html=True)
    
    step = st.radio(
        "选择观测阶段：",
        ["1. 初始规划 (均衡点 A)",
         "2. 替代效应剥离 (点 A → B)",
         "3. 规模效应爆发 (点 B → C)"],
        key="step"
    )
    
    st.markdown("<hr style='border-color: rgba(16, 185, 129, 0.2);'>", unsafe_allow_html=True)
    st.caption("📊 快捷情景")
    col_a, col_b = st.columns(2)
    with col_a:
        def _preset_robot():
            st.session_state.w0 = 8
            st.session_state.r = 30
            st.session_state.alpha = 0.5
            st.session_state.w_drop = 30
        st.button("🤖 机器人主导", use_container_width=True, key="preset_robot", on_click=_preset_robot)
    with col_b:
        def _preset_labor():
            st.session_state.w0 = 20
            st.session_state.r = 10
            st.session_state.alpha = 0.2
            st.session_state.w_drop = 40
        st.button("👷 劳动密集型", use_container_width=True, key="preset_labor", on_click=_preset_labor)
    
    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 核心算法 (Cobb-Douglas)
# ==========================================
# 给定 Q 和要素价格，成本最小化的最优要素需求
def optimal_inputs(Q, w, r, a):
    """
    min wL + rK  s.t. K^a * L^(1-a) = Q
    解析解:
    K* = Q * [a/(1-a) * w/r]^(1-a)
    L* = Q * [(1-a)/a * r/w]^a
    """
    K_opt = Q * (a / (1 - a) * w / r) ** (1 - a)
    L_opt = Q * ((1 - a) / a * r / w) ** a
    return K_opt, L_opt

# 给定预算 C 和要素价格，产量最大化的要素需求 + 最大产量
def max_output(C, w, r, a):
    """
    max K^a * L^(1-a)  s.t. wL + rK = C
    解析解:
    K* = a * C / r
    L* = (1-a) * C / w
    Q_max = K*^a * L*^(1-a)
    """
    K_opt = a * C / r
    L_opt = (1 - a) * C / w
    Q_max = (K_opt ** a) * (L_opt ** (1 - a))
    return K_opt, L_opt, Q_max

# 计算等产量线
def isoquant(Q, L_range, a):
    """对于产量 Q，给定 L 求 K: K = (Q / L^(1-a))^(1/a)"""
    K = (Q / (L_range ** (1 - a))) ** (1 / a)
    return K

# ==========================================
# 三步解算
# ==========================================
# 基准产量 Q0（以初始预算 C0 能生产的最大产量）
K0_init = alpha * (w0 * 10 + r * 5) / r  # 随便取个初始比例作为 seed
L0_init = (1 - alpha) * (w0 * 10 + r * 5) / w0
# 用初始均衡点的成本反推：先随便取个 Q 算均衡，得到预算，再用预算算 Q0
_, _ = optimal_inputs(100, w0, r, alpha)  # dummy to get ratio
# 换个思路：设定一个合理的初始产量 Q0，让 L 大约在 50-200 区间
Q0_guess = 100
K_tmp, L_tmp = optimal_inputs(Q0_guess, w0, r, alpha)
# 调整 Q0 让初始 L 在合理范围
while L_tmp > 200:
    Q0_guess /= 2
    K_tmp, L_tmp = optimal_inputs(Q0_guess, w0, r, alpha)
while L_tmp < 30:
    Q0_guess *= 2
    K_tmp, L_tmp = optimal_inputs(Q0_guess, w0, r, alpha)

Q0 = Q0_guess
C0 = w0 * L_tmp + r * K_tmp  # 初始总预算

# 点 A：初始最优要素组合（w0, r, Q0）
K_A, L_A = optimal_inputs(Q0, w0, r, alpha)
C_A = w0 * L_A + r * K_A

# 点 B：替代效应后（w1, r, Q0）— 同产量，更低工资
K_B, L_B = optimal_inputs(Q0, w1, r, alpha)
C_B = w1 * L_B + r * K_B

# 点 C：规模效应后（w1, r, 预算 C0）— 同预算，更高产量
K_C, L_C, Q1 = max_output(C0, w1, r, alpha)

# 效应量
sub_K = K_A - K_B   # 替代效应：机器减少量
sub_L = L_B - L_A   # 替代效应：工人增加量
scale_K = K_C - K_B # 规模效应：机器增加量
scale_L = L_C - L_B # 规模效应：工人增加量
total_K = K_C - K_A
total_L = L_C - L_A

# ==========================================
# Plotly 可视化
# ==========================================
L_plot = np.linspace(1, max(L_A, L_B, L_C) * 1.6, 300)
K_iso_A = isoquant(Q0, L_plot, alpha)  # 等产量线 Q0

fig = go.Figure()

# --- 第一阶段：初始均衡 A ---
# 等产量线 Q0
fig.add_trace(go.Scatter(
    x=L_plot, y=K_iso_A,
    mode='lines', name="等产量线 Q₀",
    line=dict(color='#3b82f6', width=3),
    hovertemplate='工人: %{x:.0f}<br>机器人: %{y:.1f}<br>产量 Q₀<extra></extra>'
))
# 初始等成本线
L_cost = np.array([0, C0 / w0])
K_cost = np.array([C0 / r, 0])
fig.add_trace(go.Scatter(
    x=L_cost, y=K_cost,
    mode='lines', name="初始等成本线",
    line=dict(color='rgba(148, 163, 184, 0.8)', width=2),
    hovertemplate='工人: %{x:.0f}<br>机器人: %{y:.1f}<extra></extra>'
))
# 点 A
fig.add_trace(go.Scatter(
    x=[L_A], y=[K_A],
    mode='markers+text', name="均衡点 A",
    text=["A"], textposition="top right",
    textfont=dict(size=16, color='#3b82f6', family='Arial Black'),
    marker=dict(size=16, color='#3b82f6', line=dict(width=2, color='white')),
    hovertemplate=(
        f'<b>点A：初始均衡</b><br>'
        f'工人: {L_A:.0f} 人 | 机器人: {K_A:.1f} 台<br>'
        f'产量 Q₀ | 工资 w₀={w0}万<br>'
        f'总成本: {C_A:.0f} 万元<extra></extra>'
    )
))

# --- 第二阶段：替代效应 B ---
if "2" in step or "3" in step:
    # 新等成本线（工资降低后，保持原产量）
    # 画一条过B点的新等成本线（虚线）
    C_B_line = w1 * L_B + r * K_B
    L_cost_B = np.array([0, C_B_line / w1])
    K_cost_B = np.array([C_B_line / r, 0])
    fig.add_trace(go.Scatter(
        x=L_cost_B, y=K_cost_B,
        mode='lines', name="补贴后等成本线",
        line=dict(color='#fbbf24', width=2.5, dash='dash'),
        hovertemplate='💡 稳岗补贴后成本线<extra></extra>'
    ))
    
    fig.add_trace(go.Scatter(
        x=[L_B], y=[K_B],
        mode='markers+text', name="替代点 B",
        text=["B"], textposition="bottom right",
        textfont=dict(size=16, color='#fbbf24', family='Arial Black'),
        marker=dict(size=16, color='#fbbf24', symbol='diamond', line=dict(width=2, color='white')),
        hovertemplate=(
            f'<b>点B：纯替代效应</b><br>'
            f'工人 +{sub_L:.0f} 人 | 机器人 -{sub_K:.1f} 台<br>'
            f'产量不变 Q₀ | 成本降至 {C_B:.0f}万<br>'
            f'💡 人便宜了→用人替机器<extra></extra>'
        )
    ))
    
    # 替代效应箭头
    fig.add_annotation(
        x=L_B, y=(K_A + K_B) / 2, ax=L_A, ay=(K_A + K_B) / 2,
        xref="x", yref="y", axref="x", ayref="y",
        showarrow=True, arrowhead=3, arrowcolor="#fbbf24", arrowsize=1.8,
        text=f"替代效应<br>L +{sub_L:.0f}, K -{sub_K:.1f}",
        font=dict(size=11, color="#fbbf24")
    )

# --- 第三阶段：规模效应 C ---
if "3" in step:
    # 新等产量线 Q1
    K_iso_C = isoquant(Q1, L_plot, alpha)
    fig.add_trace(go.Scatter(
        x=L_plot, y=K_iso_C,
        mode='lines', name=f"等产量线 Q₁",
        line=dict(color='#34d399', width=3),
        hovertemplate=f'产量 Q₁={Q1:.0f}<extra></extra>'
    ))
    
    # 原始预算下的新等成本线（w1, C0）
    L_cost_C = np.array([0, C0 / w1])
    K_cost_C = np.array([C0 / r, 0])
    fig.add_trace(go.Scatter(
        x=L_cost_C, y=K_cost_C,
        mode='lines', name="原始预算+新工资",
        line=dict(color='#34d399', width=3),
        hovertemplate='预算 C₀ 但工资已降<extra></extra>'
    ))
    
    fig.add_trace(go.Scatter(
        x=[L_C], y=[K_C],
        mode='markers+text', name="规模扩张点 C",
        text=["C"], textposition="top right",
        textfont=dict(size=16, color='#34d399', family='Arial Black'),
        marker=dict(size=18, color='#34d399', symbol='star', line=dict(width=2, color='white')),
        hovertemplate=(
            f'<b>点C：规模效应爆发</b><br>'
            f'工人 +{scale_L:.0f} 人 | 机器人 +{scale_K:.1f} 台<br>'
            f'产量 Q₁={Q1:.0f} (+{(Q1/Q0-1)*100:.0f}%)<br>'
            f'💡 成本省了→扩产→全要素增加<extra></extra>'
        )
    ))
    
    # 规模效应箭头 B→C
    fig.add_annotation(
        x=L_C, y=(K_B + K_C) / 2, ax=L_B, ay=(K_B + K_C) / 2,
        xref="x", yref="y", axref="x", ayref="y",
        showarrow=True, arrowhead=3, arrowcolor="#34d399", arrowsize=1.8,
        text=f"规模效应<br>L +{scale_L:.0f}, K +{scale_K:.1f}",
        font=dict(size=11, color="#34d399")
    )

fig.update_layout(
    xaxis_title="产业工人 L (人/年)",
    yaxis_title="工业机器人 K (台/年)",
    xaxis=dict(range=[0, max(L_A, L_B, L_C) * 1.7], gridcolor="rgba(51, 65, 85, 0.3)"),
    yaxis=dict(range=[0, max(K_A, K_B, K_C) * 1.7], gridcolor="rgba(51, 65, 85, 0.3)"),
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#e2e8f0", size=13),
    height=550, margin=dict(l=40, r=20, t=40, b=40),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    hovermode='closest'
)

with col_graph:
    st.markdown("<div class='tech-card'>", unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 动态诊断报告
# ==========================================
st.markdown("<div class='tech-card'>", unsafe_allow_html=True)
st.markdown("<div class='cyber-header'>💡 孪生系统智能诊断报告</div>", unsafe_allow_html=True)

if "1" in step:
    st.info(
        f"📍 **当前阶段：初始要素规划**\n\n"
        f"在当前工资 **{w0} 万元/人**、机器人租金 **{r} 万元/台** 的条件下，"
        f"成本最小化的最优配置为：\n\n"
        f"👷 雇佣 **{L_A:.0f} 名** 产业工人 | 🤖 部署 **{K_A:.1f} 台** 机器人\n"
        f"📦 产量 Q₀ = **{Q0:.0f}** | 💰 总成本 = **{C_A:.0f} 万元**\n\n"
        f"要素比例 K/L = {K_A/L_A:.2f}（资本密集度 α = {alpha}）\n\n"
        f"👉 地方政府已出台稳岗补贴，请切换到「第二阶段」观察替代效应。"
    )

elif "2" in step:
    st.warning(
        f"⚡ **替代效应：要素替代正在发生**\n\n"
        f"稳岗补贴使企业实际工资降至 **{w1:.1f} 万元**（降幅 {w_drop}%）。\n\n"
        f"在保持产量 Q₀ 不变的前提下（沿等产量线滑动）：\n\n"
        f"🔹 机器人 **减少 {sub_K:.1f} 台**（{sub_K/K_A*100:.0f}%）— 人比机器划算了\n"
        f"🔹 工人 **增加 {sub_L:.0f} 人**（{sub_L/L_A*100:.0f}%）— 用人力替代自动化\n"
        f"🔹 总成本从 {C_A:.0f} 降至 **{C_B:.0f} 万元**（节省 {C_A-C_B:.0f} 万）\n\n"
        f"这就是**替代效应**——在产量不变时，工资下降促使企业用劳动替代资本。\n\n"
        f"但故事还没完——省下来的钱去哪了？👉 切换到「第三阶段」。"
    )

elif "3" in step:
    c1, c2, c3 = st.columns(3)
    with c1:
        st.success(
            f"**替代效应**\n\n"
            f"👷 工人 **+{sub_L:.0f}** 人\n"
            f"🤖 机器人 **-{sub_K:.1f}** 台\n\n"
            f"产量不变 → 纯要素替代"
        )
    with c2:
        st.success(
            f"**规模效应**\n\n"
            f"👷 工人 **+{scale_L:.0f}** 人\n"
            f"🤖 机器人 **+{scale_K:.1f}** 台\n\n"
            f"产能扩张 {Q1/Q0:.1f}× → 全要素增加"
        )
    with c3:
        total_text = f"+{total_L:.0f}人, +{total_K:.1f}台"
        st.success(
            f"**总效应**\n\n"
            f"👷 工人 **{total_text.split(',')[0]}**\n"
            f"📦 产量 **+{(Q1/Q0-1)*100:.0f}%**\n\n"
            f"替代+规模双重引擎"
        )
    
    st.markdown("---")
    
    # 课程思政判断：工资是否压得过低
    if w_drop > 50:
        st.error(
            f"⚠️ **孪生系统风控提示**\n\n"
            f"当前工资降幅高达 **{w_drop}%**，虽然短期内通过替代效应大幅增加了劳动需求（+{total_L:.0f} 人），"
            f"但这种「低工资扩张」模式不可持续：\n\n"
            f"1. 过低的工资压缩了劳动者的人力资本积累空间，本质上是在透支「人口红利」\n"
            f"2. 真正的高质量发展应主要依靠**规模效应**——通过技术创新降低成本、扩大产能，"
            f"实现「产业升级」与「高质量就业」的双赢\n"
            f"3. 稳岗补贴的初衷是**保就业而不压低工资**，合理的补贴力度应起到「四两拨千斤」的杠杆作用\n\n"
            f"🏛️ **课程思政**：新质生产力战略强调「人才红利」而非「人口红利」。"
            f"政府补贴的目的是激励企业通过技术创新（向外跃迁到 C 点）带动规模效应，"
            f"而非鼓励企业无底线压低劳动力成本。"
        )
    else:
        st.success(
            f"✅ **良性扩张诊断**\n\n"
            f"稳岗补贴（降幅 {w_drop}%）处于合理区间。总效应呈现「工人与机器人双增长」态势：\n\n"
            f"⚡ 替代效应：工人 +{sub_L:.0f} 人（短期要素替代）\n"
            f"📈 规模效应：工人 +{scale_L:.0f} 人，机器人 +{scale_K:.1f} 台（产能扩张 {Q1/Q0:.1f}×）\n\n"
            f"🏛️ **关键结论**：当工资成本合理下降时，规模效应不仅增加了劳动需求，"
            f"还带动了资本投入（机器人部署同步增加），实现了「产业升级 + 就业增长」的双赢格局。"
            f"这正是中国制造业从「低成本竞争」转向「高质量智能制造」的微观基础。\n\n"
            f"📚 **理论对应**：希克斯-马歇尔派生需求定理指出，当规模效应 > 替代效应时，"
            f"劳动需求弹性较小且就业总体增长——本实验为这一定理提供了直观的数值验证。"
        )
    
    st.markdown("---")
    st.markdown(f"""
    | | 工人 L | 机器人 K | 产量 Q | 总成本 |
    |------|--------|---------|--------|--------|
    | **A (初始)** | {L_A:.0f} | {K_A:.1f} | {Q0:.0f} | {C_A:.0f} |
    | **B (替代)** | {L_B:.0f} (+{sub_L:.0f}) | {K_B:.1f} (-{sub_K:.1f}) | {Q0:.0f} (不变) | {C_B:.0f} |
    | **C (规模)** | {L_C:.0f} (+{scale_L:.0f}) | {K_C:.1f} (+{scale_K:.1f}) | {Q1:.0f} (+{(Q1/Q0-1)*100:.0f}%) | {C0:.0f} (不变) |
    """)

st.markdown("</div>", unsafe_allow_html=True)
