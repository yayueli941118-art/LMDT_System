"""
🚫 劳动力市场歧视经济学实验 — 第六章 劳动力市场歧视
贝克尔偏好歧视模型 + 统计性歧视螺旋 + 拥挤假说 + 中国政策实验
"""

import streamlit as st
import numpy as np
import plotly.graph_objects as go
import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from shared import COLOR, SHARED_CSS, SCHOOL_NAME, AUTHOR_NAME, render_page_banner

st.set_page_config(page_title="歧视经济学实验", page_icon="🚫", layout="wide")
st.markdown(SHARED_CSS(), unsafe_allow_html=True)

render_page_banner("🚫", "劳动力市场歧视经济学实验", "第六章 · Becker模型 + 统计性歧视", "red")

# ==========================================
# 预测脚手架
# ==========================================
if "disc_pred_done" not in st.session_state:
    st.markdown("<div class='card' style='border: 2px solid #ef4444;'>", unsafe_allow_html=True)
    st.markdown("##### 🔮 先判断：歧视能在市场中长期存在吗？")
    pred_d = st.radio(
        "**根据新古典经济学，如果雇主因为个人偏见歧视某一群体——**",
        ["A. 市场会自动消除歧视——不歧视的雇主人力成本更低，最终占领市场",
         "B. 歧视会长期存在——因为有信息不对称和制度惯性",
         "C. 歧视不仅存在，还会自我强化（统计性歧视→被歧视者减少人力资本投资→真的变差→歧视被'验证'）",
         "D. 说不清，要看具体制度环境"],
        key="disc_pred"
    )
    def _confirm_d_pred():
        st.session_state.disc_pred_done = True
        st.session_state.disc_pred_answer = st.session_state.disc_pred
    st.button("✅ 这是我的判断，开始实验！", key="disc_pred_btn", on_click=_confirm_d_pred)
    st.markdown("</div>", unsafe_allow_html=True)
else:
    user_pred_d = st.session_state.get("disc_pred_answer", "")
    st.info(f"📝 你的直觉：**{user_pred_d}** — 实验结束后记得对比。")

# ==========================================
# 情境故事
# ==========================================
with st.expander("📖 两个求职者的故事（点击展开）", expanded=False):
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        ### 👩‍💼 求职者 A（对照组）
        - 25 岁，本科，人力专业
        - 期望薪资：8k/月
        - 户籍：本地城市
        - 面试反馈：正常通过，无阻力
        """)
    with c2:
        st.markdown("""
        ### 👩‍🔧 求职者 B（歧视对象）
        - 25 岁，本科，人力专业（**同校同专业**）
        - 期望薪资：8k/月
        - 户籍：农村 / 女性 / 35岁+ / 非985
        - 面试反馈："不好意思，我们这个岗位有特殊要求"
        """)
    st.markdown("""
    > **两个人的人力资本完全相同。但市场上的"定价"却不同。**
    > 这不是经济学模型失灵——恰恰是经济学试图解释的核心现象：**歧视如何扭曲了劳动力市场的价格信号。**
    """)

# ==========================================
# Tab 切换：三个实验
# ==========================================
tab1, tab2, tab3 = st.tabs(["🎯 实验一：贝克尔偏好歧视", "📊 实验二：统计性歧视螺旋", "🏛️ 实验三：中国政策实验"])

# ==========================================
# TAB 1: Becker Taste-for-Discrimination Model
# ==========================================
with tab1:
    col_ctrl, col_graph = st.columns([1, 2.2])
    
    with col_ctrl:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='card-header'>🎚️ 歧视参数</div>", unsafe_allow_html=True)
        
        d = st.slider("贝克尔歧视系数 d", 0.0, 1.0, 0.3, 0.05, key="d_becker",
                      help="d=0 无歧视 | d=1 极强歧视。雇主愿意多付 d×w 来避免雇佣被歧视群体")
        mpl = st.slider("边际产品价值 MPL (k/月)", 5, 20, 10, key="mpl",
                        help="两个群体的真实生产率完全相同")
        
        st.markdown("---")
        st.caption("📊 快捷情景")
        col_a, col_b = st.columns(2)
        with col_a:
            def _preset_weak(): st.session_state.d_becker = 0.1
            st.button("🤏 弱歧视", key="p_weak", on_click=_preset_weak, use_container_width=True)
        with col_b:
            def _preset_strong(): st.session_state.d_becker = 0.8
            st.button("💀 强歧视", key="p_strong", on_click=_preset_strong, use_container_width=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    w_pref = mpl
    w_disc = mpl / (1 + d)
    wage_gap = w_pref - w_disc
    gap_pct = (wage_gap / w_pref) * 100
    
    d_range = np.linspace(0, 1, 50)
    w_disc_range = mpl / (1 + d_range)
    
    fig1 = go.Figure()
    
    fig1.add_trace(go.Scatter(
        x=d_range, y=[mpl] * 50, name="偏好群体工资",
        line=dict(color=COLOR["success"], width=3),
        hovertemplate='偏好群体: MPL=%{y:.1f}k<extra></extra>'
    ))
    
    fig1.add_trace(go.Scatter(
        x=d_range, y=w_disc_range, name="被歧视群体工资",
        line=dict(color=COLOR["danger"], width=4),
        fill='tonexty', fillcolor='rgba(239, 68, 68, 0.1)',
        hovertemplate='歧视系数 d=%{x:.2f}<br>被歧视群体: %{y:.1f}k<br>工资差距: %{customdata:.1f}k<extra></extra>',
        customdata=mpl - w_disc_range
    ))
    
    fig1.add_trace(go.Scatter(
        x=[d], y=[w_disc], mode='markers', name=f"当前歧视水平 d={d}",
        marker=dict(size=20, color=COLOR["danger"], symbol='x', line=dict(width=3, color='white')),
        hovertemplate=f'<b>当前:</b> d={d}<br>被歧视工资={w_disc:.1f}k<br>差距={wage_gap:.1f}k ({gap_pct:.0f}%)<extra></extra>'
    ))
    
    fig1.add_trace(go.Scatter(
        x=np.concatenate([d_range, d_range[::-1]]),
        y=np.concatenate([[mpl] * 50, w_disc_range[::-1]]),
        fill='toself', fillcolor='rgba(239, 68, 68, 0.08)',
        line=dict(width=0), hoverinfo='skip', name='福利损失'
    ))
    
    fig1.add_annotation(
        x=d_range[25], y=(mpl + w_disc_range[25]) / 2,
        text="⚠️ 同工不同酬<br>福利损失区",
        showarrow=False, font=dict(size=13, color=COLOR["danger"]),
        bgcolor="rgba(255,255,255,0.9)", borderpad=6
    )
    
    fig1.update_layout(
        xaxis_title="歧视系数 d", yaxis_title="月工资 (k)",
        xaxis=dict(range=[0, 1], gridcolor="rgba(0, 0, 0, 0.08)"),
        yaxis=dict(range=[0, mpl * 1.3], gridcolor="rgba(0, 0, 0, 0.08)"),
        template="plotly_white",
        height=420, margin=dict(l=40, r=20, t=30, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode='closest'
    )
    
    with col_graph:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.plotly_chart(fig1, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("偏好群体月薪", f"{w_pref:.1f}k", delta="MPL")
    with c2:
        st.metric("被歧视群体月薪", f"{w_disc:.1f}k", delta=f"-{gap_pct:.0f}%", delta_color="inverse")
    with c3:
        st.metric("歧视年度成本", f"{(wage_gap * 12):.1f}k", delta="被歧视者年损失")
    
    st.markdown("---")
    st.markdown(f"""
    <div style="background: #fef2f2; border-left: 3px solid {COLOR['danger']}; padding: 16px; border-radius: 4px;">
    <strong>🔬 贝克尔模型的核心洞见：</strong><br>
    具有歧视偏好的雇主，愿意为「不雇佣特定群体」支付额外的心理成本（d × MPL）。<br>
    在竞争性市场中，<strong>非歧视雇主的人力成本更低</strong>，理论上会逐步占领市场，挤出歧视者。<br>
    ——但这只在完美竞争的假设下成立。现实中，信息不对称、制度刚性、社会规范共同维持着歧视。
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# TAB 2: Statistical Discrimination Spiral
# ==========================================
with tab2:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='card-header'>📊 统计性歧视——「自我实现的预言」</div>", unsafe_allow_html=True)
    
    st.markdown("""
    **统计性歧视的逻辑链：**
    > 雇主观察到：群体 B 的平均离职率更高 → 雇主给群体 B 更低的起薪/更少的培训机会 →
    > 群体 B 的人力资本积累受阻 → 十年后，群体 B 真的「更差」→ 雇主的歧视被"数据验证"了。
    
    **这是一个完美的恶性循环——而最初的原因可能只是一次历史上的偶然偏见。**
    """)
    
    col_s1, col_s2 = st.columns([1, 2])
    
    with col_s1:
        st.markdown("##### 🎚️ 调节螺旋参数")
        initial_gap = st.slider("初始偏见 (历史遗留)", 0, 30, 10, key="init_gap",
                                help="历史上的起始工资差距 (%)")
        invest_reduction = st.slider("被歧视者人力资本投资减少 (%)", 0, 50, 20, 5, key="invest_red")
        employer_amplify = st.slider("雇主统计偏见放大系数", 1.0, 3.0, 1.5, 0.1, key="amplify")
        rounds = st.slider("观察代际数", 1, 10, 5, key="rounds")
    
    with col_s2:
        gaps = [initial_gap]
        for i in range(rounds):
            new_gap_raw = gaps[-1] + invest_reduction * (1 + i * 0.1)
            new_gap = new_gap_raw * employer_amplify
            gaps.append(round(new_gap, 1))
        
        rounds_vec = np.arange(rounds + 1)
        
        fig2 = go.Figure()
        
        fig2.add_trace(go.Scatter(
            x=rounds_vec, y=[initial_gap] * (rounds + 1),
            mode='lines', name='无自我强化 (理想)',
            line=dict(color=COLOR["success"], width=2, dash='dash'),
            hovertemplate='无自我强化: 差距=%{y}%<extra></extra>'
        ))
        
        fig2.add_trace(go.Scatter(
            x=rounds_vec, y=gaps,
            mode='lines+markers', name='歧视自我强化螺旋',
            line=dict(color=COLOR["danger"], width=4),
            marker=dict(size=10, color=COLOR["danger"]),
            fill='tozeroy', fillcolor='rgba(239, 68, 68, 0.1)',
            hovertemplate='第%{x}代<br>工资差距: %{y:.1f}%<br>累计扩大: %{customdata:+.1f}%<extra></extra>',
            customdata=[g - initial_gap for g in gaps]
        ))
        
        fig2.add_annotation(
            x=rounds, y=gaps[-1] * 0.5,
            text=f"📈 第{rounds}代:<br>差距 = <b>{gaps[-1]:.1f}%</b>",
            showarrow=False, font=dict(size=14, color=COLOR["danger"]),
            bgcolor="rgba(255,255,255,0.9)", borderpad=8
        )
        
        fig2.update_layout(
            xaxis_title="代际", yaxis_title="工资差距 (%)",
            xaxis=dict(dtick=1, gridcolor="rgba(0, 0, 0, 0.08)"),
            yaxis=dict(gridcolor="rgba(0, 0, 0, 0.08)"),
            template="plotly_white",
            height=380, margin=dict(l=40, r=20, t=20, b=40),
            legend=dict(),
            hovermode='x unified'
        )
        
        st.plotly_chart(fig2, use_container_width=True)
    
    st.markdown(f"""
    <div style="background: #fef2f2; border: 1px solid {COLOR['danger']}; border-radius: 8px; padding: 16px; margin: 12px 0;">
    <strong>⚠️ 螺旋诊断：</strong> 初始仅 {initial_gap}% 的工资差距，经过 {rounds} 代自我强化后，扩大至 <strong>{gaps[-1]:.1f}%</strong>（扩大了 {gaps[-1]/initial_gap:.1f} 倍）。<br>
    
    <strong>经济学含义：</strong>统计性歧视的危险不在于它起始时的准确度，而在于它的<strong>自我验证机制</strong>。
    即使最初的统计推断有微小的合理性，在反馈循环中也会不断放大，直到变成系统性的不公正。<br>
    
    <strong>唯一的破解方式：</strong>外部的政策干预（如信息披露制度、积极平权），切断「歧视 → 低投资 → 差表现 → 歧视被验证」的反馈链。
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# TAB 3: 中国政策实验
# ==========================================
with tab3:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='card-header'>🏛️ 中国劳动力市场的歧视形态与政策实验</div>", unsafe_allow_html=True)
    
    st.markdown("""
    ### 🇨🇳 中国特色的歧视维度
    与西方国家主要以种族歧视为焦点不同，中国劳动力市场的歧视呈现独特的多维形态：
    """)
    
    col_form, col_policy = st.columns([1, 2])
    
    with col_form:
        st.markdown("##### 📋 歧视类型（多选）")
        hukou = st.checkbox("🏠 户籍歧视", value=True, key="hukou_d")
        gender = st.checkbox("♀️ 性别歧视", value=False, key="gender_d")
        age = st.checkbox("🎂 年龄歧视 (35岁门槛)", value=False, key="age_d")
        school = st.checkbox("🎓 第一学历歧视 (非985/211)", value=False, key="school_d")
        
        n_types = sum([hukou, gender, age, school])
        
        if hukou:
            st.slider("户籍歧视强度 (%)", 0, 40, 15, 5, key="hukou_strength")
        if gender:
            st.slider("性别歧视强度 (%)", 0, 30, 10, 5, key="gender_strength")
        if age:
            st.slider("年龄歧视强度 (%)", 0, 40, 20, 5, key="age_strength")
        if school:
            st.slider("学历歧视强度 (%)", 0, 30, 10, 5, key="school_strength")
        
        st.markdown("---")
        st.markdown("##### 🛡️ 政策干预")
        eq_pay = st.checkbox("同工同酬法 (禁止工资歧视)", value=True, key="eq_pay")
        aa = st.checkbox("平权行动配额 (企业必须雇佣一定比例)", value=False, key="aa")
        info_disc = st.checkbox("信息披露制度 (公示薪酬数据)", value=False, key="info_disc")
        
        if eq_pay:
            eq_pay_str = st.slider("同工同酬执行力度 (%)", 0, 100, 60, 10, key="eq_pay_str")
        else:
            eq_pay_str = 0
        if aa:
            aa_quota = st.slider("平权配额 (%)", 5, 50, 20, 5, key="aa_quota")
        else:
            aa_quota = 0
        if info_disc:
            info_str = st.slider("信息披露透明度 (%)", 0, 100, 50, 10, key="info_str")
        else:
            info_str = 0
    
    with col_policy:
        total_disc = 0
        disc_labels = []
        if hukou:
            total_disc += st.session_state.get("hukou_strength", 15)
            disc_labels.append("户籍")
        if gender:
            total_disc += st.session_state.get("gender_strength", 10)
            disc_labels.append("性别")
        if age:
            total_disc += st.session_state.get("age_strength", 20)
            disc_labels.append("年龄")
        if school:
            total_disc += st.session_state.get("school_strength", 10)
            disc_labels.append("学历")
        
        policy_reduction = eq_pay_str * 0.01 * total_disc * 0.7
        policy_reduction += aa_quota * 0.015 * total_disc
        policy_reduction += info_str * 0.01 * total_disc * 0.3
        
        final_disc = max(0, total_disc - policy_reduction)
        
        disc_before = np.array([total_disc] * 8)
        time_vec = np.arange(8)
        
        fig3 = go.Figure()
        
        fig3.add_trace(go.Scatter(
            x=time_vec, y=disc_before, name="无政策干预",
            line=dict(color=COLOR["danger"], width=3, dash='dot'),
            hovertemplate='无政策: 工资差距=%{y:.0f}%<extra></extra>'
        ))
        
        policy_path = []
        for i in range(8):
            t = i / 7
            policy_path.append(total_disc - (total_disc - final_disc) * t)
        
        fig3.add_trace(go.Scatter(
            x=time_vec, y=policy_path, name="政策干预后",
            line=dict(color=COLOR["success"], width=4),
            fill='tonexty', fillcolor='rgba(16, 185, 129, 0.1)',
            hovertemplate='政策第%{x}年<br>工资差距: %{y:.1f}%<br>已消除: %{customdata:.1f}%<extra></extra>',
            customdata=[total_disc - pp for pp in policy_path]
        ))
        
        fig3.add_hline(y=0, line_dash="dash", line_color=COLOR["warning"],
                       annotation_text="🎯 完全消除歧视", annotation_font=dict(color=COLOR["warning"]))
        
        fig3.update_layout(
            xaxis_title="政策实施年份", yaxis_title="工资差距 (%)",
            xaxis=dict(gridcolor="rgba(0, 0, 0, 0.08)"),
            yaxis=dict(range=[0, max(total_disc * 1.3, 10)], gridcolor="rgba(0, 0, 0, 0.08)"),
            template="plotly_white",
            height=380, margin=dict(l=40, r=20, t=20, b=40),
            legend=dict(),
            hovermode='x unified'
        )
        
        st.plotly_chart(fig3, use_container_width=True)
        
        st.markdown(f"""
        <div style="background: #ecfdf5; border: 1px solid {COLOR['success']}; border-radius: 8px; padding: 16px; margin: 12px 0;">
        <strong>🏛️ 政策干预效果评估</strong><br><br>
        
        📊 <strong>歧视维度：</strong>{' + '.join(disc_labels) if disc_labels else '无'}
        → 初始工资差距：<strong>{total_disc:.0f}%</strong><br>
        
        🛡️ <strong>政策组合：</strong>
        {'同工同酬法（{:.0f}%执行力）'.format(eq_pay_str) if eq_pay else ''}
        {' + 平权配额（{:.0f}%）'.format(aa_quota) if aa else ''}
        {' + 信息披露（{:.0f}%透明）'.format(info_str) if info_disc else ''}
        {'无——完全依赖市场自发调节' if not any([eq_pay, aa, info_disc]) else ''}<br>
        
        ✅ <strong>政策后差距：{final_disc:.0f}%</strong>（消除了 <strong>{total_disc - final_disc:.0f}%</strong>）<br>
        
        📈 剩余差距: {final_disc:.0f}% — {'完全消除！市场回归公平定价。' if final_disc < 1 else '仍需持续干预，歧视具有制度惯性。' if final_disc > 5 else '接近消除，微量遗留差别可接受。'}
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 课程思政
# ==========================================
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.markdown("<div class='card-header'>🏛️ 深度思考：歧视的经济学与社会学</div>", unsafe_allow_html=True)

col_ideo1, col_ideo2 = st.columns(2)

with col_ideo1:
    st.markdown("""
    ### 1. 市场的限界
    > 贝克尔告诉我们：竞争性市场**理论上**会消除歧视。
    > 但现实告诉我们：歧视持续存在了几百年。
    > 
    > 这个差距——恰好是经济学从「黑板模型」走向「真实世界」的门槛。
    > 市场需要**制度基础设施**（法律、信息、文化）才能实现它的公平定价功能。
    
    ### 2. 中国劳动力市场的特殊性
    > 户籍制度是中国独有的劳动力市场摩擦——它不仅仅是一种「偏好歧视」，
    > 更是一种**制度性歧视**，由国家力量直接嵌入了市场。
    > 2014年来的户籍改革，本质上是在拆除这道制度性壁垒。
    """)

with col_ideo2:
    st.markdown("""
    ### 3. 超越补偿——走向制度变革
    > 光靠「同工同酬法」不够——因为歧视的根源不是工资条，而是**进入门槛**。
    > 
    > 拥挤假说的洞见：当某一群体被「挤」入少数低薪职业，
    > 即使这些职业内部同工同酬，整体工资差距依然存在。
    > 真正的公平需要拆除职业准入的隐形天花板。
    
    ### 4. 数据的力量
    > 信息披露制度可能是最被低估的反歧视武器。
    > 当企业薪酬数据被公示，统计性歧视的**信息不对称基础**就被瓦解了。
    > 
    > 这正是「阳光是最好的消毒剂」在经济学中的精确对应。
    """)

st.markdown("---")

if "disc_pred_done" in st.session_state:
    user_pred_d = st.session_state.get("disc_pred_answer", "")
    st.info(f"📝 **你的预测 vs 经济学共识：**\n\n"
            f"你的判断：{user_pred_d}\n\n"
            f"经济学共识：**C** — 歧视不仅存在，还会自我强化。"
            f"贝克尔模型的结论（A：市场自动消除）只在完美竞争条件下成立。"
            f"现实中，统计性歧视、制度刚性、社会规范形成了**自我维系的歧视均衡**。\n\n"
            f"这也是为什么——反歧视法不是多余的，而是让市场回归效率的**基础设施**。")

st.markdown("</div>", unsafe_allow_html=True)
