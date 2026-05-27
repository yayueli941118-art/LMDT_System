"""
📉 失业经济学 — 第八章 失业 (学生体验优化版)
因果诊断+求职者日记+政策按钮逆转体验
"""

import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.stats import norm as scipy_norm
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
    .btn-policy { margin-top: 10px; margin-bottom: 10px; }
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
        {SCHOOL_NAME} · 课程负责人：{AUTHOR_NAME} | 失业类型诊断 · 职业搜寻日记 · 政策干预沙盘
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

# ==========================================
# 三个实验 Tab
# ==========================================
tab1, tab2, tab3 = st.tabs(["🔍 经济门诊 (失业类型诊断)", "🎯 求职日记 (职业搜寻模型)", "📈 市长沙盘 (贝弗里奇曲线)"])

# ==========================================
# TAB 1: 失业类型诊断 (改写为“现象归因”逻辑)
# ==========================================
with tab1:
    col_ctrl, col_graph = st.columns([1.2, 2])
    
    with col_ctrl:
        st.markdown("<div class='tech-card'>", unsafe_allow_html=True)
        st.markdown("<div class='cyber-header'>🌡️ 调节宏观经济现象</div>", unsafe_allow_html=True)
        
        st.markdown("**作为观察者，你看到了什么？**")
        # 优化1：调节经济热度代替直接调周期性失业
        econ_temp = st.slider("📉 经济景气度 (总需求)", -5.0, 5.0, 0.0, 0.5, key="t1_econ",
                              help="-5=百业萧条，工厂倒闭 | +5=经济过热，疯狂招人")
        # 优化2：调节AI冲击代替直接调结构性失业
        ai_impact = st.slider("🤖 技术迭代与AI冲击程度", 0.0, 10.0, 3.0, 0.5, key="t1_ai",
                              help="0=传统产业为主 | 10=AI全面替代初级白领")
        # 优化3：调节流动性代替直接调摩擦性失业
        mobility = st.slider("🏃‍♂️ 劳动力流动自由度", 0.0, 10.0, 5.0, 0.5, key="t1_mob",
                             help="0=户口锁死无法跳槽 | 10=说走就走，频繁换城市/工作")
        
        # 核心映射算法：现象 -> 结果
        cyclical = max(0.0, -econ_temp * 1.5)  # 经济越差，周期性越高
        structural = ai_impact * 0.8 + 0.5     # AI冲击直连结构性
        frictional = mobility * 0.3 + 1.0      # 越爱跳槽，摩擦性越高
        seasonal = 1.0                         # 季节性设为常数基底
        
        total_u = frictional + structural + cyclical + seasonal
        
        st.markdown("---")
        st.caption("📊 快捷模拟剧本")
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            def _p_normal(): st.session_state.t1_econ=1; st.session_state.t1_ai=2; st.session_state.t1_mob=4
            st.button("🇨🇳 平稳期", on_click=_p_normal, use_container_width=True)
        with col_b:
            def _p_crisis(): st.session_state.t1_econ=-4.5; st.session_state.t1_ai=3; st.session_state.t1_mob=2
            st.button("💥 金融危机", on_click=_p_crisis, use_container_width=True)
        with col_c:
            def _p_tech(): st.session_state.t1_econ=2; st.session_state.t1_ai=9; st.session_state.t1_mob=7
            st.button("🤖 AI大爆发", on_click=_p_tech, use_container_width=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col_graph:
        st.markdown("<div class='tech-card'>", unsafe_allow_html=True)
        
        # 堆叠柱状图——失业构成
        categories = ['季节性', '周期性(需求不足)', '结构性(技能错配)', '摩擦性(正常换工)']
        values = [seasonal, cyclical, structural, frictional]
        colors_d = ['#6366f1', '#ef4444', '#f59e0b', '#3b82f6']
        
        fig1 = go.Figure()
        for i, (cat, val, col) in enumerate(zip(categories, values, colors_d)):
            fig1.add_trace(go.Bar(
                x=['当前宏观失业率构成'], y=[val], name=cat,
                marker_color=col,
                text=f'{val:.1f}%', textposition='inside',
                hovertemplate=f'{cat}: {val:.1f}%<extra></extra>'
            ))
        
        fig1.add_hline(y=5, line_dash="dash", line_color="#10b981", line_width=2,
                       annotation_text="警戒线 ≈5%", annotation_font=dict(color="#10b981"))
        
        fig1.update_layout(
            title=f"总失业率: {total_u:.1f}%", title_font=dict(size=20, color="#e2e8f0"),
            barmode='stack', xaxis=dict(showgrid=False),
            yaxis=dict(title="失业率 (%)", range=[0, 25], gridcolor="rgba(51, 65, 85, 0.3)"),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e2e8f0", size=13),
            height=350, margin=dict(l=40, r=20, t=50, b=40),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig1, use_container_width=True)
        
        # 诊断报告 (视觉升级版)
        st.markdown("### 🏥 系统自动诊断结论")
        if cyclical > 4:
            st.error(f"🚨 **红色预警：严重的需求不足！**\n经济景气度极寒导致大规模裁员（周期性失业 {cyclical:.1f}%）。当务之急是**释放货币流动性或开展大基建**，刺激总需求。")
        elif structural > 5:
            st.warning(f"⚠️ **黄色预警：危险的结构性撕裂！**\nAI技术冲击导致旧岗位消失，新岗位招不到人（结构性失业 {structural:.1f}%）。发钱没用，必须立刻开展**劳动者技能重塑工程**。")
        elif frictional > 3.5:
            st.info(f"ℹ️ **蓝色提示：流动性过热**\n大家都在频繁跳槽找更好的机会（摩擦性失业 {frictional:.1f}%）。这是自由市场的正常代价，建议建立**公共就业信息联网**以缩短匹配时间。")
        else:
            st.success(f"✅ **绿色健康：接近自然失业率**\n当前总失业率为 {total_u:.1f}%，主要由摩擦性和季节性构成，经济处于极其健康的「充分就业」状态。")
        st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# TAB 2: 求职日记 (增加情感代入和福利陷阱预警)
# ==========================================
with tab2:
    col_ctrl2, col_graph2 = st.columns([1, 2.2])
    
    with col_ctrl2:
        st.markdown("<div class='tech-card'>", unsafe_allow_html=True)
        st.markdown("<div class='cyber-header'>🎯 设定求职者心态</div>", unsafe_allow_html=True)
        
        unemp_benefit = st.slider("💸 失业救济金/低保 (k/月)", 0.0, 10.0, 2.0, 0.5, key="ub",
                                  help="失业金越高，求职者越不着急工作")
        offer_mean = st.slider("🏢 市场平均开出的薪资 (k/月)", 4.0, 25.0, 10.0, 0.5, key="offer_m")
        offer_std = st.slider("🎲 薪资波动差 (运气成分)", 1.0, 10.0, 4.0, 0.5, key="offer_std",
                              help="波动越大，求职者越想等等看有没有'大包'")
        
        # 简化计算：保留工资模型
        search_cost = 0.5
        reservation_wage = unemp_benefit + search_cost + offer_std * 0.4
        accept_prob = 1 - scipy_norm.cdf(reservation_wage, offer_mean, offer_std)
        expected_duration = 1 / accept_prob if accept_prob > 0.01 else 999
        
        st.markdown("---")
        st.markdown("##### 💼 求职者日记摘要")
        st.metric("我的底线工资 (保留工资)", f"{reservation_wage:.1f} k/月", delta="低于这个数我绝对不干")
        st.metric("预计要投简历/面试的时间", f"{expected_duration:.1f} 个月", delta_color="inverse")
        
        # 【核心体验升级】情感预警反馈
        if reservation_wage > offer_mean and unemp_benefit > offer_mean * 0.5:
            st.error("🚨 **陷入失业陷阱！**\n底线比市场均价还高！由于有高额失业金兜底，求职者选择『躺平』，这在经济学上叫做严重的**道德风险**。")
        elif expected_duration > 12:
            st.warning("⚠️ **长期失业警告！**\n预期等待超过 1 年。虽然你在死磕高薪，但请注意：脱离职场太久会导致**人力资本严重贬值**！")
        else:
            st.success("✅ **积极求职状态**\n底线设定合理，心态平和，预计能在正常周期内匹配到工作。")
            
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col_graph2:
        st.markdown("<div class='tech-card'>", unsafe_allow_html=True)
        
        w_range = np.linspace(0, offer_mean + 3 * offer_std, 200)
        offer_pdf = scipy_norm.pdf(w_range, offer_mean, offer_std)
        
        fig2 = go.Figure()
        
        # 市场 Offer 分布
        fig2.add_trace(go.Scatter(
            x=w_range, y=offer_pdf, name='市场Offer分布图',
            line=dict(color='#6366f1', width=3),
            fill='tozeroy', fillcolor='rgba(99, 102, 241, 0.1)',
            hovertemplate='工资=%{x:.1f}k<br>收到该Offer概率=%{y:.3f}<extra></extra>'
        ))
        
        # 保留工资红线
        fig2.add_vline(x=reservation_wage, line_dash="dash", line_color="#f59e0b", line_width=4)
        
        # 绿色接受区
        accept_mask = w_range >= reservation_wage
        if np.any(accept_mask):
            fig2.add_trace(go.Scatter(
                x=w_range[accept_mask], y=offer_pdf[accept_mask], mode='lines', 
                name=f'接Offer概率: {accept_prob*100:.1f}%',
                line=dict(color='rgba(16, 185, 129, 0)'), fill='tozeroy', fillcolor='rgba(16, 185, 129, 0.4)'
            ))
            
        # 红色拒绝区
        reject_mask = w_range < reservation_wage
        if np.any(reject_mask):
            fig2.add_trace(go.Scatter(
                x=w_range[reject_mask], y=offer_pdf[reject_mask], mode='lines', 
                name=f'拒绝Offer概率: {(1-accept_prob)*100:.1f}%',
                line=dict(color='rgba(239, 68, 68, 0)'), fill='tozeroy', fillcolor='rgba(239, 68, 68, 0.4)'
            ))
            
        fig2.add_annotation(
            x=reservation_wage, y=offer_pdf.max(),
            text=f"👈 看不上的 Offer | 愿意接的 Offer 👉<br>底线线：{reservation_wage:.1f}k",
            showarrow=True, arrowhead=2, ax=0, ay=-40, font=dict(color="#f59e0b", size=14)
        )
        
        fig2.update_layout(
            title="求职者内心博弈图：接还是拒？", title_font=dict(color="#e2e8f0"),
            xaxis_title="市场开出的月薪 (k)", yaxis_title="概率",
            xaxis=dict(gridcolor="rgba(51, 65, 85, 0.3)"), yaxis=dict(showticklabels=False),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e2e8f0"), height=450, margin=dict(l=20, r=20, t=50, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.05)
        )
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# TAB 3: 市长沙盘 (增加干预按钮，制造逆转时刻)
# ==========================================
with tab3:
    # 初始化 Session State
    if "match_eff" not in st.session_state: st.session_state.match_eff = 0.5
    if "ad" not in st.session_state: st.session_state.ad = 0

    col_ctrl3, col_graph3 = st.columns([1, 2.2])
    
    with col_ctrl3:
        st.markdown("<div class='tech-card'>", unsafe_allow_html=True)
        st.markdown("<div class='cyber-header'>🏛️ 宏观经济驾驶舱</div>", unsafe_allow_html=True)
        
        st.markdown("**1. 设定初始环境参数**")
        matching_efficiency = st.slider("🧩 市场匹配效率 μ", 0.1, 1.0, st.session_state.match_eff, 0.05, key="match_eff",
                                        help="受AI冲击、信息不对称影响。越低，结构性失业越重。")
        demand_level = st.slider("🔥 总需求水平 (经济热度)", -5, 5, st.session_state.ad, 1, key="ad",
                                 help="受消费、投资影响。越低，周期性失业越重。")
        
        # 贝弗里奇逻辑计算
        u_current = max(2, 5 - demand_level * 0.8 + (1 - matching_efficiency) * 5)
        v_current = matching_efficiency ** 2 / (u_current / 100)
        u_natural = matching_efficiency * 5 + (1 - matching_efficiency) * 8
        
        st.markdown("---")
        st.markdown("**2. 市长政策工具箱 (点击执行干预)**")
        
        # 按钮 1：宏观需求刺激
        def apply_stimulus():
            st.session_state.ad = 4
        st.button("🏗️ 砸四万亿大基建 (刺激需求)", on_click=apply_stimulus, use_container_width=True, 
                  help="沿曲线移动：大幅提高总需求，但可能导致严重招工难。")
        
        # 按钮 2：供给侧改革
        def apply_reskilling():
            st.session_state.match_eff = min(1.0, st.session_state.match_eff + 0.4)
        st.button("🎓 实施全民AI技能重塑 (供给侧改革)", on_click=apply_reskilling, use_container_width=True,
                  help="曲线内移：提升劳动者技能，彻底解决结构性错配。")
                  
        st.markdown("---")
        col_m1, col_m2 = st.columns(2)
        col_m1.metric("即时失业率 U", f"{u_current:.1f}%", delta=f"{u_current - u_natural:+.1f}% vs 自然率", delta_color="inverse")
        col_m2.metric("岗位空缺率 V", f"{v_current:.1f}%")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col_graph3:
        st.markdown("<div class='tech-card'>", unsafe_allow_html=True)
        
        fig3 = go.Figure()
        u_range = np.linspace(2, 15, 50)
        v_curve = matching_efficiency ** 2 / (u_range / 100)
        
        # 绘制基准幽灵线（假设 μ=0.5）作为固定参照物
        v_ghost = 0.5 ** 2 / (u_range / 100)
        fig3.add_trace(go.Scatter(
            x=u_range, y=v_ghost, mode='lines', name='历史基准曲线 (μ=0.5)',
            line=dict(color='#475569', width=2, dash='dot'), hoverinfo='skip'
        ))
        
        # 当前贝弗里奇曲线
        fig3.add_trace(go.Scatter(
            x=u_range, y=v_curve, name=f'当前贝弗里奇曲线 (μ={matching_efficiency:.2f})',
            line=dict(color='#6366f1' if matching_efficiency>=0.5 else '#ef4444', width=4),
            fill='tonexty' if matching_efficiency != 0.5 else 'none',
            fillcolor='rgba(239, 68, 68, 0.1)' if matching_efficiency < 0.5 else 'rgba(16, 185, 129, 0.1)'
        ))
        
        # 当前状态星号点
        fig3.add_trace(go.Scatter(
            x=[u_current], y=[v_current], mode='markers+text', name='当前经济落点',
            marker=dict(size=22, color='#f59e0b', symbol='star', line=dict(width=3, color='white')),
            text=["📍 你在这里"], textposition="top right", textfont=dict(color="#f59e0b", size=14)
        ))
        
        # 动态反馈文案
        if matching_efficiency < 0.4:
            diag_text = "🚨 滞胀危机：曲线恶性外移！\n(高失业+招工难并存)"
            diag_color = "#ef4444"
        elif demand_level > 3:
            diag_text = "🔥 经济过热：沿曲线向左上方滑动\n(失业率低，但企业极度缺人)"
            diag_color = "#f59e0b"
        elif matching_efficiency >= 0.8:
            diag_text = "✅ 改革奏效：曲线良性内移！\n(匹配效率极高，新质生产力迸发)"
            diag_color = "#10b981"
        else:
            diag_text = "⚪ 市场平稳运行中"
            diag_color = "#cbd5e1"
            
        fig3.add_annotation(
            x=12, y=10, text=diag_text, showarrow=False,
            font=dict(color="white", size=15), bgcolor=diag_color, borderpad=10, borderwidth=2, bordercolor="white"
        )
        
        fig3.update_layout(
            title="贝弗里奇曲线动态沙盘 (U-V Curve)", title_font=dict(color="#e2e8f0"),
            xaxis_title="失业率 U (%)", yaxis_title="岗位空缺率 V (%)",
            xaxis=dict(range=[0, 16], gridcolor="rgba(51, 65, 85, 0.3)"),
            yaxis=dict(range=[0, 15], gridcolor="rgba(51, 65, 85, 0.3)"),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e2e8f0"), height=450, margin=dict(l=20, r=20, t=50, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.05)
        )
        
        st.plotly_chart(fig3, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
