"""
✈️ 职场迁徙决策仿真 — 第五章 劳动力流动
NPV动态累积+制度壁垒+中国政策杠杆+情景对比+双线竞速可视化
"""

import streamlit as st
import numpy as np
import plotly.graph_objects as go
import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from shared import CHINA_MIGRANT_WAGE_2024, DATA_SOURCES, SCHOOL_NAME, AUTHOR_NAME

st.set_page_config(page_title="迁移决策仿真", page_icon="✈️", layout="wide")

# ==========================================
# 赛博暗色 UI
# ==========================================
st.markdown("""
<style>
    .stApp { background-color: #0b0f19 !important; }
    section[data-testid="stSidebar"] {
        background-color: #090d16 !important;
        border-right: 1px solid rgba(139, 92, 246, 0.1) !important;
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
        color: #a78bfa !important; font-weight: 600 !important;
    }
    .tech-card {
        background: linear-gradient(145deg, rgba(30, 41, 59, 0.6) 0%, rgba(15, 23, 42, 0.8) 100%) !important;
        border: 1px solid rgba(139, 92, 246, 0.15) !important;
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
        background: #8b5cf6; margin-right: 12px; border-radius: 3px;
        box-shadow: 0 0 8px #8b5cf6;
    }
    .decision-green {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.2) 0%, rgba(5, 150, 105, 0.1) 100%);
        border: 2px solid #10b981; border-radius: 12px; padding: 20px; margin: 10px 0;
    }
    .decision-red {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.2) 0%, rgba(220, 38, 38, 0.1) 100%);
        border: 2px solid #ef4444; border-radius: 12px; padding: 20px; margin: 10px 0;
    }
    .decision-yellow {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.2) 0%, rgba(217, 119, 6, 0.1) 100%);
        border: 2px solid #f59e0b; border-radius: 12px; padding: 20px; margin: 10px 0;
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
    <h1 style="color: #ffffff; font-weight: 900; margin-bottom: 5px;">✈️ 职场迁徙决策仿真</h1>
    <h4 style="color: #a78bfa; font-weight: 600; letter-spacing: 1px;">
        第五章 劳动力流动 — 去大城市闯荡，还是留在家乡？
    </h4>
    <p style="color: #64748b; font-size: 14px; margin-top: 4px;">
        {SCHOOL_NAME} · 课程负责人：{AUTHOR_NAME} | NPV 净现值模型
    </p>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 三种人生情景
# ==========================================
with st.expander("📖 三种人生，三种选择（点击展开）", expanded=False):
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        ### 🏙️ 小张：北漂码农
        23岁，本科计算机，拿到北京 Offer（月薪 18k）。
        老家县城找不到对口工作（月薪 5k）。
        
        **纠结：** 北京房租 4k/月，通勤 2 小时/天，
        五年能攒下首付吗？还是趁早回老家考公？
        """)
    with c2:
        st.markdown("""
        ### 🏡 小李：返乡创业者
        28岁，在深圳打工 5 年攒了 30 万。
        老家县政府出「返乡创业补贴」10 万。
        
        **纠结：** 在深圳继续熬（月薪 15k），
        还是回家开个电商工作室？
        """)
    with c3:
        st.markdown("""
        ### 🎓 小王：人才引进对象
        26岁，硕士，收到成都「蓉漂计划」Offer。
        年薪 20 万 + 安家费 15 万 + 人才公寓。
        
        **纠结：** 一线城市（30 万）vs 新一线（20 万+政策福利），
        哪个 NPV 更高？
        """)

# ==========================================
# 预测脚手架
# ==========================================
if "migrate_pred_done" not in st.session_state:
    st.markdown("<div class='tech-card' style='border-color: rgba(168, 85, 247, 0.3) !important;'>", unsafe_allow_html=True)
    st.markdown("##### 🔮 先判断：直觉 vs 模型")
    pred_m = st.radio(
        "**你认为，什么因素对「是否去大城市」的决策影响最大？**",
        ["A. 工资差（一线城市工资越高越想去）",
         "B. 生活成本（房租太贵就打退堂鼓）",
         "C. 制度壁垒（户口/社保/子女入学才是关键）",
         "D. 年龄（年轻才敢闯，老了就不动了）"],
        key="migrate_pred"
    )
    def _confirm_m_pred():
        st.session_state.migrate_pred_done = True
        st.session_state.migrate_pred_answer = st.session_state.migrate_pred
    st.button("✅ 这是我的判断，开始实验！", key="migrate_pred_btn", on_click=_confirm_m_pred)
    st.markdown("</div>", unsafe_allow_html=True)
else:
    user_pred_m = st.session_state.get("migrate_pred_answer", "")
    st.info(f"📝 你的直觉：**{user_pred_m}** — 实验结束后记得回来对比！")

# ==========================================
# 控制面板
# ==========================================
col_ctrl, col_graph = st.columns([1, 2.2])

with col_ctrl:
    st.markdown("<div class='tech-card'>", unsafe_allow_html=True)
    st.markdown("<div class='cyber-header'>🧭 你的迁徙参数</div>", unsafe_allow_html=True)
    
    st.markdown("**💰 收入差**")
    w_home = st.slider("家乡月薪 (k)", 2, 20, 5, key="w_home")
    w_city = st.slider("目标城市月薪 (k)", w_home + 1, 50, 18, key="w_city")
    st.caption(f"月薪差距：**+{w_city - w_home}k/月**，年收入差 **{(w_city-w_home)*12}k**")
    
    st.markdown("---")
    st.markdown("**🏠 生活成本（城市 vs 家乡差价）**")
    cost_rent = st.slider("额外房租/年 (k)", 0, 80, 36, 5, key="cost_rent",
                         help="城市房租减去家乡住房成本")
    cost_living = st.slider("额外生活开销/年 (k)", 0, 40, 12, 2, key="cost_living",
                            help="餐饮/交通/社交等城市溢价")
    
    st.markdown("---")
    st.markdown("**🚧 制度壁垒（中国特色）**")
    hukou_barrier = st.slider("户籍限制影响度 (%)", 0, 60, 20, 5, key="hukou",
        help="0=无壁垒 | 60=极高壁垒：影响房贷利率/子女入学/社保接续，等效于额外成本")
    hukou_cost = hukou_barrier / 100 * w_city * 2  # 等效年度额外成本
    
    st.markdown("---")
    st.markdown("**🏛️ 政策杠杆**")
    talent_subsidy = st.slider("人才引进/返乡创业补贴 (k，一次性)", 0, 200, 0, 10, key="subsidy",
        help="如：人才安家费、返乡创业启动金")
    
    st.markdown("---")
    st.markdown("**⏳ 个人因素**")
    remain_years = st.slider("剩余职业生涯 (年)", 5, 40, 25, 5, key="years",
        help="年龄越大，剩余年限越短，迁移的 NPV 越低")
    
    st.markdown("---")
    st.caption("📊 快捷情景")
    col_a, col_b = st.columns(2)
    with col_a:
        def _preset_beijing():
            st.session_state.w_home = 5; st.session_state.w_city = 18
            st.session_state.cost_rent = 48; st.session_state.cost_living = 18
            st.session_state.hukou = 30; st.session_state.subsidy = 0; st.session_state.years = 25
        st.button("🏙️ 北漂青年", key="beijing", on_click=_preset_beijing, use_container_width=True)
    with col_b:
        def _preset_return():
            st.session_state.w_home = 8; st.session_state.w_city = 15
            st.session_state.cost_rent = 36; st.session_state.cost_living = 12
            st.session_state.hukou = 10; st.session_state.subsidy = 100; st.session_state.years = 20
        st.button("🏡 返乡创业", key="return", on_click=_preset_return, use_container_width=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# NPV 计算 (双线累积竞速模型)
# ==========================================
t_vec = np.arange(1, remain_years + 1)
discount_rate = 0.05

# 1. 留在家乡的资产累积
annual_home = w_home * 12
flow_home = np.full(remain_years, annual_home)
cum_home = np.cumsum(flow_home / ((1 + discount_rate) ** t_vec))

# 2. 迁徙到大城市的资产累积
annual_benefit = (w_city - w_home) * 12 - cost_rent - cost_living - hukou_cost
annual_city_net = w_city * 12 - cost_rent - cost_living - hukou_cost
flow_city = np.full(remain_years, annual_city_net)
flow_city[0] += talent_subsidy  # 第一年拿补贴/安家费
cum_city = np.cumsum(flow_city / ((1 + discount_rate) ** t_vec))

# 3. 计算差距与盈亏平衡点 (NPV 本质上就是这两条线的差值)
cum_npv = cum_city - cum_home
final_npv = cum_npv[-1]

# 判断哪一年大城市的累计财富 > 家乡的累计财富
breakeven_arr = np.where(cum_city > cum_home)[0]
if len(breakeven_arr) > 0 and final_npv > 0:
    breakeven_year = breakeven_arr[0] + 1
else:
    breakeven_year = None

# ==========================================
# Plotly 可视化 (双线竞速图)
# ==========================================
fig = go.Figure()

# 线条 A：留在家乡轨迹 (平缓基准线)
fig.add_trace(go.Scatter(
    x=t_vec, y=cum_home,
    mode='lines',
    name='🏡 留在家乡累计财富',
    line=dict(color='#94a3b8', width=3, dash='dash'),
    hovertemplate='第%{x}年<br>家乡累计: %{y:.1f}k<extra></extra>'
))

# 线条 B：迁徙大城市轨迹
fig.add_trace(go.Scatter(
    x=t_vec, y=cum_city,
    mode='lines',
    name='🏙️ 迁徙大城市累计财富',
    line=dict(color='#a855f7', width=4),
    fill='tonexty', # 核心魔法：填充两条线之间的差值区域
    fillcolor='rgba(16, 185, 129, 0.15)' if final_npv > 0 else 'rgba(239, 68, 68, 0.15)',
    hovertemplate='第%{x}年<br>城市累计: %{y:.1f}k<extra></extra>'
))

# 标注盈亏平衡交叉点
if breakeven_year and breakeven_year <= remain_years:
    fig.add_vline(x=breakeven_year, line_dash="dot", line_color="#10b981", opacity=0.6)
    # 如果不是第一年就直接碾压，则标出明显的交叉点
    if breakeven_year > 1:
        fig.add_trace(go.Scatter(
            x=[breakeven_year], y=[cum_city[breakeven_year - 1]],
            mode='markers+text', name='🌟 回本交叉点',
            marker=dict(size=14, color='#10b981', line=dict(width=3, color='white')),
            text=["命运交叉点 (反超)"], textposition="top left",
            textfont=dict(color="#10b981", size=13, weight="bold"),
            hovertemplate=f'<b>交叉反超</b><br>第 {breakeven_year} 年城市财富超过家乡<extra></extra>'
        ))

# 尾部最终财富差距标注
fig.add_annotation(
    x=remain_years, y=(cum_city[-1] + cum_home[-1]) / 2,
    text=f"最终差距 (NPV):<br><b>{final_npv:+.0f}k</b>",
    showarrow=False,
    bgcolor="rgba(16, 185, 129, 0.9)" if final_npv > 0 else "rgba(239, 68, 68, 0.9)",
    font=dict(color="white", size=13),
    borderpad=6, bordercolor="white", borderwidth=1
)

fig.update_layout(
    title="双城记：留守 vs 迁徙的财富累积竞速",
    title_font=dict(size=16, color="#e2e8f0"),
    xaxis_title="年份 (年)", yaxis_title="累计折现财富 (k)",
    xaxis=dict(dtick=5, gridcolor="rgba(51, 65, 85, 0.3)"),
    yaxis=dict(gridcolor="rgba(51, 65, 85, 0.3)"),
    template="plotly_dark", 
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#e2e8f0", size=13),
    height=450, margin=dict(l=40, r=40, t=50, b=40),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color="#e2e8f0")),
    hovermode='x unified'
)

with col_graph:
    st.markdown("<div class='tech-card'>", unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 决策输出
# ==========================================
st.markdown("<div class='tech-card'>", unsafe_allow_html=True)
st.markdown("<div class='cyber-header'>⚖️ 迁徙决策诊断</div>", unsafe_allow_html=True)

col_d1, col_d2 = st.columns([3, 2])

with col_d1:
    if final_npv > 0 and breakeven_year and breakeven_year <= remain_years // 2:
        st.markdown("<div class='decision-green'>", unsafe_allow_html=True)
        st.success(
            f"## ✅ 强烈建议迁徙\n\n"
            f"在 **{remain_years} 年**的职业生涯中，迁徙将为你带来 **{final_npv:+.0f}k** 的净收益。\n\n"
            f"🔹 年收入净增益：**+{annual_benefit:+.0f}k/年**\n"
            f"🔹 投资回收期：仅需 **{breakeven_year} 年**（之后全是净赚）\n"
            f"🔹 回本速度：快于职业生涯一半，投资回报率极高\n\n"
            f"从小张的视角看：这个 Offer 值得接。"
        )
        st.markdown("</div>", unsafe_allow_html=True)
    elif final_npv > 0 and breakeven_year:
        st.markdown("<div class='decision-yellow'>", unsafe_allow_html=True)
        st.warning(
            f"## ⚠️ 谨慎考虑迁徙\n\n"
            f"迁徙最终能带来 **{final_npv:+.0f}k** 净收益，但回收期长达 **{breakeven_year} 年**。\n\n"
            f"🔹 年收入净增益：**+{annual_benefit:+.0f}k/年**\n"
            f"🔹 回收期：**{breakeven_year}/{remain_years} 年** — 占了职业生涯 **{breakeven_year/remain_years*100:.0f}%**\n\n"
            f"如果你已经超过 30 岁，这个决策的窗口期可能不够充裕。"
        )
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='decision-red'>", unsafe_allow_html=True)
        st.error(
            f"## ❌ 不建议迁徙\n\n"
            f"在 {remain_years} 年的职业生涯中，迁徙的 NPV 为 **{final_npv:+.0f}k**。\n\n"
            f"🔹 年收入净增益：**{annual_benefit:+.0f}k/年**\n"
            f"🔹 **{f'即使 {remain_years} 年后也无法回本' if not breakeven_year else f'回本需 {breakeven_year} 年，超出合理等待期' if breakeven_year > remain_years * 0.6 else '总体收益为负'}**\n\n"
            f"从理性经济人的角度看，留下来是更好的选择。\n"
            f"但——生活不只有 NPV。如果你去城市是为了发展机会、社交圈层、子女教育……那些非货币收益，这个模型算不出来。"
        )
        st.markdown("</div>", unsafe_allow_html=True)

with col_d2:
    st.markdown("##### 📊 关键数据")
    
    c1, c2 = st.columns(2)
    with c1:
        st.metric("年净收入增益", f"{annual_benefit:+.0f}k")
        st.metric("最终 NPV", f"{final_npv:+.0f}k")
    with c2:
        st.metric("投资回收期", f"{breakeven_year} 年" if breakeven_year else "永不回本")
        st.metric("户籍壁垒成本", f"-{hukou_cost:.0f}k/年" if hukou_barrier > 0 else "无壁垒")
    
    if talent_subsidy > 0:
        st.metric("政策补贴", f"+{talent_subsidy:.0f}k (一次性)", delta="政策杠杆")
    
    st.markdown("---")
    st.markdown("##### 🔮 你的预测 vs 模型")
    if "migrate_pred_done" in st.session_state:
        user_pred_m = st.session_state.get("migrate_pred_answer", "")
        # 分析哪个因素实际影响最大
        impacts = {
            "A": abs((w_city - w_home) * 12 * remain_years * 0.8),  # 工资差
            "B": abs(cost_rent + cost_living) * remain_years,  # 生活成本
            "C": abs(hukou_cost) * remain_years,  # 制度壁垒
            "D": abs(final_npv * (1 if remain_years < 20 else 2)),  # 年龄
        }
        actual_top = max(impacts, key=impacts.get)
        map_letter = {"A": "A. 工资差", "B": "B. 生活成本", "C": "C. 制度壁垒", "D": "D. 年龄"}
        if user_pred_m.startswith(actual_top):
            st.success(f"✅ 你的直觉很准！\n\n模型也认为 **{map_letter[actual_top]}** 在当前参数下影响最大。")
        else:
            st.info(f"🤔 有趣的偏差！\n\n你选了「{user_pred_m[0]}. ...」\n但模型中 **{map_letter[actual_top]}** 的量化影响最大。")
    else:
        st.info("🔮 回到顶部先做预测")

st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 情景对比矩阵
# ==========================================
st.markdown("<div class='tech-card'>", unsafe_allow_html=True)
st.markdown("<div class='cyber-header'>📊 三种人生 · NPV 对比</div>", unsafe_allow_html=True)

# 计算三种预设情景的 NPV
def calc_scenario_npv(w_h, w_c, rent, living, hukou_pct, subsidy, years):
    h_cost = hukou_pct / 100 * w_c * 2
    a_benefit = (w_c - w_h) * 12 - rent - living - h_cost
    flows = np.full(years, a_benefit)
    flows[0] += subsidy
    t = np.arange(1, years + 1)
    npv = np.sum(flows / ((1 + 0.05) ** t))
    be = np.where(np.cumsum(flows / ((1 + 0.05) ** t)) > 0)[0]
    return npv, be[0] + 1 if len(be) > 0 else None

npv_a, be_a = calc_scenario_npv(5, 18, 48, 18, 30, 0, 25)    # 北漂
npv_b, be_b = calc_scenario_npv(8, 15, 36, 12, 10, 100, 20)   # 返乡
npv_c, be_c = calc_scenario_npv(8, 20, 30, 10, 5, 150, 30)    # 人才引进

col_s1, col_s2, col_s3 = st.columns(3)
with col_s1:
    st.markdown("""
    ### 🏙️ 小张：北漂青年
    """)
    st.metric("NPV", f"{npv_a:+.0f}k")
    st.metric("回本年限", f"{be_a} 年" if be_a else "永不")
    st.caption("北京 18k vs 老家 5k\n高房租+高户籍壁垒")
    
with col_s2:
    st.markdown("""
    ### 🏡 小李：返乡创业
    """)
    st.metric("NPV", f"{npv_b:+.0f}k")
    st.metric("回本年限", f"{be_b} 年" if be_b else "永不")
    st.caption("城市 15k vs 家乡 8k\n补贴 100k + 低壁垒")
    
with col_s3:
    st.markdown("""
    ### 🎓 小王：人才引进
    """)
    st.metric("NPV", f"{npv_c:+.0f}k")
    st.metric("回本年限", f"{be_c} 年" if be_c else "永不")
    st.caption("成都 20k vs 老家 8k\n安家费 150k + 低壁垒")

st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 中国数据基准 + 课程思政
# ==========================================
st.markdown("<div class='tech-card'>", unsafe_allow_html=True)
st.markdown("<div class='cyber-header'>🇨🇳 中国劳动力流动的现实图景</div>", unsafe_allow_html=True)

col_real, col_ideo = st.columns([1, 1])

with col_real:
    st.markdown(f"""
    ### 📊 真实数据
    
    根据 {DATA_SOURCES['migrant']}：
    
    - **2024 年全国农民工总量**：约 2.98 亿人
    - **外出农民工月均收入**：**{CHINA_MIGRANT_WAGE_2024} 元**
    - **本地农民工月均收入**：约 4,100 元
    - **跨省流动比例**：约 42%（持续下降中）
    
    **趋势观察：**
    > 2010 年后，"孔雀东南飞"的势头在减弱。
    > 越来越多的人选择「省内流动」甚至「返乡创业」。
    > 这不仅仅是工资差的缩窄，更是**制度壁垒**与**政策引导**共同作用的结果。
    
    **你的模拟数据 vs 中国现实：**
    """)
    
    st.metric("你的城市月薪", f"{w_city}k", delta=f"vs 农民工 {CHINA_MIGRANT_WAGE_2024/1000:.1f}k")

with col_ideo:
    st.markdown("""
    ### 🏛️ 课程思政：流动的中国
    
    **1. 户籍制度的历史与改革**
    > 中国的户籍制度曾是世界上最大的"劳动力市场摩擦"之一。
    > 2014 年以来，新型城镇化战略推动户籍改革，
    > 但「教育、医疗、社保」的属地化管理仍是流动的隐性壁垒。
    > 你的模型中的**户籍限制影响度**滑块，就是在量化这种真实存在的摩擦。
    
    **2. 「孔雀东南飞」→「群凤归巢」**
    > 2000 年代：劳动力大规模向东南沿海流动。
    > 2020 年代：中西部崛起、乡村振兴、县域经济使"返乡"成为理性选择。
    > 你刚才看到的三种人生——北漂、返乡、人才引进——
    > 正是这个时代的三条真实路径。
    
    **3. 超越 NPV 的思考**
    > 模型告诉你「要不要去大城市」，但算不出：
    > - 把父母留在老家的愧疚感
    > - 在大城市认识的伴侣和朋友
    > - 创业失败从头再来的可能性
    > 
    > **经济学给你框架，但生活的答案，只有你自己知道。**
    """)

st.markdown("</div>", unsafe_allow_html=True)
