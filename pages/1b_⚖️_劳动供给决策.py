"""
劳动供给决策实验室 — 收入效应 vs 替代效应分步拆解
教学竞赛级：脚手架式探究 (Learning Scaffolding) + Cobb-Douglas 精确解算
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
    .stApp label, .stApp p, .stApp span,
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
    .stApp li, .stApp strong, .stApp b, .stApp em, .stMarkdown {
        color: #e2e8f0 !important;
    }
    .stMarkdown table th, .stMarkdown table td {
        border-color: rgba(148, 163, 184, 0.3) !important;
        color: #cbd5e1 !important;
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
col_ctrl, col_graph = st.columns([1, 2.5])

with col_ctrl:
    st.markdown("<div class='tech-card'>", unsafe_allow_html=True)
    st.markdown("<div class='cyber-header'>🎛️ 参数注射器</div>", unsafe_allow_html=True)
    
    w0 = st.slider("初始工资率 (w₀ 元/小时)", 5, 100, 15, key="w0")
    w1 = st.slider("冲击后新工资率 (w₁ 元/小时)", 5, 100, min(w0 + 20, 100), key="w1")
    V = st.slider("非劳动收入 (V 元/天)", 0, 500, 150, step=10, key="V",
                  help="如：基金分红、房屋租金、家人转账等不依赖劳动的每日收入")
    
    st.markdown("<hr style='border-color: rgba(56, 189, 248, 0.2);'>", unsafe_allow_html=True)
    st.markdown("<div class='cyber-header'>👣 探究进度控制</div>", unsafe_allow_html=True)
    
    step = st.radio(
        "选择观测阶段：",
        ["1. 基准状态 (初始均衡 A)",
         "2. 替代效应剥离 (点 A → B)",
         "3. 收入效应与最终均衡 (点 B → C)"],
        key="step"
    )
    
    # 快捷预设
    st.markdown("<hr style='border-color: rgba(56, 189, 248, 0.2);'>", unsafe_allow_html=True)
    st.caption("📊 快捷情景")
    col_a, col_b = st.columns(2)
    with col_a:
        def _preset_rise():
            st.session_state.w0 = 15
            st.session_state.w1 = 40
            st.session_state.V = 150
        st.button("💰 低→高工资", use_container_width=True, key="preset_rise", on_click=_preset_rise)
    with col_b:
        def _preset_fall():
            st.session_state.w0 = 70
            st.session_state.w1 = 35
            st.session_state.V = 300
        st.button("📉 高→低工资", use_container_width=True, key="preset_fall", on_click=_preset_fall)
    
    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 数据解算
# ==========================================
L_array = np.linspace(0.1, 25, 200)

# A 点：初始均衡
L_A, Y_A, U_A = calc_equilibrium(w0, V)
# C 点：最终均衡
L_C, Y_C, U_C = calc_equilibrium(w1, V)
# B 点：希克斯补偿
L_B, Y_B, comp_intercept = calc_hicks_compensation(w1, U_A)

# 效应量
sub_effect = L_A - L_B  # 替代效应：闲暇减少量（正=劳动增加）
inc_effect = L_B - L_C  # 收入效应：闲暇回弹量（正=再次减少，负=回增）

# ==========================================
# Plotly 赛博可视化
# ==========================================
fig = go.Figure()

# --- 第一阶段：A 点基准 ---
fig.add_trace(go.Scatter(
    x=[0, 24, 24], y=[w0 * 24 + V, V, 0],
    mode='lines', name="初始预算线",
    line=dict(color='rgba(148, 163, 184, 0.8)', width=2),
    hovertemplate='闲暇: %{x:.1f}h<br>收入: %{y:.0f}元<extra></extra>'
))

Y_indiff_A = calc_indifference_curve(U_A, L_array)
fig.add_trace(go.Scatter(
    x=L_array, y=Y_indiff_A,
    mode='lines', name="初始效用 U₀",
    line=dict(color='#3b82f6', width=3),
    hovertemplate='闲暇: %{x:.1f}h<br>收入: %{y:.0f}元<br>效用 U₀<extra></extra>'
))

fig.add_trace(go.Scatter(
    x=[L_A], y=[Y_A],
    mode='markers+text', name="均衡点 A",
    text=["A"], textposition="top right",
    textfont=dict(size=16, color='#3b82f6', family='Arial Black'),
    marker=dict(size=16, color='#3b82f6', line=dict(width=2, color='white')),
    hovertemplate=(
        f'<b>点A：初始均衡</b><br>'
        f'闲暇: {L_A:.1f}h | 工作: {24-L_A:.1f}h<br>'
        f'收入: {Y_A:.0f}元 | 工资: {w0}元/h<br>'
        f'效用: {U_A:.0f}<extra></extra>'
    )
))

# --- 第二阶段：替代效应 B 点 ---
if "2" in step or "3" in step:
    # 希克斯补偿线
    fig.add_trace(go.Scatter(
        x=[0, 24], y=[comp_intercept, comp_intercept - w1 * 24],
        mode='lines', name="希克斯补偿线",
        line=dict(color='#fbbf24', width=2.5, dash='dash'),
        hovertemplate='闲暇: %{x:.1f}h<br>💡 补偿预算线（保持旧效用）<extra></extra>'
    ))
    
    fig.add_trace(go.Scatter(
        x=[L_B], y=[Y_B],
        mode='markers+text', name="虚拟点 B",
        text=["B"], textposition="bottom left",
        textfont=dict(size=16, color='#fbbf24', family='Arial Black'),
        marker=dict(size=16, color='#fbbf24', symbol='diamond', line=dict(width=2, color='white')),
        hovertemplate=(
            f'<b>点B：纯替代效应</b><br>'
            f'闲暇减少: {sub_effect:.2f}h → 多工作<br>'
            f'效用不变(补偿后)<br>'
            f'💡 工资↑→闲暇变贵→多工作<extra></extra>'
        )
    ))
    
    # 替代效应箭头 A→B
    fig.add_annotation(
        x=L_B, y=Y_A * 0.55, ax=L_A, ay=Y_A * 0.55,
        xref="x", yref="y", axref="x", ayref="y",
        showarrow=True, arrowhead=3, arrowcolor="#fbbf24", arrowsize=1.8,
        text=f"替代效应<br>闲暇 -{sub_effect:.1f}h", font=dict(size=11, color="#fbbf24")
    )

# --- 第三阶段：收入效应 C 点 ---
if "3" in step:
    # 新预算线
    fig.add_trace(go.Scatter(
        x=[0, 24, 24], y=[w1 * 24 + V, V, 0],
        mode='lines', name="新预算线",
        line=dict(color='#34d399', width=3),
        hovertemplate='闲暇: %{x:.1f}h<br>收入: %{y:.0f}元<br>新预算 (w₁)<extra></extra>'
    ))
    
    Y_indiff_C = calc_indifference_curve(U_C, L_array)
    fig.add_trace(go.Scatter(
        x=L_array, y=Y_indiff_C,
        mode='lines', name="新效用 U₁",
        line=dict(color='#34d399', width=3),
        hovertemplate='闲暇: %{x:.1f}h<br>收入: %{y:.0f}元<br>效用 U₁<extra></extra>'
    ))
    
    fig.add_trace(go.Scatter(
        x=[L_C], y=[Y_C],
        mode='markers+text', name="最终均衡 C",
        text=["C"], textposition="top right",
        textfont=dict(size=16, color='#34d399', family='Arial Black'),
        marker=dict(size=18, color='#34d399', symbol='star', line=dict(width=2, color='white')),
        hovertemplate=(
            f'<b>点C：最终均衡</b><br>'
            f'闲暇: {L_C:.1f}h | 工作: {24-L_C:.1f}h<br>'
            f'收入: {Y_C:.0f}元 | 工资: {w1}元/h<br>'
            f'效用: {U_C:.0f}<extra></extra>'
        )
    ))
    
    # 收入效应箭头 B→C
    inc_dir = "回增" if inc_effect < 0 else "续减"
    inc_text = f"收入效应<br>闲暇 {inc_dir} {abs(inc_effect):.1f}h"
    fig.add_annotation(
        x=L_C, y=Y_B * 0.3, ax=L_B, ay=Y_B * 0.3,
        xref="x", yref="y", axref="x", ayref="y",
        showarrow=True, arrowhead=3, arrowcolor="#34d399", arrowsize=1.8,
        text=inc_text, font=dict(size=11, color="#34d399")
    )

# 图表布局
fig.update_layout(
    xaxis_title="闲暇时间 L (小时/天)",
    yaxis_title="总收入 Y (元/天)",
    xaxis=dict(range=[0, 26], gridcolor="rgba(51, 65, 85, 0.3)", zerolinecolor="rgba(100, 116, 139, 0.5)"),
    yaxis=dict(range=[0, max(w1 * 24 + V, comp_intercept) + 80], gridcolor="rgba(51, 65, 85, 0.3)", zerolinecolor="rgba(100, 116, 139, 0.5)"),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#e2e8f0", size=13),
    height=550,
    margin=dict(l=40, r=20, t=40, b=40),
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
        f"📍 **当前阶段：基准状态**\n\n"
        f"在初始工资 **{w0} 元/小时** 下，劳动者每天选择享受 **{L_A:.1f} 小时** 闲暇，"
        f"工作 **{24 - L_A:.1f} 小时**，日收入 **{Y_A:.0f} 元**。\n\n"
        f"无差异曲线与预算线在 **点A** 处相切，达到效用最大化（U = {U_A:.0f}）。\n\n"
        f"👉 请切换到「第二阶段」施加工资冲击，观察替代效应。"
    )

elif "2" in step:
    st.warning(
        f"⚡ **替代效应已显现**\n\n"
        f"工资从 {w0} → {w1} 元/小时后，闲暇的「机会成本」变高了！\n\n"
        f"🔹 如果只考虑**价格变化**（保持原有效用水平不变，沿虚线滑动）：\n"
        f"　　劳动者会将闲暇减少 **{sub_effect:.2f} 小时**（即多工作 {sub_effect:.2f}h），\n"
        f"　　这是**纯粹的替代效应**——闲暇变贵，用劳动替代闲暇。\n\n"
        f"👉 切换到「第三阶段」，观察收入效应如何抵消这一趋势。"
    )

elif "3" in step:
    total_work_change = sub_effect + inc_effect
    
    col_r1, col_r2, col_r3 = st.columns(3)
    with col_r1:
        render_metric_card("替代效应", f"闲暇 -{sub_effect:.2f} h", "positive")
        st.caption("工资↑ → 闲暇变贵 → 多工作")
    with col_r2:
        inc_color = "negative" if inc_effect < 0 else "positive"
        inc_sign = "-" if inc_effect < 0 else "+"
        render_metric_card("收入效应", f"闲暇 {inc_sign}{abs(inc_effect):.2f} h", inc_color)
        st.caption("工资↑ → 变富了 → 可能少工作")
    with col_r3:
        if total_work_change > 0:
            st.success(
                f"**替代效应主导**\n\n"
                f"工作时间净增 **+{total_work_change:.2f} h**\n\n"
                f"劳动者仍处于「为收入而工作」阶段\n"
                f"→ 正斜率的劳动供给区间"
            )
        else:
            st.warning(
                f"**收入效应主导**\n\n"
                f"工作时间净变化 **{total_work_change:.2f} h**\n\n"
                f"工资越高，越愿享受闲暇\n"
                f"→ 向后弯曲的劳动供给曲线！"
            )
    
    st.markdown("---")
    st.success(
        f"⚖️ **双效应博弈完成**\n\n"
        f"随着真实收入提升，劳动者觉得自己「变富了」，"
        f"于是赎回了 **{abs(inc_effect):.2f} 小时** 的闲暇（点B → 点C，即**收入效应**）。\n\n"
        f"最终均衡：每天闲暇 **{L_C:.1f} h**，工作 **{24 - L_C:.1f} h**，日收入 **{Y_C:.0f} 元**（效用 U = {U_C:.0f}）\n\n"
        f"🔑 **核心结论**：当工资上升时，替代效应推动劳动供给 ↑，收入效应推动劳动供给 ↓。"
        f"两者博弈决定了劳动供给曲线的形状——这正是「向后弯曲的劳动供给曲线」的微观基础。"
    )

st.markdown("</div>", unsafe_allow_html=True)
