"""
📉 失业经济学 — 第八章 失业
失业类型诊断+职业搜寻模型+贝弗里奇曲线+自然失业率
"""

import streamlit as st
import numpy as np
import plotly.graph_objects as go
import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from shared import SCHOOL_NAME, AUTHOR_NAME

st.set_page_config(page_title="失业经济学", page_icon="📉", layout="wide")

# ==========================================
# 赛博暗色 UI（灰蓝色系——冷静分析）
# ==========================================
st.markdown("""
<style>
    .stApp { background-color: #0b0f19 !important; }
    section[data-testid="stSidebar"] {
        background-color: #090d16 !important;
        border-right: 1px solid rgba(99, 102, 241, 0.1) !important;
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
        color: #818cf8 !important; font-weight: 600 !important;
    }
    .tech-card {
        background: linear-gradient(145deg, rgba(30, 41, 59, 0.6) 0%, rgba(15, 23, 42, 0.8) 100%) !important;
        border: 1px solid rgba(99, 102, 241, 0.15) !important;
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
        background: #6366f1; margin-right: 12px; border-radius: 3px;
        box-shadow: 0 0 8px #6366f1;
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
    <h1 style="color: #ffffff; font-weight: 900; margin-bottom: 5px;">📉 失业经济学</h1>
    <h4 style="color: #818cf8; font-weight: 600; letter-spacing: 1px;">
        第八章 失业 — 为什么有人找不到工作，同时有岗位招不到人？
    </h4>
    <p style="color: #64748b; font-size: 14px; margin-top: 4px;">
        {SCHOOL_NAME} · 课程负责人：{AUTHOR_NAME} | 失业类型 · 职业搜寻 · 贝弗里奇曲线 · 自然失业率
    </p>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 预测脚手架
# ==========================================
if "unemp_pred_done" not in st.session_state:
    st.markdown("<div class='tech-card' style='border-color: rgba(99, 102, 241, 0.3) !important;'>", unsafe_allow_html=True)
    st.markdown("##### 🔮 先判断：失业一定是坏事吗？")
    pred_u = st.radio(
        "**如果一国的失业率是 0%，这意味着什么？**",
        ["A. 经济最健康——人人有工作，完美！",
         "B. 不可能实现——总有人在换工作、在培训、在等待合适的Offer",
         "C. 可能是坏消息——劳动力市场过度僵化，没有流动性（如计划经济）",
         "D. B 和 C 都对——有些失业是必要的、健康的"],
        key="unemp_pred"
    )
    def _confirm_u_pred():
        st.session_state.unemp_pred_done = True
        st.session_state.unemp_pred_answer = st.session_state.unemp_pred
    st.button("✅ 这是我的判断，开始实验！", key="unemp_pred_btn", on_click=_confirm_u_pred)
    st.markdown("</div>", unsafe_allow_html=True)
else:
    user_pred_u = st.session_state.get("unemp_pred_answer", "")
    st.info(f"📝 你的直觉：**{user_pred_u}** — 实验结束后对比。")

# ==========================================
# 三个实验 Tab
# ==========================================
tab1, tab2, tab3 = st.tabs(["🔍 失业类型诊断", "🎯 职业搜寻模型", "📈 贝弗里奇曲线"])

# ==========================================
# TAB 1: Unemployment Type Diagnosis
# ==========================================
with tab1:
    col_ctrl, col_graph = st.columns([1, 2.2])
    
    with col_ctrl:
        st.markdown("<div class='tech-card'>", unsafe_allow_html=True)
        st.markdown("<div class='cyber-header'>🔍 失业类型诊断仪</div>", unsafe_allow_html=True)
        
        st.markdown("**你观察到的「症状」：**")
        frictional = st.slider("摩擦性失业 (换工作/毕业生)", 0, 10, 3, 1, key="fric",
                              help="正常流动：跳槽期、毕业季——健康")
        structural = st.slider("结构性失业 (技能错配)", 0, 10, 2, 1, key="struct",
                              help="AI替代/产业转型——需要再培训")
        cyclical = st.slider("周期性失业 (经济下行)", 0, 10, 1, 1, key="cyclical",
                            help="需求不足——需要宏观政策刺激")
        seasonal = st.slider("季节性失业 (旅游/农业)", 0, 5, 1, 1, key="seasonal")
        
        total_u = frictional + structural + cyclical + seasonal
        
        st.markdown("---")
        st.caption("📊 快捷情景")
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            def _p_normal(): st.session_state.fric = 3; st.session_state.struct = 2; st.session_state.cyclical = 1; st.session_state.seasonal = 1
            st.button("🇨🇳 中国正常", key="p_cn", on_click=_p_normal, use_container_width=True)
        with col_b:
            def _p_crisis(): st.session_state.fric = 4; st.session_state.struct = 3; st.session_state.cyclical = 8; st.session_state.seasonal = 2
            st.button("💥 经济危机", key="p_crisis", on_click=_p_crisis, use_container_width=True)
        with col_c:
            def _p_tech(): st.session_state.fric = 2; st.session_state.struct = 7; st.session_state.cyclical = 1; st.session_state.seasonal = 1
            st.button("🤖 AI冲击", key="p_tech", on_click=_p_tech, use_container_width=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col_graph:
        st.markdown("<div class='tech-card'>", unsafe_allow_html=True)
        
        # 堆叠柱状图——失业构成
        categories = ['季节性', '周期性', '结构性', '摩擦性']
        values = [seasonal, cyclical, structural, frictional]
        colors_d = ['#6366f1', '#ef4444', '#f59e0b', '#3b82f6']
        
        fig1 = go.Figure()
        for i, (cat, val, col) in enumerate(zip(categories, values, colors_d)):
            fig1.add_trace(go.Bar(
                x=['失业率构成'], y=[val], name=cat,
                marker_color=col,
                text=f'{cat}\n{val}%', textposition='inside',
                hovertemplate=f'{cat}: {val}%<extra></extra>'
            ))
        
        fig1.add_hline(y=5, line_dash="dash", line_color="#10b981", line_width=2,
                       annotation_text="自然失业率 ≈5%", annotation_font=dict(color="#10b981"))
        
        fig1.update_layout(
            barmode='stack',
            xaxis=dict(showgrid=False),
            yaxis=dict(title="失业率 (%)", range=[0, max(20, total_u * 1.3)], gridcolor="rgba(51, 65, 85, 0.3)"),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e2e8f0", size=13),
            height=380, margin=dict(l=40, r=20, t=20, b=40),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color="#e2e8f0")),
            hovermode='closest'
        )
        
        st.plotly_chart(fig1, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # 诊断报告
    col_d1, col_d2 = st.columns(2)
    
    with col_d1:
        st.markdown(f"""
        ### 🏥 诊断结果
        
        | 失业类型 | 占比 | 性质 |
        |---------|------|------|
        | 摩擦性 | {frictional/total_u*100:.0f}% | 🟢 自然 |
        | 结构性 | {structural/total_u*100:.0f}% | {"🔴 需干预" if structural > 4 else "🟡 关注"}|
        | 周期性 | {cyclical/total_u*100:.0f}% | {"🔴 宏观紧急" if cyclical > 5 else "🟡 监测"}|
        | 季节性 | {seasonal/total_u*100:.0f}% | 🟢 正常 |
        
        **总失业率：{total_u}%**
        """)
    
    with col_d2:
        # 处方
        prescriptions = []
        if frictional > 5:
            prescriptions.append("📊 建立公共就业信息平台，降低搜寻成本")
        else:
            prescriptions.append("✅ 摩擦性失业在健康范围——劳动力市场流动性良好")
        
        if structural > 4:
            prescriptions.append("🎓 加大职业培训投入，对接产业转型需求")
        else:
            prescriptions.append("✅ 结构性失业可控")
        
        if cyclical > 3:
            prescriptions.append("💸 扩张性财政/货币政策刺激总需求")
        else:
            prescriptions.append("✅ 无严重周期性失业")
        
        st.markdown("### 💊 政策处方\n")
        for i, p in enumerate(prescriptions):
            st.markdown(f"{i+1}. {p}")
    
    # 自然失业率
    natural_rate = frictional + structural
    gap = cyclical
    st.markdown(f"""
    <div style="background: rgba(99,102,241,0.1); border-left: 3px solid #6366f1; padding: 16px; border-radius: 4px; margin-top: 12px;">
    <strong>🧬 自然失业率 = 摩擦性 + 结构性 = {natural_rate}%</strong><br>
    周期性失业 = {gap}%（是"过剩"失业，应通过宏观政策消除）<br>
    当前失业率 {total_u}% {'>' if total_u > natural_rate else '=' if total_u == natural_rate else '<'} 自然失业率 — {'存在负产出缺口，需要政策干预。' if total_u > natural_rate else '经济处于充分就业状态。' if total_u == natural_rate else '经济过热（劳动力短缺）。'}
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# TAB 2: Job Search Model (Reservation Wage)
# ==========================================
with tab2:
    col_ctrl2, col_graph2 = st.columns([1, 2.2])
    
    with col_ctrl2:
        st.markdown("<div class='tech-card'>", unsafe_allow_html=True)
        st.markdown("<div class='cyber-header'>🎯 职业搜寻 —— 保留工资</div>", unsafe_allow_html=True)
        
        st.markdown("**失业者的困境：等到什么时候接受 Offer？**")
        unemp_benefit = st.slider("失业保险金 (k/月)", 0, 8, 2, key="ub",
                                  help="更高的失业金 → 更高的保留工资 → 更长的失业期")
        offer_mean = st.slider("市场 Offer 均值 (k)", 5, 25, 10, key="offer_m")
        offer_std = st.slider("Offer 波动 (标准差 k)", 1, 10, 4, key="offer_std")
        search_cost = st.slider("搜索成本 (面试/投简历 k/月)", 0.0, 3.0, 0.5, 0.2, key="search_c")
        discount = st.slider("耐心程度 (年折现率 %)", 1, 20, 5, key="disc")
        
        # 最优保留工资近似
        monthly_disc = discount / 100 / 12
        # 由最优停止理论: reservation = unemp_benefit + search_cost + option_value
        # 简化: 保留工资略高于失业金
        reservation_wage = unemp_benefit + search_cost + offer_std * 0.4
        
        # 接受概率
        from scipy.stats import norm as scipy_norm
        accept_prob = 1 - scipy_norm.cdf(reservation_wage, offer_mean, offer_std)
        expected_duration = 1 / accept_prob if accept_prob > 0.01 else 100
        
        st.markdown("---")
        st.metric("你的保留工资", f"{reservation_wage:.1f}k", delta="低于此不接")
        st.metric("预期失业期", f"{expected_duration:.0f} 月")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col_graph2:
        st.markdown("<div class='tech-card'>", unsafe_allow_html=True)
        
        # Offer 分布 + 保留工资
        w_range = np.linspace(0, offer_mean + 3 * offer_std, 200)
        offer_pdf = scipy_norm.pdf(w_range, offer_mean, offer_std)
        
        fig2 = go.Figure()
        
        # Offer 分布
        fig2.add_trace(go.Scatter(
            x=w_range, y=offer_pdf, name='Offer分布',
            line=dict(color='#6366f1', width=3),
            fill='tozeroy', fillcolor='rgba(99, 102, 241, 0.15)',
            hovertemplate='工资=%{x:.1f}k<br>概率密度=%{y:.3f}<extra></extra>'
        ))
        
        # 保留工资竖线
        fig2.add_vline(
            x=reservation_wage, line_dash="dash", line_color="#f59e0b", line_width=3,
            annotation_text=f"保留工资={reservation_wage:.1f}k",
            annotation_font=dict(size=13, color="#fbbf24"),
            annotation_position="top"
        )
        
        # 接受区（绿色）
        accept_mask = w_range >= reservation_wage
        if np.any(accept_mask):
            fig2.add_trace(go.Scatter(
                x=w_range[accept_mask], y=offer_pdf[accept_mask],
                mode='lines', name=f'接受区 ({accept_prob*100:.0f}%)',
                line=dict(color='rgba(16, 185, 129, 0.5)', width=0),
                fill='tozeroy', fillcolor='rgba(16, 185, 129, 0.2)',
                hoverinfo='skip'
            ))
        
        # 拒绝区（红色）
        reject_mask = w_range < reservation_wage
        if np.any(reject_mask):
            fig2.add_trace(go.Scatter(
                x=w_range[reject_mask], y=offer_pdf[reject_mask],
                mode='lines', name=f'拒绝区 ({(1-accept_prob)*100:.0f}%)',
                line=dict(color='rgba(239, 68, 68, 0.3)', width=0),
                fill='tozeroy', fillcolor='rgba(239, 68, 68, 0.15)',
                hoverinfo='skip'
            ))
        
        fig2.add_annotation(
            x=reservation_wage + offer_std * 0.5, y=offer_pdf.max() * 0.7,
            text=f"接受概率<br><b>{accept_prob*100:.0f}%</b><br>预期等待 {expected_duration:.0f} 月",
            showarrow=False,
            font=dict(size=13, color="#10b981"),
            bgcolor="rgba(0,0,0,0.7)", borderpad=8
        )
        
        fig2.update_layout(
            xaxis_title="月工资 Offer (k)", yaxis_title="概率密度",
            xaxis=dict(gridcolor="rgba(51, 65, 85, 0.3)"),
            yaxis=dict(gridcolor="rgba(51, 65, 85, 0.3)"),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e2e8f0", size=13),
            height=420, margin=dict(l=40, r=20, t=30, b=40),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color="#e2e8f0")),
            hovermode='closest'
        )
        
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # 搜寻模型洞察
    st.markdown(f"""
    <div class="tech-card">
    <div class="cyber-header">🔬 搜寻模型核心机制</div>
    
    | 参数变化 | 保留工资 | 失业期 | 经济学含义 |
    |---------|---------|--------|-----------|
    | 失业金 ↑ (当前 {unemp_benefit}k) | ↑ | ↑ | 更好的安全网 → 更挑剔 → 失业更长 |
    | 市场工资 ↑ (均值 {offer_mean}k) | ↑ | ↓ | 好 Offer 更多 → 更快找到 |
    | Offer 波动 ↑ (σ={offer_std}) | ↑ | ↓ | 更多"惊喜 Offer" → 值得多等 |
    | 搜索成本 ↑ ({search_cost}k) | ↑ | ↑ | 成本高 → 要求更高 → 但非直觉 |
    
    <strong>政策含义：</strong>
    提高失业保险金确实会延长失业期（道德风险），但也提高了匹配质量——工人不会因为急着付房租而接受不合适的低薪工作。
    这就是<strong>效率与公平的永恒张力</strong>：你要保障底线，还是优化速度？
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# TAB 3: Beveridge Curve
# ==========================================
with tab3:
    col_ctrl3, col_graph3 = st.columns([1, 2.2])
    
    with col_ctrl3:
        st.markdown("<div class='tech-card'>", unsafe_allow_html=True)
        st.markdown("<div class='cyber-header'>📈 贝弗里奇曲线</div>", unsafe_allow_html=True)
        
        st.markdown("**空岗率 = f(失业率, 匹配效率)**")
        matching_efficiency = st.slider("匹配效率 μ", 0.1, 1.0, 0.5, 0.05, key="match_eff",
                                        help="高=市场高效匹配 | 低=摩擦/结构性障碍大")
        
        st.markdown("**经济状态**")
        demand_level = st.slider("总需求水平", -5, 5, 0, 1, key="ad",
                                help="<0=衰退 | 0=正常 | >0=过热")
        
        # 贝弗里奇曲线: v = μ² / u (简化Cobb-Douglas匹配函数)
        u_range = np.linspace(2, 15, 50)
        v_curve = matching_efficiency ** 2 / (u_range / 100)
        
        # 当前点
        u_current = max(2, 5 - demand_level * 0.8 + (1 - matching_efficiency) * 5)
        v_current = matching_efficiency ** 2 / (u_current / 100)
        
        st.markdown("---")
        st.metric("当前失业率", f"{u_current:.1f}%")
        st.metric("当前空岗率", f"{v_current:.1f}%")
        
        st.markdown("---")
        st.caption("📊 快捷预设")
        col_h1, col_h2 = st.columns(2)
        with col_h1:
            def _p_efficient(): st.session_state.match_eff = 0.8; st.session_state.ad = 0
            st.button("✅ 高效市场", key="eff", on_click=_p_efficient, use_container_width=True)
        with col_h2:
            def _p_mismatch(): st.session_state.match_eff = 0.2; st.session_state.ad = -3
            st.button("💥 滞涨（高失业+高空岗）", key="mis", on_click=_p_mismatch, use_container_width=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col_graph3:
        st.markdown("<div class='tech-card'>", unsafe_allow_html=True)
        
        fig3 = go.Figure()
        
        # 贝弗里奇曲线
        fig3.add_trace(go.Scatter(
            x=u_range, y=v_curve, name='贝弗里奇曲线',
            line=dict(color='#6366f1', width=4),
            hovertemplate=(
                '失业率=%{x:.1f}%<br>'
                '空岗率=%{y:.1f}%<br>'
                '匹配效率 μ={customdata:.2f}'
                '<extra></extra>'
            ),
            customdata=[matching_efficiency] * 50
        ))
        
        # 当前点
        fig3.add_trace(go.Scatter(
            x=[u_current], y=[v_current],
            mode='markers', name=f'当前经济点',
            marker=dict(size=20, color='#f59e0b', symbol='star', line=dict(width=3, color='white')),
            hovertemplate=(
                f'<b>当前</b><br>'
                f'失业率={u_current:.1f}%<br>'
                f'空岗率={v_current:.1f}%<br>'
                f'总需求={"扩张" if demand_level > 0 else "收缩" if demand_level < 0 else "中性"}'
                '<extra></extra>'
            )
        ))
        
        # 自然失业率标注
        u_natural = matching_efficiency * 5 + (1 - matching_efficiency) * 8
        fig3.add_vline(
            x=u_natural, line_dash="dash", line_color="#10b981", line_width=1.5,
            annotation_text=f"自然率 ≈{u_natural:.1f}%",
            annotation_font=dict(size=11, color="#10b981"),
            annotation_position="bottom"
        )
        
        fig3.update_layout(
            xaxis_title="失业率 (%)", yaxis_title="空岗率 (%)",
            xaxis=dict(range=[0, 16], gridcolor="rgba(51, 65, 85, 0.3)"),
            yaxis=dict(range=[0, max(v_curve) * 1.3], gridcolor="rgba(51, 65, 85, 0.3)"),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e2e8f0", size=13),
            height=420, margin=dict(l=40, r=20, t=20, b=40),
            legend=dict(font=dict(color="#e2e8f0")),
            hovermode='closest'
        )
        
        st.plotly_chart(fig3, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # 贝弗里奇解读
    d_from_natural = u_current - u_natural
    curvature = "陡峭" if matching_efficiency < 0.3 else "平缓" if matching_efficiency > 0.7 else "适中"
    
    st.markdown(f"""
    <div class="tech-card">
    <div class="cyber-header">📊 贝弗里奇曲线诊断</div>
    
    | 指标 | 当前值 | 解读 |
    |------|--------|------|
    | 曲线形态 | {curvature} | {"匹配效率低→同等空岗率对应更高失业（结构性失业严重）" if matching_efficiency < 0.3 else "匹配效率高→市场高效运转" if matching_efficiency > 0.7 else ""} |
    | 失业率偏差 | {d_from_natural:+.1f}% vs 自然率 | {'周期性失业（需求不足）' if d_from_natural > 0.5 else '正常范围' if abs(d_from_natural) <= 0.5 else '经济过热'} |
    | 匹配效率 μ | {matching_efficiency:.2f} | {'需改善信息匹配/降低制度摩擦' if matching_efficiency < 0.4 else '良好'} |
    
    <strong>贝弗里奇曲线的核心洞见：</strong><br>
    1. <strong>沿曲线移动</strong> = 总需求变化（衰退→失业↑空岗↓，扩张→反之）<br>
    2. <strong>曲线外移</strong> = 匹配效率恶化（同等空岗率对应更高失业）——结构性失业加重<br>
    3. <strong>曲线内移</strong> = 匹配效率改善——政策干预有效<br><br>
    中国经济面临的挑战：AI替代 + 产业升级 → 贝弗里奇曲线可能正在<strong>外移</strong> → 职业培训比货币宽松更重要。
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 课程思政
# ==========================================
st.markdown("<div class='tech-card'>", unsafe_allow_html=True)
st.markdown("<div class='cyber-header'>🏛️ 深度思考：失业的社会成本</div>", unsafe_allow_html=True)

col_ideo1, col_ideo2 = st.columns(2)

with col_ideo1:
    st.markdown("""
    ### 1. 失业不只是经济问题
    > 失业率每上升 1%，离婚率、犯罪率、自杀率随之变化。
    > 
    > 工作不只是收入来源——它是社会身份的锚点、日常生活的结构、
    > 自我价值感的来源。失业摧毁的不仅是钱包，还有人的尊严。
    > 
    > 这就是为什么「充分就业」是所有现代政府的首要经济目标。
    
    ### 2. 中国的就业优先战略
    > 中国是世界上为数不多将「就业优先」写进宏观政策框架的国家。
    > 「六稳」之首是稳就业，「六保」之首是保居民就业。
    > 
    > 背后的经济学逻辑：中国有 8 亿劳动力，失业不仅意味着 GDP 损失，
    > 更意味着社会稳定的最大威胁。
    """)

with col_ideo2:
    st.markdown("""
    ### 3. 零失业率不是目标
    > 计划经济追求"人人有工作"→ 结果是人浮于事、隐性失业。
    > 
    > 市场经济承认摩擦性失业和结构性失业是**必要的、健康的**——
    > 它们反映了劳动者在寻找更好的匹配，经济在升级换代。
    > 
    > 自然失业率 = 劳动力市场灵活性与保障的平衡点。
    
    ### 4. AI 时代的失业挑战
    > 当 AI 能写代码、翻译、设计时，结构性失业可能系统性上升。
    > 
    > 答案不是阻止技术进步，而是：
    > - 改革教育体系（从记忆型 → 创造型）
    > - 建立终身学习制度
    > - 完善社会保障网
    > 
    > **最好的失业政策，是一个能让人不断升级的人力资本体系。**
    """)

# 预测 vs 实验
if "unemp_pred_done" in st.session_state:
    st.info(f"""
    📝 **你的预测 vs 经济学共识：**
    
    经济学共识：**D** — 零失业率不仅是不可实现的（存在自然失业率），而且是不健康的。
    摩擦性失业反映劳动力市场的流动性，结构性失业推动产业升级。
    真正需要政策干预的是周期性失业。
    
    计划经济追求「消灭失业」，结果制造了全球最大的隐性失业大军。
    市场经济追求「接近自然失业率」，这才是真正的充分就业。
    """)

st.markdown("</div>", unsafe_allow_html=True)
