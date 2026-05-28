"""
✈️ 职场迁徙决策仿真 — 第五章 劳动力流动
NPV动态累积+制度壁垒+中国政策杠杆+情景对比
"""

import streamlit as st
import numpy as np
import plotly.graph_objects as go
import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from shared import COLOR, SHARED_CSS, CHINA_MIGRANT_WAGE_2024, DATA_SOURCES, SCHOOL_NAME, AUTHOR_NAME, render_page_banner

st.set_page_config(page_title="迁移决策仿真", page_icon="✈️", layout="wide")
st.markdown(SHARED_CSS(), unsafe_allow_html=True)

render_page_banner("✈️", "职场迁徙决策仿真", "第五章 劳动力流动 · NPV净现值模型", "purple")

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
    st.markdown("<div class='card' style='border: 2px solid #8b5cf6;'>", unsafe_allow_html=True)
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
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='card-header'>🧭 你的迁徙参数</div>", unsafe_allow_html=True)
    
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
    annual_net = (w_city - w_home) * 12 - cost_rent - cost_living
    
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
# NPV 计算
# ==========================================
t_vec = np.arange(1, remain_years + 1)

annual_benefit = (w_city - w_home) * 12 - cost_rent - cost_living - hukou_cost
net_flow = np.full(remain_years, annual_benefit)
net_flow[0] += talent_subsidy

discount_rate = 0.05
cum_npv = np.cumsum(net_flow / ((1 + discount_rate) ** t_vec))

final_npv = cum_npv[-1]
breakeven_arr = np.where(cum_npv > 0)[0]
breakeven_year = breakeven_arr[0] + 1 if len(breakeven_arr) > 0 else None

# ==========================================
# Plotly 可视化
# ==========================================
fig = go.Figure()

colors_bar = [COLOR["danger"] if v < 0 else COLOR["success"] for v in cum_npv]
fig.add_trace(go.Bar(
    x=t_vec, y=cum_npv, marker_color=colors_bar,
    name="累计 NPV",
    hovertemplate='第%{x}年<br>累计NPV: %{y:+.1f}k<br>%{customdata}<extra></extra>',
    customdata=[f'{"✅ 已回本！" if v > 0 else "⏳ 尚未回本"}' for v in cum_npv]
))

fig.add_hline(y=0, line_dash="solid", line_color="#64748b", line_width=1)

if breakeven_year:
    fig.add_vline(
        x=breakeven_year, line_dash="dash", line_color=COLOR["success"], line_width=2,
        annotation_text=f"📌 回本！第 {breakeven_year} 年",
        annotation_font=dict(size=14, color=COLOR["success"]),
        annotation_position="top"
    )
    fig.add_trace(go.Scatter(
        x=[breakeven_year], y=[cum_npv[breakeven_year - 1]],
        mode='markers', name='盈亏平衡点',
        marker=dict(size=16, color=COLOR["success"], symbol='star', line=dict(width=3, color='white')),
        hovertemplate=f'<b>🌟 盈亏平衡</b><br>第 {breakeven_year} 年<br>NPV={cum_npv[breakeven_year-1]:.1f}k<extra></extra>'
    ))

fig.add_annotation(
    x=remain_years * 0.7, y=final_npv * 0.85 if final_npv > 0 else final_npv * 0.5,
    text=f"最终 NPV: <b>{final_npv:+.0f}k</b>",
    showarrow=False,
    font=dict(size=18, color=COLOR["success"] if final_npv > 0 else COLOR["danger"]),
    bgcolor="rgba(255,255,255,0.9)", borderpad=8
)

fig.update_layout(
    xaxis_title="年份", yaxis_title="累计净现值 NPV (k)",
    xaxis=dict(dtick=5, gridcolor="rgba(0, 0, 0, 0.08)"),
    yaxis=dict(gridcolor="rgba(0, 0, 0, 0.08)"),
    template="plotly_white",
    height=430, margin=dict(l=40, r=20, t=20, b=40),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    hovermode='x unified'
)

with col_graph:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 决策输出
# ==========================================
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.markdown("<div class='card-header'>⚖️ 迁徙决策诊断</div>", unsafe_allow_html=True)

col_d1, col_d2 = st.columns([3, 2])

with col_d1:
    if final_npv > 0 and breakeven_year and breakeven_year <= remain_years // 2:
        st.markdown("""
        <div style="background:#ecfdf5; border: 2px solid #10b981; border-radius: 12px; padding: 20px; margin: 10px 0;">
        """, unsafe_allow_html=True)
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
        st.markdown("""
        <div style="background:#fffbeb; border: 2px solid #f59e0b; border-radius: 12px; padding: 20px; margin: 10px 0;">
        """, unsafe_allow_html=True)
        st.warning(
            f"## ⚠️ 谨慎考虑迁徙\n\n"
            f"迁徙最终能带来 **{final_npv:+.0f}k** 净收益，但回收期长达 **{breakeven_year} 年**。\n\n"
            f"🔹 年收入净增益：**+{annual_benefit:+.0f}k/年**\n"
            f"🔹 回收期：**{breakeven_year}/{remain_years} 年** — 占了职业生涯 **{breakeven_year/remain_years*100:.0f}%**\n\n"
            f"如果你已经超过 30 岁，这个决策的窗口期可能不够充裕。"
        )
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background:#fef2f2; border: 2px solid #ef4444; border-radius: 12px; padding: 20px; margin: 10px 0;">
        """, unsafe_allow_html=True)
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
        hukou_label = f"-{hukou_cost:.0f}k/年" if hukou_barrier > 0 else "无壁垒"
        st.metric("户籍壁垒成本", hukou_label)
        # hukou_cost is negative, so delta_color inverse is appropriate
        st.metric("", "", delta_color="off")  # placeholder
    
    if talent_subsidy > 0:
        st.metric("政策补贴", f"+{talent_subsidy:.0f}k (一次性)", delta="政策杠杆")
    
    st.markdown("---")
    st.markdown("##### 🔮 你的预测 vs 模型")
    if "migrate_pred_done" in st.session_state:
        user_pred_m = st.session_state.get("migrate_pred_answer", "")
        impacts = {
            "A": abs((w_city - w_home) * 12 * remain_years * 0.8),
            "B": abs(cost_rent + cost_living) * remain_years,
            "C": abs(hukou_cost) * remain_years,
            "D": abs(final_npv * (1 if remain_years < 20 else 2)),
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
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.markdown("<div class='card-header'>📊 三种人生 · NPV 对比</div>", unsafe_allow_html=True)

def calc_scenario_npv(w_h, w_c, rent, living, hukou_pct, subsidy, years):
    h_cost = hukou_pct / 100 * w_c * 2
    a_benefit = (w_c - w_h) * 12 - rent - living - h_cost
    flows = np.full(years, a_benefit)
    flows[0] += subsidy
    t = np.arange(1, years + 1)
    npv = np.sum(flows / ((1 + 0.05) ** t))
    be = np.where(np.cumsum(flows / ((1 + 0.05) ** t)) > 0)[0]
    return npv, be[0] + 1 if len(be) > 0 else None

npv_a, be_a = calc_scenario_npv(5, 18, 48, 18, 30, 0, 25)
npv_b, be_b = calc_scenario_npv(8, 15, 36, 12, 10, 100, 20)
npv_c, be_c = calc_scenario_npv(8, 20, 30, 10, 5, 150, 30)

col_s1, col_s2, col_s3 = st.columns(3)
with col_s1:
    st.markdown("### 🏙️ 小张：北漂青年")
    st.metric("NPV", f"{npv_a:+.0f}k")
    st.metric("回本年限", f"{be_a} 年" if be_a else "永不")
    st.caption("北京 18k vs 老家 5k\n高房租+高户籍壁垒")
    
with col_s2:
    st.markdown("### 🏡 小李：返乡创业")
    st.metric("NPV", f"{npv_b:+.0f}k")
    st.metric("回本年限", f"{be_b} 年" if be_b else "永不")
    st.caption("城市 15k vs 家乡 8k\n补贴 100k + 低壁垒")
    
with col_s3:
    st.markdown("### 🎓 小王：人才引进")
    st.metric("NPV", f"{npv_c:+.0f}k")
    st.metric("回本年限", f"{be_c} 年" if be_c else "永不")
    st.caption("成都 20k vs 老家 8k\n安家费 150k + 低壁垒")

st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 中国数据基准 + 课程思政
# ==========================================
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.markdown("<div class='card-header'>🇨🇳 中国劳动力流动的现实图景</div>", unsafe_allow_html=True)

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
