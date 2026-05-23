"""
劳动供给决策实验室 — 收入效应 vs 替代效应分步拆解
脚手架式探究 (Learning Scaffolding) + Cobb-Douglas 精确解算
"""

import streamlit as st
import numpy as np
import plotly.graph_objects as go
import sys, os

# 安全引入共享模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from shared import render_page_banner, render_metric_card

# ==========================================
# 页面配置
# ==========================================
st.set_page_config(page_title="劳动供给决策", page_icon="⚖️", layout="wide")

# ==========================================
# 赛博暗色 UI
# ==========================================
st.markdown("""
<style>
    /* ===== 1. 精准锁定全局App背景 ===== */
    .stApp {
        background-color: #0b0f19 !important;
    }

    /* ===== 2. 侧边栏暗色背景 ===== */
    section[data-testid="stSidebar"] {
        background-color: #090d16 !important;
        border-right: 1px solid rgba(56, 189, 248, 0.1) !important;
    }

    /* ===== 3. 核心文本全局亮白/灰蓝覆盖 ===== */
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

    /* ===== 4. 滑块与单选框的标签颜色 ===== */
    div[data-testid="stSlider"] label, div[data-testid="stRadio"] label {
        color: #38bdf8 !important;
        font-weight: 600 !important;
    }

    /* Radio 选中态 */
    div[data-testid="stRadio"] label[data-selected="true"] {
        color: #00f2fe !important;
        font-weight: 700 !important;
    }

    /* ===== 5. 赛博玻璃态卡片 ===== */
    .tech-card {
        background: linear-gradient(145deg, rgba(30, 41, 59, 0.6) 0%, rgba(15, 23, 42, 0.8) 100%) !important;
        border: 1px solid rgba(56, 189, 248, 0.15) !important;
        box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.6) !important;
        backdrop-filter: blur(12px);
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 24px;
    }

    /* ===== 6. 标题指示灯 ===== */
    .cyber-header {
        font-size: 20px;
        font-weight: 700;
        color: #ffffff !important;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
    }
    .cyber-header::before {
        content: '';
        display: inline-block;
        width: 6px;
        height: 24px;
        background: #00f2fe;
        margin-right: 12px;
        border-radius: 3px;
        box-shadow: 0 0 8px #00f2fe;
    }

    /* ===== 布局与隐藏 ===== */
    .block-container { padding-top: 2rem !important; padding-bottom: 3rem !important; max-width: 98% !important; }
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 顶部 Banner
# ==========================================
st.markdown("""
<div style="margin-bottom: 20px;">
    <h1 style="color: #ffffff; font-weight: 900; margin-bottom: 5px;">⚖️ 劳动供给决策实验室</h1>
    <h4 style="color: #38bdf8; font-weight: 600; letter-spacing: 1px;">
        重难点突破：工作-闲暇决策与双效应拆解 <span style="color:#64748b; font-weight:400;">(Micro-Simulation)</span>
    </h4>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 经济学底层算法 (Cobb-Douglas: U(L,Y) = L × Y)
# ==========================================
def calc_equilibrium(w, V):
    """
    给定工资率 w 和非劳动收入 V，求最优闲暇 L*
    max U = L × Y  s.t. Y = w×(24-L) + V
    解析解: L* = 12 + V/(2w)
    """
    L_opt = 12 + V / (2 * w)
    L_opt = min(L_opt, 24)
    Y_opt = w * (24 - L_opt) + V
    U_max = L_opt * Y_opt
    return L_opt, Y_opt, U_max

def calc_indifference_curve(U, L_range):
    """由效用水平 U 反解 Y = U / L"""
    return U / L_range

def calc_hicks_compensation(w_new, U_old):
    """
    希克斯补偿点 B：
    在旧无差异曲线上，找 MRS = w_new 的点
    MRS = Y/L = w_new → Y = w_new × L
    代入 U_old = L × Y = w_new × L² → L = √(U_old/w_new)
    """
    L_comp = np.sqrt(U_old / w_new)
    Y_comp = U_old / L_comp
    intercept = Y_comp + w_new * L_comp  # 补偿预算线截距
    return L_comp, Y_comp, intercept

# ==========================================
# 互动控制台
# ==========================================
# 3. 互动控制台：连续插值滑块
# ==========================================
col_ctrl, col_graph = st.columns([1, 2.5])

with col_ctrl:
    st.markdown("<div class='tech-card'>", unsafe_allow_html=True)
    st.markdown("<div class='cyber-header'>🎛️ 参数注射器</div>", unsafe_allow_html=True)
    
    w0 = st.slider("初始工资率 (w₀ 元/小时)", 5, 100, 15, key="w0")
    w1 = st.slider("冲击后新工资率 (w₁ 元/小时)", 5, 100, w0 + 20, key="w1")
    V = st.slider("非劳动收入 (V 元/天)", 0, 500, 150, step=10, key="V",
                  help="如：基金分红、房屋租金、家人转账等不依赖劳动的每日收入")
    
    st.markdown("<hr style='border-color: rgba(56, 189, 248, 0.2);'>", unsafe_allow_html=True)
    st.markdown("<div class='cyber-header'>🎚️ 工资冲击进度</div>", unsafe_allow_html=True)
    
    progress = st.slider("拖动滑块，亲手观察曲线变化 👇", 0, 100, 0, 1, key="progress",
                         help="0% = 初始状态 → 100% = 工资冲击完全生效")
    
    # 进度阶段指示
    if progress < 5:
        st.info("📍 **初始均衡** — 工资尚未变化")
    elif progress < 50:
        st.warning(f"⚡ **替代效应区** — 工资上升 {progress:.0f}%，闲暇变贵，你愿意多工作吗？")
    else:
        st.success(f"💰 **收入效应区** — 工资已升 {progress:.0f}%，收入增加，你想享受更多闲暇吗？")
    
    st.markdown("<hr style='border-color: rgba(56, 189, 248, 0.2);'>", unsafe_allow_html=True)
    st.caption("📊 快捷情景")
    col_a, col_b = st.columns(2)
    with col_a:
        def _preset_rise():
            st.session_state.w0 = 15; st.session_state.w1 = 40; st.session_state.V = 150
        st.button("💰 低→高工资", use_container_width=True, key="preset_rise", on_click=_preset_rise)
    with col_b:
        def _preset_fall():
            st.session_state.w0 = 70; st.session_state.w1 = 35; st.session_state.V = 300
        st.button("📉 高→低工资", use_container_width=True, key="preset_fall", on_click=_preset_fall)
    
    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 4. 连续插值解算
# ==========================================
t = progress / 100.0  # 0 → 1

# 当前有效工资率（线性插值）
w_current = w0 + (w1 - w0) * t

# 三个关键点
L_A, Y_A, U_A = calc_equilibrium(w0, V)        # 初始 A
L_C, Y_C, U_C = calc_equilibrium(w1, V)        # 最终 C
L_B, Y_B, comp_intercept = calc_hicks_compensation(w1, U_A)  # 希克斯补偿 B

# 当前点位置（沿弧线从 A 到 C）
# 前半段：沿旧无差异曲线的替代路径（w_current, U_A 约束）
# 后半段：沿新预算线的收入路径（w1, 效用从 U_A 过渡到 U_C）
if t < 0.4:
    # 替代效应阶段：工资在变，但效用保持在 U_A
    t_sub = t / 0.4  # 映射到 0→1
    L_star_sub, Y_star_sub, intercept_sub = calc_hicks_compensation(
        w0 + (w1 - w0) * t_sub, U_A
    )
    L_current = L_star_sub
    Y_current = Y_star_sub
    # 当前预算线使用实际工资 w_current
    phase = "sub"
else:
    # 收入效应阶段：工资固定为 w1，效用从 U_A 过渡到 U_C
    t_inc = (t - 0.4) / 0.6  # 映射到 0→1
    L_current = L_B + (L_C - L_B) * t_inc
    Y_current = w1 * (24 - L_current) + V
    phase = "inc"

# 实际效用
U_current = L_current * Y_current

L_plot = np.linspace(0.1, 25, 200)

# ==========================================
# 5. Plotly 动态可视化
# ==========================================
fig = go.Figure()

# --- 始终显示：旧预算线 + 旧无差异曲线 + A 点 ---
fig.add_trace(go.Scatter(
    x=[0, 24, 24], y=[w0 * 24 + V, V, 0],
    mode='lines', name="初始预算线 (w₀)",
    line=dict(color='rgba(148, 163, 184, 0.5)', width=1.5, dash='dot'),
    hovertemplate='初始工资 {w0}元/h<extra></extra>'.replace('{w0}', str(w0))
))

Y_indiff_A = calc_indifference_curve(U_A, L_plot)
fig.add_trace(go.Scatter(
    x=L_plot, y=Y_indiff_A,
    mode='lines', name="初始效用 U₀",
    line=dict(color='rgba(59, 130, 246, 0.4)', width=2, dash='dot'),
    hovertemplate='初始效用水平<extra></extra>'
))

fig.add_trace(go.Scatter(
    x=[L_A], y=[Y_A],
    mode='markers+text', name="均衡点 A",
    text=["A"], textposition="top right",
    textfont=dict(size=16, color='#3b82f6', family='Arial Black'),
    marker=dict(size=14, color='#3b82f6', line=dict(width=2, color='white')),
    hovertemplate=f'<b>点A：初始均衡</b><br>闲暇: {L_A:.1f}h | 工作: {24-L_A:.1f}h<br>收入: {Y_A:.0f}元 | 效用: {U_A:.0f}<extra></extra>'
))

# --- 当前预算线（随 w_current 旋转） ---
fig.add_trace(go.Scatter(
    x=[0, 24, 24], y=[w_current * 24 + V, V, 0],
    mode='lines', name=f"当前预算线 (w={w_current:.0f})",
    line=dict(color='#38bdf8', width=3.5),
    hovertemplate=f'当前工资 {w_current:.0f}元/h<extra></extra>'
))

# --- 希克斯补偿预算线（辅助线） ---
if progress > 5:
    fig.add_trace(go.Scatter(
        x=[0, 24], y=[comp_intercept, comp_intercept - w1 * 24],
        mode='lines', name="希克斯补偿线",
        line=dict(color='#fbbf24', width=2, dash='dash'),
        hovertemplate='💡 保持原效用U₀<extra></extra>'
    ))
    
    # B 点（纯替代效应终点）
    fig.add_trace(go.Scatter(
        x=[L_B], y=[Y_B],
        mode='markers+text', name="替代终点 B",
        text=["B"], textposition="bottom left",
        textfont=dict(size=14, color='#fbbf24', family='Arial Black'),
        marker=dict(size=12, color='#fbbf24', symbol='diamond', line=dict(width=2, color='white')),
        hovertemplate=f'<b>点B：纯替代效应</b><br>闲暇 -{L_A-L_B:.1f}h → 多工作<br>效用不变 (补偿后)<extra></extra>'
    ))

# --- 新预算线 + 新无差异曲线 + C 点 ---
if progress > 40:
    Y_indiff_C = calc_indifference_curve(U_C, L_plot)
    fig.add_trace(go.Scatter(
        x=[0, 24, 24], y=[w1 * 24 + V, V, 0],
        mode='lines', name="新预算线 (w₁)",
        line=dict(color='#34d399', width=2, dash='dot'),
        hovertemplate=f'目标工资 {w1}元/h<extra></extra>'
    ))
    
    fig.add_trace(go.Scatter(
        x=L_plot, y=Y_indiff_C,
        mode='lines', name="新效用 U₁",
        line=dict(color='rgba(52, 211, 153, 0.4)', width=2, dash='dot'),
        hovertemplate='目标效用水平<extra></extra>'
    ))
    
    fig.add_trace(go.Scatter(
        x=[L_C], y=[Y_C],
        mode='markers+text', name="最终均衡 C",
        text=["C"], textposition="top right",
        textfont=dict(size=16, color='#34d399', family='Arial Black'),
        marker=dict(size=16, color='#34d399', symbol='star', line=dict(width=2, color='white')),
        hovertemplate=f'<b>点C：最终均衡</b><br>闲暇: {L_C:.1f}h | 工作: {24-L_C:.1f}h<br>收入: {Y_C:.0f}元 | 效用: {U_C:.0f}<extra></extra>'
    ))

# --- 当前点（拖动的圆球） ---
fig.add_trace(go.Scatter(
    x=[L_current], y=[Y_current],
    mode='markers', name="📍 当前位置",
    marker=dict(size=22, color='#00f2fe', symbol='circle',
                line=dict(width=4, color='white'),
                opacity=0.9),
    hovertemplate=(
        f'<b>🎚️ 当前位置 (进度 {progress}%)</b><br>'
        f'闲暇: {L_current:.1f}h | 工作: {24-L_current:.1f}h<br>'
        f'收入: {Y_current:.0f}元 | 效用: {U_current:.0f}<br>'
        f'当前工资: {w_current:.0f}元/h<extra></extra>'
    )
))

# --- 拖尾轨迹 ---
trail_L = []
trail_Y = []
for ti in np.linspace(0, t, min(30, max(2, progress // 3 + 2))):
    w_ti = w0 + (w1 - w0) * ti
    if ti < 0.4:
        t_sub_i = ti / 0.4
        L_ti, Y_ti, _ = calc_hicks_compensation(w0 + (w1 - w0) * t_sub_i, U_A)
    else:
        t_inc_i = (ti - 0.4) / 0.6
        L_ti = L_B + (L_C - L_B) * t_inc_i
        Y_ti = w1 * (24 - L_ti) + V
    trail_L.append(L_ti)
    trail_Y.append(Y_ti)

if len(trail_L) > 1:
    fig.add_trace(go.Scatter(
        x=trail_L, y=trail_Y,
        mode='lines', name="运动轨迹",
        line=dict(color='rgba(0, 242, 254, 0.4)', width=2),
        hoverinfo='skip'
    ))

# --- 效应标注 ---
if progress > 5:
    sub_L = L_A - L_B
    inc_L = L_B - L_C
    # 替代效应标注
    if progress < 60:
        fig.add_annotation(
            x=(L_A + L_B) / 2, y=Y_A * 0.65,
            text=f"替代效应<br>闲暇 -{sub_L:.1f}h",
            showarrow=False,
            font=dict(size=11, color="#fbbf24"),
            bgcolor="rgba(0,0,0,0.6)",
            borderpad=4
        )
    # 收入效应标注
    if progress > 50:
        inc_dir = "增" if inc_L < 0 else "减"
        fig.add_annotation(
            x=(L_B + L_C) / 2, y=Y_B * 0.35,
            text=f"收入效应<br>闲暇 {inc_dir} {abs(inc_L):.1f}h",
            showarrow=False,
            font=dict(size=11, color="#34d399" if inc_L < 0 else "#ef4444"),
            bgcolor="rgba(0,0,0,0.6)",
            borderpad=4
        )

fig.update_layout(
    xaxis_title="闲暇时间 L (小时/天)",
    yaxis_title="总收入 Y (元/天)",
    xaxis=dict(range=[0, 26], gridcolor="rgba(51, 65, 85, 0.3)"),
    yaxis=dict(range=[0, max(w1 * 24 + V, comp_intercept) + 80], gridcolor="rgba(51, 65, 85, 0.3)"),
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
# 6. 动态诊断报告
# ==========================================
st.markdown("<div class='tech-card'>", unsafe_allow_html=True)
st.markdown("<div class='cyber-header'>💡 孪生系统智能诊断报告</div>", unsafe_allow_html=True)

sub_L = L_A - L_B
inc_L = L_C - L_B  # 注意符号：L_C - L_B（C在B左边=闲暇减少=继续多工作, C在B右边=闲暇回弹）
total_work = (24 - L_C) - (24 - L_A)

col_r1, col_r2 = st.columns(2)
with col_r1:
    if progress < 20:
        st.info(
            f"📍 **工资尚未显著变化** (w = {w_current:.0f} 元/h)\n\n"
            f"当前劳动者每天工作 **{24 - L_current:.1f} 小时**，"
            f"享受闲暇 **{L_current:.1f} 小时**。\n\n"
            f"👈 **向右拖动滑块**，施加工资冲击，观察预算线如何旋转！"
        )
    elif progress < 60:
        st.warning(
            f"⚡ **替代效应正在进行**\n\n"
            f"工资 {w0} → {w_current:.0f} 元/h（进度 {progress}%）\n\n"
            f"闲暇的「机会成本」变高了。你看到点沿着 U₀ 向左滑动——\n"
            f"这是在同一条无差异曲线上 **用劳动替代闲暇**。\n\n"
            f"当前工作时间已增加 **{(24-L_current) - (24-L_A):.1f} 小时**"
        )
    else:
        st.success(
            f"💰 **收入效应介入**\n\n"
            f"工资已升至 {w1} 元/h。你看到点开始离开 U₀ 向上跃迁——\n"
            f"收入提高了，可以「购买」更多闲暇。\n\n"
            f"最终均衡：工作 **{24 - L_C:.1f}h**，闲暇 **{L_C:.1f}h**"
        )

with col_r2:
    if progress > 20:
        c1, c2 = st.columns(2)
        with c1:
            st.metric("替代效应", f"闲暇 -{L_A - L_B:.1f}h", delta="多工作")
        with c2:
            inc_sign = "多工作" if inc_L > 0 else "回弹"
            st.metric("收入效应", f"闲暇 {inc_L:+.1f}h", delta=inc_sign, delta_color="inverse" if inc_L < 0 else "normal")
        
        if progress > 60:
            net = (24 - L_C) - (24 - L_A)
            dominant = "替代效应主导 → 正斜率" if net > 0 else "收入效应主导 → 向后弯曲"
            st.metric("总效应", f"劳动 {net:+.1f}h", delta=dominant)

st.markdown("---")
if progress > 80:
    if (24 - L_C) > (24 - L_A):
        st.success(f"⚖️ **替代效应 > 收入效应** — 工资上升使劳动供给净增加 **{total_work:+.1f}h**。劳动者处于正斜率的劳动供给区间。")
    else:
        st.error(f"⚖️ **收入效应 > 替代效应** — 工资上升使劳动供给净减少 **{abs(total_work):.1f}h**。这就是「向后弯曲的劳动供给曲线」的微观基础！")

st.markdown("</div>", unsafe_allow_html=True)
