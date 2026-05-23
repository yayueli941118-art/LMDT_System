"""
⚖️ 劳动供给决策实验室 — 收入效应 vs 替代效应分解
国赛级交互模块：解决"最难懂的概念"痛点
"""

import streamlit as st
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import sys
import os

# 添加共享模块路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from shared import (
    COLOR, SHARED_CSS, get_lab_css,
    render_page_banner, render_metric_card, render_card_header,
    calc_income_substitution_effect,
    generate_lab_report, generate_report_download,
)

# ==========================================
# 页面配置
# ==========================================
st.set_page_config(page_title="劳动供给决策", page_icon="⚖️", layout="wide")

# 注入主题 CSS（紫色系，与宏观区分）
st.markdown(SHARED_CSS(color="#8b5cf6", dark="#4c1d95", light="#7c3aed"), unsafe_allow_html=True)

# ==========================================
# Banner
# ==========================================
render_page_banner(
    icon="⚖️",
    title="劳动供给决策实验室",
    subtitle="收入效应 vs 替代效应",
    theme="purple"
)

# ==========================================
# 教学引导
# ==========================================
st.markdown("""
<div class="card" style="background: linear-gradient(135deg, #ede9fe 0%, #f3e8ff 100%); border-color: #a78bfa;">
<h4 style="color:#5b21b6;">📖 核心概念</h4>
<p>当工资率上升时，劳动者的工作时间会如何变化？答案取决于<strong>两种效应的博弈</strong>：</p>
<ul>
<li><strong>替代效应 (Substitution Effect)</strong>：工资高了 → 闲暇的"价格"变贵 → 你愿意<strong>多工作</strong>（用劳动替代闲暇）</li>
<li><strong>收入效应 (Income Effect)</strong>：工资高了 → 同样的工作时间能赚更多 → 你<strong>少工作</strong>也可以维持生活水平</li>
</ul>
<p>当工资水平较低时，替代效应 > 收入效应 → 劳动供给 <strong>↑</strong>；当工资水平较高时，收入效应 > 替代效应 → 劳动供给可能 <strong>↓</strong>（向后弯曲的劳动供给曲线）。</p>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 参数设置
# ==========================================
st.markdown('<div class="card">', unsafe_allow_html=True)
render_card_header("🎛️ 实验参数设置", color="#8b5cf6", dark_color="#4c1d95")

col1, col2, col3, col4 = st.columns(4)
with col1:
    wage_initial = st.slider("初始工资率 (元/小时)", 10, 100, 25, key="wage_init")
with col2:
    wage_new = st.slider("新工资率 (元/小时)", 15, 100, 45, key="wage_new_slider")
with col3:
    beta = st.slider("闲暇偏好 β（越大越爱休息）", 0.2, 0.8, 0.5, 0.05,
                      help="β=0.5表示闲暇与消费同等重要；β>0.5表示更重视闲暇")
with col4:
    st.markdown("##### 📊 情景预设")
    
    def _preset_rise():
        st.session_state.wage_init = 20
        st.session_state.wage_new_slider = 40
        st.session_state.beta_slider = 0.5
    
    def _preset_fall():
        st.session_state.wage_init = 80
        st.session_state.wage_new_slider = 40
        st.session_state.beta_slider = 0.5
    
    col4a, col4b = st.columns(2)
    with col4a:
        st.button("💰 低工资→高工资", use_container_width=True, key="preset_rise", on_click=_preset_rise)
    with col4b:
        st.button("📉 高工资→低工资", use_container_width=True, key="preset_fall", on_click=_preset_fall)

st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 核心计算
# ==========================================
results = calc_income_substitution_effect(wage_initial, wage_new, beta)
T = 24

# 生成预算线数据
L_range = np.linspace(0.5, T - 0.5, 100)

# 初始预算线
C_budget_init = wage_initial * L_range
# 新高预算线
C_budget_new = wage_new * L_range
# 补偿预算线（过L_substitution点，斜率=wage_new）
# C = C_substitution + wage_new * (L - L_substitution)
compensation_intercept = results["C_substitution"] - wage_new * results["L_substitution"]
C_budget_comp = compensation_intercept + wage_new * L_range

# 无差异曲线数据（初始效用水平）
U0 = (results["L_initial"] ** beta) * (results["C_initial"] ** (1 - beta))
L_ic = np.linspace(1, T - 1, 100)
C_ic_init = (U0 / (L_ic ** beta)) ** (1 / (1 - beta))
C_ic_init = np.clip(C_ic_init, 0, wage_new * T)  # 限制范围

# ==========================================
# 步骤式教学展示
# ==========================================
st.markdown('<div class="card">', unsafe_allow_html=True)
render_card_header("📊 分步解析：收入效应与替代效应", color="#8b5cf6", dark_color="#4c1d95")

show_step = st.radio("选择展示步骤：",
                     ["🔴 步骤1：初始均衡 (点A)",
                      "🟡 步骤2：工资上升 → 替代效应 (点A → 点B)",
                      "🟢 步骤3：收入效应 → 最终均衡 (点B → 点C)",
                      "🔵 全部展示 (点A → 点B → 点C)"],
                     index=3, horizontal=True)

# 构建图表
fig = go.Figure()

# 预算线
fig.add_trace(go.Scatter(x=L_range, y=C_budget_init,
    mode='lines', name=f'初始预算线 (w={wage_initial})',
    line=dict(color='#94a3b8', width=2, dash='dash')))

if show_step in ["🟡 步骤2：工资上升 → 替代效应 (点A → 点B)", 
                 "🟢 步骤3：收入效应 → 最终均衡 (点B → 点C)",
                 "🔵 全部展示 (点A → 点B → 点C)"]:
    # 新高预算线
    fig.add_trace(go.Scatter(x=L_range, y=C_budget_new,
        mode='lines', name=f'新高预算线 (w={wage_new})',
        line=dict(color='#3b82f6', width=3)))
    
    # 补偿预算线（虚线，过B点，斜率=新高工资）
    L_comp_range = np.linspace(
        max(0.5, results["L_substitution"] - 6),
        min(T - 0.5, results["L_substitution"] + 6),
        50
    )
    C_comp_line = compensation_intercept + wage_new * L_comp_range
    C_comp_line = np.clip(C_comp_line, 0, wage_new * T)
    valid_mask = C_comp_line > 0
    fig.add_trace(go.Scatter(
        x=L_comp_range[valid_mask], y=C_comp_line[valid_mask],
        mode='lines', name='补偿预算线 (虚)',
        line=dict(color='#f59e0b', width=2, dash='dot')))

# 无差异曲线
fig.add_trace(go.Scatter(x=L_ic, y=C_ic_init,
    mode='lines', name=f'无差异曲线 U₀',
    line=dict(color='#d1d5db', width=2)))

# 标注点A：初始均衡
fig.add_trace(go.Scatter(
    x=[results["L_initial"]], y=[results["C_initial"]],
    mode='markers+text', name='点A：初始均衡',
    marker=dict(size=18, color='#ef4444', symbol='circle', line=dict(width=2, color='white')),
    text=['A'], textposition='top center',
    textfont=dict(size=14, color='#ef4444', family='Arial Black'),
    hovertemplate=(
        f'<b>点A：初始均衡</b><br>'
        f'工作时间: {results["L_initial"]:.1f} 小时<br>'
        f'休闲时间: {T - results["L_initial"]:.1f} 小时<br>'
        f'日收入: {results["C_initial"]:.1f} 元<br>'
        f'工资率: {wage_initial} 元/小时<br>'
        f'<extra></extra>'
    )
))

if show_step in ["🟡 步骤2：工资上升 → 替代效应 (点A → 点B)", 
                 "🟢 步骤3：收入效应 → 最终均衡 (点B → 点C)",
                 "🔵 全部展示 (点A → 点B → 点C)"]:
    # 点B：替代效应后
    fig.add_trace(go.Scatter(
        x=[results["L_substitution"]], y=[results["C_substitution"]],
        mode='markers+text', name='点B：替代效应',
        marker=dict(size=18, color='#f59e0b', symbol='diamond', line=dict(width=2, color='white')),
        text=['B'], textposition='top center',
        textfont=dict(size=14, color='#f59e0b', family='Arial Black'),
        hovertemplate=(
            f'<b>点B：纯替代效应</b><br>'
            f'工作时间: {results["L_substitution"]:.1f} 小时<br>'
            f'日收入: {results["C_substitution"]:.1f} 元<br>'
            f'替代效应: {results["substitution_effect"]:+.1f} 小时<br>'
            f'💡 工资提高，闲暇变贵，多工作！<br>'
            f'<extra></extra>'
        )
    ))
    
    # 点A→B的箭头线
    fig.add_annotation(x=results["L_substitution"], y=results["C_substitution"],
        text=f'替代效应：{results["substitution_effect"]:+.1f}h',
        ax=results["L_initial"], ay=results["C_initial"],
        showarrow=True, arrowhead=2, arrowsize=1.5,
        arrowcolor='#f59e0b',
        font=dict(size=12, color='#92400e'))

if show_step in ["🟢 步骤3：收入效应 → 最终均衡 (点B → 点C)",
                 "🔵 全部展示 (点A → 点B → 点C)"]:
    # 点C：最终均衡
    fig.add_trace(go.Scatter(
        x=[results["L_final"]], y=[results["C_final"]],
        mode='markers+text', name='点C：最终均衡',
        marker=dict(size=20, color='#10b981', symbol='star', line=dict(width=2, color='white')),
        text=['C'], textposition='top center',
        textfont=dict(size=16, color='#10b981', family='Arial Black'),
        hovertemplate=(
            f'<b>点C：最终均衡</b><br>'
            f'工作时间: {results["L_final"]:.1f} 小时<br>'
            f'日收入: {results["C_final"]:.1f} 元<br>'
            f'收入效应: {results["income_effect"]:+.1f} 小时<br>'
            f'{("💡 收入提高，享受更多闲暇，少工作！" if results["income_effect"] < 0 else "💡 收入尚未产生明显抑制效应")}<br>'
            f'<extra></extra>'
        )
    ))
    
    # 点B→C的箭头线
    fig.add_annotation(x=results["L_final"], y=results["C_final"],
        text=f'收入效应：{results["income_effect"]:+.1f}h',
        ax=results["L_substitution"], ay=results["C_substitution"],
        showarrow=True, arrowhead=2, arrowsize=1.5,
        arrowcolor='#10b981',
        font=dict(size=12, color='#065f46'))

fig.update_layout(
    xaxis=dict(title="工作时间 L (小时/天)", range=[0, T], dtick=4),
    yaxis=dict(title="日消费/收入 C (元/天)", range=[0, wage_new * T * 1.1]),
    template="plotly_white",
    height=550,
    margin=dict(l=20, r=20, t=10, b=20),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    hovermode='closest'
)

st.plotly_chart(fig, use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 数值分解表格
# ==========================================
st.markdown('<div class="card">', unsafe_allow_html=True)
render_card_header("📋 效应分解明细", color="#8b5cf6", dark_color="#4c1d95")

c1, c2, c3, c4 = st.columns(4)
with c1:
    sub_color = "positive" if results["substitution_effect"] > 0 else "negative"
    render_metric_card("替代效应（工作小时变化）", f"{results['substitution_effect']:+.2f} h", sub_color)
    st.caption("工资↑ → 闲暇变贵 → 多工作")
    
with c2:
    inc_color = "negative" if results["income_effect"] < 0 else ("positive" if results["income_effect"] > 0 else "neutral")
    render_metric_card("收入效应（工作小时变化）", f"{results['income_effect']:+.2f} h", inc_color)
    st.caption("工资↑ → 同样收入更少工作 → 可能少工作")
    
with c3:
    total_color = "positive" if results["total_effect"] > 0 else ("negative" if results["total_effect"] < 0 else "neutral")
    render_metric_card("净效应（总变化）", f"{results['total_effect']:+.2f} h", total_color)
    st.caption("替代效应 + 收入效应")
    
with c4:
    dominant = "替代效应占主导" if results["substitution_effect"] + results["income_effect"] > 0 else "收入效应占主导"
    dominant_color = "positive" if "替代" in dominant else "negative"
    render_metric_card("主导效应", dominant, dominant_color)

st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 文字解释
# ==========================================
st.markdown('<div class="card">', unsafe_allow_html=True)
render_card_header("📝 经济学解释", color="#8b5cf6", dark_color="#4c1d95")

# 动态解释
if results["total_effect"] > 1:
    st.success(f"""
    **当前情景下，替代效应 > 收入效应**，工资从 {wage_initial} 元/小时 提高到 {wage_new} 元/小时后：
    
    - 🟡 **替代效应**使劳动者愿意多工作 **{results['substitution_effect']:.1f}** 小时（闲暇变得昂贵）
    - 🟢 **收入效应**使劳动者想少工作 **{abs(results['income_effect']):.1f}** 小时（收入已足够）
    - 🔵 **净效应**：工作时间净增加 **{results['total_effect']:.1f}** 小时
    
    这说明在当前工资水平下，劳动者仍处于「为收入而工作」阶段，替代效应占优。
    """)
elif results["total_effect"] < -0.5:
    st.warning(f"""
    **当前情景下，收入效应 > 替代效应**，工资从 {wage_initial} 元/小时 提高到 {wage_new} 元/小时后：
    
    - 🟡 **替代效应**使劳动者愿意多工作 **{results['substitution_effect']:.1f}** 小时
    - 🟢 **收入效应**使劳动者想少工作 **{abs(results['income_effect']):.1f}** 小时（工作更少也能达到目标收入）
    - 🔴 **净效应**：工作时间净减少 **{abs(results['total_effect']):.1f}** 小时
    
    这说明劳动者已进入「向后弯曲」的劳动供给区段——工资越高，反而越愿意享受闲暇。
    这正是劳动经济学中「向后弯曲的劳动供给曲线」的微观基础！
    """)
else:
    st.info(f"""
    **当前情景下，替代效应与收入效应基本抵消。**
    
    工资从 {wage_initial} 元/小时 提高到 {wage_new} 元/小时后，
    替代效应（+{results['substitution_effect']:.1f}h）与收入效应（{results['income_effect']:.1f}h）互相抵消，
    总劳动供给几乎不变。
    """)

st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 实验报告
# ==========================================
st.markdown('<div class="card">', unsafe_allow_html=True)
render_card_header("📝 实验报告生成", color="#8b5cf6", dark_color="#4c1d95")

params = {
    "初始工资率": f"{wage_initial} 元/小时",
    "新工资率": f"{wage_new} 元/小时",
    "闲暇偏好 β": f"{beta}",
}

analysis_text = f"""### 1. 工资变动与劳动供给反应
工资从 **{wage_initial} 元/小时** 提升至 **{wage_new} 元/小时**。

### 2. 效应分解
- 替代效应：劳动供给变化 **{results['substitution_effect']:+.2f}** 小时
- 收入效应：劳动供给变化 **{results['income_effect']:+.2f}** 小时
- 净效应：劳动供给总变化 **{results['total_effect']:+.2f}** 小时

### 3. 分析
{'替代效应占主导：劳动者在相对较低的工资水平下，更倾向于用劳动替代闲暇。' if results['total_effect'] > 0 else '收入效应占主导：劳动者在较高工资水平下更看重闲暇，符合向后弯曲的劳动供给曲线。'}
"""

results_pack = {
    "analysis": analysis_text,
    "reflection_questions": """
1. 如果 β 增加（劳动者更重视闲暇），替代效应和收入效应的相对大小会如何变化？
2. 现实中，为什么高收入人群的工作时间反而可能更长（如企业家、高管）？这与模型预测矛盾吗？
3. 请用本次实验结果解释"最低工资提高"可能如何影响低技能劳动者的劳动供给。
""",
    "conclusion": f"本次实验验证了工资变动的双重效应：替代效应倾向增加劳动供给，收入效应倾向减少劳动供给。当前参数下，{'替代效应' if results['total_effect'] > 0 else '收入效应'}占据主导地位。"
}

report_text = generate_lab_report("labor_supply", params, results_pack)
generate_report_download(report_text, "Labor_Supply")
st.markdown('</div>', unsafe_allow_html=True)
