"""
💰 工资决定与收入差距 — 第六章 工资与收入分配
补偿性差异+效率工资+最低工资+洛伦兹曲线+基尼系数
"""

import streamlit as st
import numpy as np
import plotly.graph_objects as go
import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from shared import SCHOOL_NAME, AUTHOR_NAME

st.set_page_config(page_title="工资决定与收入差距", page_icon="💰", layout="wide")

# ==========================================
# 赛博暗色 UI（金色系——收入/工资主题）
# ==========================================
st.markdown("""
<style>
    .stApp { background-color: #0b0f19 !important; }
    section[data-testid="stSidebar"] {
        background-color: #090d16 !important;
        border-right: 1px solid rgba(245, 158, 11, 0.1) !important;
    }
    .stApp, .stApp p, .stApp span, .stApp div,
    .stApp li, .stApp strong, .stApp b,
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
    div[data-testid="stMarkdownContainer"],
    div[data-testid="stMarkdownContainer"] * {
        color: #e2e8f0 !important;
    }
    .stMarkdown table th, .stMarkdown table td {
        border-color: rgba(148, 163, 184, 0.3) !important; color: #cbd5e1 !important;
    }
    section[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
    div[data-testid="stSlider"] label, div[data-testid="stRadio"] label {
        color: #fbbf24 !important; font-weight: 600 !important;
    }
    .tech-card {
        background: linear-gradient(145deg, rgba(30, 41, 59, 0.6) 0%, rgba(15, 23, 42, 0.8) 100%) !important;
        border: 1px solid rgba(245, 158, 11, 0.15) !important;
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
        background: #f59e0b; margin-right: 12px; border-radius: 3px;
        box-shadow: 0 0 8px #f59e0b;
    }
    .insight-box {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(180, 83, 9, 0.05) 100%);
        border-left: 3px solid #f59e0b; padding: 16px; border-radius: 4px; margin: 12px 0;
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
    <h1 style="color: #ffffff; font-weight: 900; margin-bottom: 5px;">💰 工资决定与收入差距</h1>
    <h4 style="color: #fbbf24; font-weight: 600; letter-spacing: 1px;">
        第六章 工资与收入分配 — 为什么你的工资是这么多？
    </h4>
    <p style="color: #64748b; font-size: 14px; margin-top: 4px;">
        {SCHOOL_NAME} · 课程负责人：{AUTHOR_NAME} | 补偿性差异 · 效率工资 · 最低工资 · 收入不平等
    </p>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 预测脚手架
# ==========================================
if "wage_pred_done" not in st.session_state:
    st.markdown("<div class='tech-card' style='border-color: rgba(245, 158, 11, 0.3) !important;'>", unsafe_allow_html=True)
    st.markdown("##### 🔮 先判断：工资是谁决定的？")
    pred_w = st.radio(
        "**一个人的工资，主要由什么决定？**",
        ["A. 个人能力（教育/技能/经验）",
         "B. 岗位特征（高危/枯燥/夜班→补偿性溢价）",
         "C. 市场供需（这个行业缺人还是过剩）",
         "D. 制度设计（最低工资/工会/歧视/信息不对称）"],
        key="wage_pred"
    )
    def _confirm_w_pred():
        st.session_state.wage_pred_done = True
        st.session_state.wage_pred_answer = st.session_state.wage_pred
    st.button("✅ 这是我的判断，开始实验！", key="wage_pred_btn", on_click=_confirm_w_pred)
    st.markdown("</div>", unsafe_allow_html=True)
else:
    user_pred_w = st.session_state.get("wage_pred_answer", "")
    st.info(f"📝 你的直觉：**{user_pred_w}** — 等下看看经济学怎么说。")

# ==========================================
# 三个实验 Tab
# ==========================================
tab1, tab2, tab3 = st.tabs(["🏭 补偿性工资差异", "⚡ 效率工资博弈", "📊 收入不平等"])

# ==========================================
# TAB 1: Compensating Wage Differentials
# ==========================================
with tab1:
    col_ctrl, col_graph = st.columns([1, 2.2])
    
    with col_ctrl:
        st.markdown("<div class='tech-card'>", unsafe_allow_html=True)
        st.markdown("<div class='cyber-header'>🏭 岗位特征 → 工资补偿</div>", unsafe_allow_html=True)
        
        st.markdown("**基准岗位**")
        base_wage = st.slider("基准月薪 (k)", 3, 15, 5, key="base_w")
        base_L = st.slider("基准就业量 (万人)", 10, 200, 80, key="base_L")
        
        st.markdown("---")
        st.markdown("**风险特征**")
        risk_level = st.slider("职业风险 (死亡率/千)", 0.0, 2.0, 0.5, 0.1, key="risk",
                              help="0=安全 | 2.0=极高风险（如深海捕鱼、矿工）")
        comp_premium = risk_level * 8  # 每千分之死亡率补偿8k
        
        st.markdown("---")
        st.markdown("**工作舒适度**")
        comfort = st.slider("工作舒适度", 0, 10, 7, key="comfort",
                           help="0=极端恶劣 | 10=完美环境")
        comfort_penalty = (10 - comfort) * 0.5
        
        st.markdown("---")
        st.markdown("**夜班/加班频率**")
        night_shift = st.slider("每月夜班天数", 0, 20, 0, 2, key="night")
        night_premium = night_shift * 0.3
        
        total_wage = base_wage + comp_premium + comfort_penalty + night_premium
        
        st.markdown("---")
        st.caption("📊 快捷情景")
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            def _preset_fire(): st.session_state.risk = 1.5; st.session_state.comfort = 2; st.session_state.night = 4
            st.button("🔥 消防员", key="fire", on_click=_preset_fire, use_container_width=True)
        with col_b:
            def _preset_mine(): st.session_state.risk = 2.0; st.session_state.comfort = 1; st.session_state.night = 8
            st.button("⛏️ 矿工", key="mine", on_click=_preset_mine, use_container_width=True)
        with col_c:
            def _preset_office(): st.session_state.risk = 0.0; st.session_state.comfort = 9; st.session_state.night = 0
            st.button("🪑 白领", key="office", on_click=_preset_office, use_container_width=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col_graph:
        st.markdown("<div class='tech-card'>", unsafe_allow_html=True)
        
        # 补偿性工资差异曲线：风险 vs 工资
        risk_range = np.linspace(0, 2, 50)
        risk_wages = base_wage + risk_range * 8 + comfort_penalty + night_premium
        
        fig1a = go.Figure()
        
        # 无差异曲线（工人对不同风险-工资组合等效用）
        # U = w - risk*v(aversion) - discomfort - nights
        risk_aversion = 5  # 风险厌恶系数
        
        for u_level in [base_wage - 2, base_wage, base_wage + 2, base_wage + 5, base_wage + 10]:
            w_at_u = u_level + risk_range * risk_aversion + comfort_penalty + night_premium
            fig1a.add_trace(go.Scatter(
                x=risk_range, y=w_at_u,
                mode='lines', name=f'等效用 U={u_level:.0f}',
                line=dict(width=1, dash='dot', color='rgba(148, 163, 184, 0.4)'),
                hovertemplate='风险=%{x:.2f}‰ | 所需工资=%{y:.1f}k<extra></extra>'
            ))
        
        # 市场补偿曲线
        fig1a.add_trace(go.Scatter(
            x=risk_range, y=risk_wages,
            mode='lines', name='市场补偿曲线',
            line=dict(color='#f59e0b', width=5),
            hovertemplate=(
                '风险=%{x:.2f}‰<br>'
                '补偿后工资=%{y:.1f}k<br>'
                '溢价=%{customdata:+.1f}k'
                '<extra></extra>'
            ),
            customdata=risk_wages - base_wage
        ))
        
        # 当前选择点
        fig1a.add_trace(go.Scatter(
            x=[risk_level], y=[total_wage],
            mode='markers', name='你的选择',
            marker=dict(size=22, color='#fbbf24', symbol='star', line=dict(width=3, color='white')),
            hovertemplate=f'<b>你的岗位</b><br>风险={risk_level}‰<br>工资={total_wage:.1f}k<br>溢价=+{total_wage-base_wage:.1f}k<extra></extra>'
        ))
        
        fig1a.update_layout(
            xaxis_title="职业风险 (死亡/千人)", yaxis_title="月工资 (k)",
            xaxis=dict(gridcolor="rgba(51, 65, 85, 0.3)"),
            yaxis=dict(gridcolor="rgba(51, 65, 85, 0.3)"),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e2e8f0", size=13),
            height=420, margin=dict(l=40, r=20, t=20, b=40),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color="#e2e8f0")),
            hovermode='closest'
        )
        
        st.plotly_chart(fig1a, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # 工资分解
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("🏠 基本工资", f"{base_wage:.1f}k")
    with c2:
        st.metric("⚠️ 风险补偿", f"+{comp_premium:.1f}k", delta=f"风险{risk_level}‰")
    with c3:
        st.metric("🌡️ 环境补偿", f"+{comfort_penalty:.1f}k", delta=f"舒适度{comfort}/10")
    with c4:
        st.metric("🌙 夜班补贴", f"+{night_premium:.1f}k", delta=f"夜班{night_shift}天")
    
    st.markdown(f"""
    <div class="insight-box">
    <strong>💰 亚当·斯密的补偿性工资差异理论：</strong><br>
    总工资 = {base_wage:.1f} + {comp_premium:.1f} + {comfort_penalty:.1f} + {night_premium:.1f} = <strong>{total_wage:.1f}k</strong><br><br>
    「劳动的真正报酬不在于货币工资，而在于<strong>净优势</strong>——包括工作的愉悦性、安全性、社会地位和未来的晋升前景。」<br>
    白领宁可拿更低的名义工资，因为在安全、舒适和体面上获得了补偿。<br>
    矿工的高工资不是慷慨——是他们在用身体为风险定价。
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# TAB 2: Efficiency Wage + Minimum Wage
# ==========================================
with tab2:
    col_ctrl2, col_graph2 = st.columns([1, 2.2])
    
    with col_ctrl2:
        st.markdown("<div class='tech-card'>", unsafe_allow_html=True)
        st.markdown("<div class='cyber-header'>⚡ 效率工资 & 最低工资</div>", unsafe_allow_html=True)
        
        st.markdown("**效率工资（夏皮罗-斯蒂格利茨模型）**")
        mpl_eff = st.slider("工人边际产品价值 MPL (k)", 5, 30, 12, key="mpl_eff")
        detect_rate = st.slider("怠工被抓概率 q", 0.05, 0.50, 0.20, 0.05, key="detect",
                                help="管理者监控能力：越高=越容易发现偷懒")
        unemp_rate = st.slider("失业率 u", 0.02, 0.20, 0.06, 0.01, key="unemp_eff")
        shirk_value = st.slider("偷懒的效用(闲暇价值)", 0.0, 5.0, 1.0, 0.5, key="shirk")
        
        st.markdown("---")
        st.markdown("**最低工资政策**")
        min_wage = st.slider("法定最低工资 (k)", 0.0, 15.0, 0.0, 0.5, key="min_w",
                             help="0=无最低工资")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # 效率工资计算：不偷懒条件 NSC
    # w_eff >= e + (e + b)/q * (u/(1-u)) + b
    # 简化: w_eff = mpl_eff * [1 - (1 - detect_rate * (1 - unemp_rate))] 的反向
    # 标准简化：w_eff = (e + b/q) * (1 - u)/u 近似
    # 实际：效率工资 = shirk_value/detect_rate 的某种比例
    
    no_shirk_condition = shirk_value / detect_rate * unemp_rate / (1 - unemp_rate + unemp_rate * detect_rate)
    eff_wage = mpl_eff  # 效率工资最终 = MPL（均衡）
    eff_wage_min = no_shirk_condition + 2  # NSC 门槛
    
    unemp_range = np.linspace(0.02, 0.20, 50)
    nsc_values = shirk_value / detect_rate * (unemp_range) / (1 - unemp_range + unemp_range * detect_rate)
    
    with col_graph2:
        st.markdown("<div class='tech-card'>", unsafe_allow_html=True)
        
        fig2a = go.Figure()
        
        # 劳动需求曲线 (MPL)
        L_range = np.linspace(10, 100, 60)
        demand_wage = mpl_eff * (1 - 0.005 * (L_range - 10))  # 递减MPL
        
        fig2a.add_trace(go.Scatter(
            x=L_range, y=demand_wage, name='劳动需求 (MPL)',
            line=dict(color='#3b82f6', width=3),
            hovertemplate='就业量 %{x:.0f}万<br>工资=%{y:.1f}k<extra></extra>'
        ))
        
        # 效率工资线
        fig2a.add_hline(
            y=eff_wage_min, line_dash="dash", line_color="#f59e0b", line_width=2,
            annotation_text=f"效率工资 ≈{eff_wage_min:.1f}k (NSC)",
            annotation_font=dict(color="#fbbf24")
        )
        
        # 竞争性均衡
        market_wage_idx = np.argmin(np.abs(demand_wage - mpl_eff))
        market_L = L_range[market_wage_idx]
        
        # 最低工资线
        if min_wage > 0:
            fig2a.add_hline(
                y=min_wage, line_dash="dash", line_color="#ef4444", line_width=2,
                annotation_text=f"最低工资={min_wage:.1f}k",
                annotation_font=dict(color="#f87171")
            )
            
            # 在最低工资下的就业
            eff_w = max(min_wage, eff_wage_min)
            L_min_idx = np.argmin(np.abs(demand_wage - eff_w))
            L_min = L_range[L_min_idx]
            
            fig2a.add_trace(go.Scatter(
                x=[L_min, L_min], y=[0, eff_w],
                mode='lines', name='最低工资就业',
                line=dict(color='#ef4444', width=2, dash='dot'),
                hoverinfo='skip'
            ))
            
            # 失业损失面积
            if L_min < market_L:
                fig2a.add_trace(go.Scatter(
                    x=[L_min, market_L, market_L, L_min],
                    y=[eff_w, eff_w, demand_wage[int(market_L)], demand_wage[int(market_L)]],
                    fill='toself', fillcolor='rgba(239, 68, 68, 0.1)',
                    line=dict(width=0), name='就业损失', hoverinfo='skip'
                ))
                fig2a.add_annotation(
                    x=(L_min + market_L) / 2, y=eff_w * 0.5,
                    text=f"就业损失<br>{market_L - L_min:.0f}万",
                    showarrow=False, font=dict(size=12, color="#f87171"),
                    bgcolor="rgba(0,0,0,0.6)",
                )
        
        # 市场均衡点
        fig2a.add_trace(go.Scatter(
            x=[market_L], y=[mpl_eff], mode='markers', name='市场均衡',
            marker=dict(size=14, color='#3b82f6', line=dict(width=2, color='white')),
            hovertemplate=f'竞争均衡: L={market_L:.0f}万 w={mpl_eff:.1f}k<extra></extra>'
        ))
        
        fig2a.update_layout(
            xaxis_title="就业量 (万人)", yaxis_title="工资 (k)",
            xaxis=dict(gridcolor="rgba(51, 65, 85, 0.3)"),
            yaxis=dict(range=[0, max(mpl_eff * 1.5, min_wage * 1.5 + 2)], gridcolor="rgba(51, 65, 85, 0.3)"),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e2e8f0", size=13),
            height=420, margin=dict(l=40, r=20, t=20, b=40),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color="#e2e8f0")),
            hovermode='closest'
        )
        
        st.plotly_chart(fig2a, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # 效率工资 vs 怠工条件图
    st.markdown("<div class='tech-card'>", unsafe_allow_html=True)
    st.markdown("<div class='cyber-header'>🔬 不偷懒条件 (NSC) 曲线</div>", unsafe_allow_html=True)
    
    col_nsc1, col_nsc2 = st.columns([1, 2])
    
    with col_nsc1:
        st.markdown(f"""
        **NSC 方程：**
        
        `w ≥ e + (e + b)/(q) · u/(1-u)`
        
        | 参数 | 当前值 | 影响 |
        |------|--------|------|
        | 怠工效用 | {shirk_value:.1f} | ↑→提高效率工资 |
        | 检测率 q | {detect_rate:.2f} | ↑→降低效率工资 |
        | 失业率 u | {unemp_rate:.0%} | ↑→降低效率工资 |
        
        **含义：** 失业本身是一种「纪律装置」——
        失业率越高，工人越不敢偷懒，
        雇主所需的效率工资越低。
        """)
    
    with col_nsc2:
        fig2b = go.Figure()
        fig2b.add_trace(go.Scatter(
            x=unemp_range * 100, y=nsc_values + 2,
            mode='lines', name='NSC 不偷懒曲线',
            line=dict(color='#f59e0b', width=4),
            fill='tozeroy', fillcolor='rgba(245, 158, 11, 0.1)',
            hovertemplate='失业率=%{x:.1f}%<br>所需效率工资=%{y:.1f}k<extra></extra>'
        ))
        
        # 当前点
        nsc_current = shirk_value / detect_rate * unemp_rate / (1 - unemp_rate + unemp_rate * detect_rate) + 2
        fig2b.add_trace(go.Scatter(
            x=[unemp_rate * 100], y=[nsc_current],
            mode='markers', name=f"当前 u={unemp_rate:.0%}",
            marker=dict(size=16, color='#fbbf24', symbol='star', line=dict(width=2, color='white')),
            hovertemplate=f'当前失业率={unemp_rate:.0%}<br>效率工资≥{nsc_current:.1f}k<extra></extra>'
        ))
        
        fig2b.update_layout(
            xaxis_title="失业率 (%)", yaxis_title="效率工资门槛 (k)",
            xaxis=dict(gridcolor="rgba(51, 65, 85, 0.3)"),
            yaxis=dict(gridcolor="rgba(51, 65, 85, 0.3)"),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e2e8f0", size=13),
            height=320, margin=dict(l=40, r=20, t=20, b=40),
            legend=dict(font=dict(color="#e2e8f0")),
            hovermode='closest'
        )
        st.plotly_chart(fig2b, use_container_width=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 最低工资诊断
    if min_wage > 0:
        eff_w = max(min_wage, eff_wage_min)
        L_min_idx = np.argmin(np.abs(demand_wage - eff_w))
        L_min = L_range[L_min_idx]
        emp_loss = market_L - L_min
        
        if emp_loss > 0:
            st.markdown(f"""
            <div class="insight-box">
            <strong>⚖️ 最低工资的两难：</strong><br>
            最低工资 {min_wage:.1f}k > 市场均衡工资 {mpl_eff:.1f}k<br>
            → 就业损失约 <strong>{emp_loss:.0f} 万人</strong>（{emp_loss/market_L*100:.0f}%）<br>
            → 但保住工作的劳动者工资从 {mpl_eff:.1f}k 涨到 {eff_w:.1f}k<br><br>
            <strong>经济学没有免费午餐。</strong>最低工资保护了在岗者，但可能排斥了最边缘的劳动者。
            </div>
            """, unsafe_allow_html=True)

# ==========================================
# TAB 3: Income Inequality — Lorenz Curve + Gini + Skill Premium
# ==========================================
with tab3:
    st.markdown("<div class='tech-card'>", unsafe_allow_html=True)
    st.markdown("<div class='cyber-header'>📊 收入不平等——洛伦兹曲线与基尼系数</div>", unsafe_allow_html=True)
    
    col_lc1, col_lc2 = st.columns([1, 2])
    
    with col_lc1:
        st.markdown("**🎚️ 收入分布参数**")
        inequality = st.slider("收入不平等程度", 0.1, 0.9, 0.45, 0.05, key="ineq",
                              help="0.1=高度平等 | 0.9=极度不平等")
        
        st.markdown("**📈 技能溢价趋势**")
        skill_premium = st.slider("大学溢价倍数", 1.0, 4.0, 1.8, 0.1, key="skill_p",
                                 help="大学生工资 ÷ 高中生工资")
        
        st.markdown("---")
        st.caption("📊 快捷预设")
        col_h1, col_h2 = st.columns(2)
        with col_h1:
            def _preset_sweden(): st.session_state.ineq = 0.25
            st.button("🇸🇪 瑞典型", key="sweden", use_container_width=True, on_click=_preset_sweden)
        with col_h2:
            def _preset_brazil(): st.session_state.ineq = 0.55
            st.button("🇧🇷 巴西型", key="brazil", use_container_width=True, on_click=_preset_brazil)
    
    with col_lc2:
        # 洛伦兹曲线
        pop = np.linspace(0, 100, 200)
        # 用帕累托/对数正态近似
        # Lorenz: L(p) = p^((1+ineq) / (1-ineq))
        alpha_l = (1 + inequality) / (1 - inequality) if inequality < 0.99 else 50
        lorenz = (pop / 100) ** alpha_l
        
        # 完全平等线
        perfect = pop / 100
        
        # 基尼系数
        gini = (alpha_l - 1) / (alpha_l + 1) if alpha_l > 1 else 0
        
        fig3 = go.Figure()
        
        # 完全平等线
        fig3.add_trace(go.Scatter(
            x=pop, y=perfect, name='完全平等线',
            line=dict(color='#10b981', width=1.5, dash='dash'),
            hovertemplate='完全平等: %{y:.0%}<extra></extra>'
        ))
        
        # 洛伦兹曲线
        fig3.add_trace(go.Scatter(
            x=pop, y=lorenz, name=f'洛伦兹曲线 (Gini={gini:.3f})',
            line=dict(color='#f59e0b', width=4),
            fill='tonexty', fillcolor='rgba(245, 158, 11, 0.15)',
            hovertemplate=(
                '人口累计=%{x:.0f}%<br>'
                '收入累计=%{y:.0%}<br>'
                'Gini={customdata:.3f}'
                '<extra></extra>'
            ),
            customdata=[gini] * 200
        ))
        
        fig3.add_annotation(
            x=60, y=20,
            text=f"基尼系数<br><b>{gini:.3f}</b>",
            showarrow=False, font=dict(size=16, color="#fbbf24"),
            bgcolor="rgba(0,0,0,0.7)", borderpad=8
        )
        
        fig3.update_layout(
            xaxis_title="人口累计 (%)", yaxis_title="收入累计 (%)",
            xaxis=dict(range=[0, 100], gridcolor="rgba(51, 65, 85, 0.3)"),
            yaxis=dict(range=[0, 100], gridcolor="rgba(51, 65, 85, 0.3)"),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e2e8f0", size=13),
            height=400, margin=dict(l=40, r=20, t=20, b=40),
            legend=dict(font=dict(color="#e2e8f0")),
            hovermode='closest'
        )
        
        st.plotly_chart(fig3, use_container_width=True)
    
    st.markdown("---")
    
    # Gini + 中国数据
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.markdown(f"""
        ### 📐 基尼系数解读
        
        | 区间 | 含义 | 代表国家 |
        |------|------|---------|
        | < 0.25 | 高度平等 | 🇸🇪 瑞典 |
        | 0.25-0.35 | 比较平等 | 🇩🇪 德国 |
        | 0.35-0.45 | 中等 | 🇨🇳 中国 (≈0.40-0.47) |
        | 0.45-0.55 | 较高 | 🇺🇸 美国 |
        | > 0.55 | 极高 | 🇧🇷 巴西/🇿🇦 南非 |
        
        **当前仿真基尼系数：{gini:.3f}**
        """)
    
    with col_g2:
        # 技能溢价时间序列
        years = np.array([1980, 1985, 1990, 1995, 2000, 2005, 2010, 2015, 2020, 2024])
        # 典型中国技能溢价趋势
        cn_sp = np.array([1.1, 1.2, 1.3, 1.5, 1.8, 1.9, 1.75, 1.7, 1.65, 1.6])
        us_sp = np.array([1.4, 1.5, 1.55, 1.6, 1.7, 1.8, 1.9, 1.95, 2.0, 1.95])
        
        fig3b = go.Figure()
        fig3b.add_trace(go.Scatter(
            x=years, y=cn_sp, mode='lines+markers', name='🇨🇳 中国',
            line=dict(color='#ef4444', width=3), marker=dict(size=8)
        ))
        fig3b.add_trace(go.Scatter(
            x=years, y=us_sp, mode='lines+markers', name='🇺🇸 美国',
            line=dict(color='#3b82f6', width=3), marker=dict(size=8)
        ))
        fig3b.add_hline(y=skill_premium, line_dash="dash", line_color="#fbbf24",
                        annotation_text=f"你的设定={skill_premium:.1f}×")
        
        fig3b.update_layout(
            xaxis_title="年份", yaxis_title="大学溢价 (倍数)",
            xaxis=dict(gridcolor="rgba(51, 65, 85, 0.3)"),
            yaxis=dict(range=[0.8, 2.5], gridcolor="rgba(51, 65, 85, 0.3)"),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e2e8f0", size=13),
            height=350, margin=dict(l=40, r=20, t=20, b=40),
            legend=dict(font=dict(color="#e2e8f0"))
        )
        st.plotly_chart(fig3b, use_container_width=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 课程思政
# ==========================================
st.markdown("<div class='tech-card'>", unsafe_allow_html=True)
st.markdown("<div class='cyber-header'>🏛️ 深度思考：工资的本质与共同富裕</div>", unsafe_allow_html=True)

col_ideo1, col_ideo2 = st.columns(2)

with col_ideo1:
    st.markdown("""
    ### 1. 工资不只是「价格」
    > 工资是劳动力市场上最重要的价格信号——但它同时也是**社会正义的温度计**。
    > 补偿性差异告诉我们：矿工的高工资不是慷慨，是他们在用身体为风险定价。
    > 效率工资告诉我们：工资不仅是对劳动的报酬，更是对**人的尊严**的定价。
    
    ### 2. 中国大学溢价的变迁
    > 1999年扩招前：大学生是稀缺品，溢价极高。
    > 2008年后：供给大幅增加，溢价开始回落。
    > 这意味着：单纯的文凭信号价值在下降，**真正的人力资本积累**变得比文凭本身更重要。
    """)

with col_ideo2:
    st.markdown("""
    ### 3. 最低工资：经济学与道德的交汇点
    > 「最低工资会消灭低技能岗位」 vs 「没有最低工资意味着劳动剥削」
    > 
    > 两种说法在经济模型中都有实证支持——这恰恰说明**经济学不能代替价值判断**。
    > 最低工资定多少，不仅是一个实证问题，更是一个社会共识问题。
    
    ### 4. 从效率走向公平
    > 收入不平等不仅是效率问题，更是制度问题。
    > 教育公平、户籍改革、反歧视立法——这些不是经济的「外部变量」，
    > 而是决定收入分配的最深层制度力量。
    > 
    > **共同富裕**不是劫富济贫，而是让每个劳动者都能在公平的起跑线上，
    > 用自己的人力资本，换取与之匹配的收入。
    """)

# 预测 vs 实验
if "wage_pred_done" in st.session_state:
    user_pred_w = st.session_state.get("wage_pred_answer", "")
    st.info(f"""
    📝 **你的预测 vs 经济学共识：**
    
    你的判断：{user_pred_w}
    
    经济学的回答：**E. 以上全部**——工资由个人能力、岗位特征、市场供需和制度设计**共同决定**，
    没有哪一个可以单独解释工资差异。这就是为什么这一章需要同时讲补偿性差异（B）、
    效率工资（D）、市场供需（C）和人力资本（A）。
    
    你的回答告诉你自己最看重哪个视角——这个视角往往决定了你是哪种类型的经济学者 😉
    """)

st.markdown("</div>", unsafe_allow_html=True)
