"""
个体职业发展实验室 — 人力资本投资与职业决策仿真
学术极简风 · 前测拦截 · 挑战任务卡 · 滑块紧贴图表
"""

import streamlit as st
import numpy as np
import plotly.graph_objects as go
import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from shared import (
    SHARED_CSS, COLOR,
    render_page_banner, render_card_header, render_challenge_card,
    render_predict_gate, render_policy_tag,
    calc_mincer, calc_migration_npv,
    CHINA_WAGE_BY_EDU_2024, CHINA_MIGRANT_WAGE_2024,
    EDUCATION_LABELS, DATA_SOURCES,
    SCHOOL_NAME, AUTHOR_NAME,
)

st.set_page_config(page_title="个体职业实验室", page_icon="👤", layout="wide")
st.markdown(SHARED_CSS(), unsafe_allow_html=True)

render_page_banner("👤", "个体职业发展实验室", "Human Capital · Mincer Equation", "blue")

# ==========================================
# 侧边栏 — 仅保留全局重置 + 导航 + 快捷预设
# ==========================================
with st.sidebar:
    st.header("⚙️ 全局控制")

    def _reset_micro():
        for key in list(st.session_state.keys()):
            if key.startswith(("micro_", "edu_", "exp_", "train_", "migr_", "disc_")):
                del st.session_state[key]

    st.button("🔄 重置所有参数", use_container_width=True, on_click=_reset_micro)
    st.divider()
    st.markdown("##### 🎓 快捷预设")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        if st.button("🎓 博士", key="phd", use_container_width=True, help="22年教育"):
            st.session_state.edu = 22
    with col_b:
        if st.button("📚 硕士", key="master", use_container_width=True, help="19年教育"):
            st.session_state.edu = 19
    with col_c:
        if st.button("🏭 打工", key="worker", use_container_width=True, help="12年教育"):
            st.session_state.edu = 12
    st.divider()
    st.page_link("🏠_综合门户首页.py", label="🏠 返回门户", use_container_width=True)
    st.page_link("pages/1c_✈️_迁移决策仿真.py", label="✈️ 深度迁移决策 →", use_container_width=True)
    st.page_link("pages/1b_⚖️_劳动供给决策.py", label="⚖️ 收入/替代效应 →", use_container_width=True)
    st.page_link("pages/1d_🚫_歧视经济学实验.py", label="🚫 歧视经济学 →", use_container_width=True)
    st.page_link("pages/1e_💰_工资决定与收入差距.py", label="💰 工资决定 →", use_container_width=True)
    st.page_link("pages/1f_📉_失业经济学.py", label="📉 失业经济学 →", use_container_width=True)

# ==========================================
# 情境代入（可折叠）
# ==========================================
with st.expander("📋 你的故事（点击展开）", expanded=False):
    st.markdown("""
    **🎓 假设你正站在人生的十字路口——**
    
    你刚高中毕业，面前有三条路：
    - 📚 **继续读书**（本科 → 硕士 → 博士），但 4~10 年没有全职收入
    - 🏭 **直接工作**，早早赚钱，起薪低、天花板有限
    - 🏙️ **去大城市闯荡**，高薪但房租贵、压力大
    
    **你要做一个可能会影响你未来 40 年的决定。**
    """)

# ==========================================
# 挑战任务卡
# ==========================================
render_challenge_card(
    title="人生规划挑战",
    description="你的目标是使<b style='color:#2563eb;'>终身收入最大化</b>，同时考虑培训投资回报和迁移成本。请选择最优的教育年限、培训类型和城市策略。"
)

# ==========================================
# 前测拦截
# ==========================================
gate_unlocked = render_predict_gate(
    question="**你认为：读 4 年本科（vs 高中毕业直接工作），一生的总收入会增加多少？**",
    options=["A. 不到 10%（差不多）", "B. 约 20~50%（有明显提升）",
             "C. 超过 100%（翻倍以上）", "D. 不一定，还要看培训和歧视因素"],
    var_name="micro_pred"
)

if gate_unlocked:
    # 前测反馈
    user_ans = st.session_state.get("micro_pred_answer", "")
    if "D" in user_ans:
        st.success("✅ 你的直觉很成熟！教育回报确实受培训、歧视、市场环境等多因素影响。")
    else:
        st.info("📚 让我们看看实验数据怎么说——可能和直觉有差距。")

    # ==========================================
    # 参数面板 — 直接在主体中，紧贴图表上方
    # ==========================================
    st.markdown('<div class="card">', unsafe_allow_html=True)
    render_card_header("🎛️ 你的人生参数")

    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        edu = st.slider("🎓 受教育年限", 9, 22, 16, key="edu",
                        help="9=初中 | 12=高中 | 16=本科 | 19=硕士 | 22=博士")
        edu_label = EDUCATION_LABELS.get(edu, f"{edu}年")
        st.caption(f"当前：**{edu_label}**")

    with c2:
        exp_peak = st.slider("📈 职业生涯观察年限", 5, 40, 40, 5, key="exp",
                             help="你想看未来多少年的收入曲线？")

    with c3:
        train_type = st.radio("🏋️ 培训投资类型",
                              ["无额外培训", "一般培训 (通用技能)", "特殊培训 (企业专属技能)"],
                              key="train", horizontal=False)
    gen_t = 5 if "一般" in train_type else 0
    spec_t = 3 if "特殊" in train_type else 0

    c4, c5 = st.columns([1, 1])
    with c4:
        disc = st.slider("⚖️ 劳动力市场歧视 (%)", 0, 40, 10, key="disc",
                         help="非生产率因素（性别/户籍等）导致的工资折损")
    with c5:
        migrate = st.checkbox("🏙️ 考虑迁移至一二线城市？", key="migrate",
                              help="高薪但高成本，值得吗？")
        w_diff, c_move, c_psych = 0, 0, 0
        if migrate:
            w_diff = st.slider("城市月薪优势 (k)", 2, 30, 10, key="wdiff")
            c_move = st.slider("一次性搬迁成本 (k)", 5, 80, 25, key="cmove")
            c_psych = st.slider("年度心理成本 (k)", 0, 30, 8, key="cpsych")

    st.markdown('</div>', unsafe_allow_html=True)

    # ==========================================
    # 核心计算
    # ==========================================
    exp_vec = np.linspace(0, exp_peak, 120)
    w_exp, w_disc = calc_mincer(edu, exp_vec, gen_t, spec_t, disc)
    w_base, _ = calc_mincer(12, exp_vec, 0, 0, 0)

    real_wage = CHINA_WAGE_BY_EDU_2024.get(edu)
    edu_label_full = EDUCATION_LABELS.get(edu, f"{edu}年")

    migrate_years, migrate_npv = None, None
    if migrate and w_diff > 0:
        migrate_years, migrate_npv = calc_migration_npv(5, 5 + w_diff, c_move, c_psych)

    lifetime_edu = np.trapezoid(w_exp, exp_vec)
    lifetime_base = np.trapezoid(w_base, exp_vec)
    premium = (lifetime_edu / lifetime_base - 1) * 100

    # ==========================================
    # st.metric 指标卡片行
    # ==========================================
    st.markdown('<div class="card">', unsafe_allow_html=True)
    render_card_header("📊 关键数据面板")

    mc1, mc2, mc3, mc4 = st.columns(4)

    with mc1:
        delta_c = "normal" if premium > 0 else "inverse"
        st.metric("一生总收入提升", f"{premium:+.1f}%",
                  delta=f"vs 高中毕业", delta_color=delta_c)

    with mc2:
        if disc > 0:
            st.metric("歧视导致的损失", f"-{disc}%",
                      delta="工资被压低 ↓", delta_color="inverse")
        else:
            st.metric("市场公平度", "无歧视", delta="✅")

    with mc3:
        if real_wage:
            dev = (w_exp[0] / real_wage - 1) * 100
            st.metric("vs 中国实际基准", f"{dev:+.1f}%",
                      delta=f"{edu_label_full}均薪{real_wage}元", delta_color="off")
        else:
            st.metric("数据基准", "无对应数据")

    with mc4:
        cum_edu = np.cumsum(w_exp)
        cum_base = np.cumsum(w_base)
        diff_cum = cum_edu - cum_base
        be_idx = None
        for i, d in enumerate(diff_cum):
            if d > 0 and (i == 0 or diff_cum[i-1] <= 0):
                be_idx = i
                break
        if be_idx and diff_cum[-1] > 0:
            st.metric("投资回本年限", f"≈{exp_vec[be_idx]:.0f}年",
                      delta="之后全是净收益")
        else:
            st.metric("回本评估", "未达回本点", delta="教育投入过大？")

    st.markdown('</div>', unsafe_allow_html=True)

    # ==========================================
    # 工资曲线 + 迁移分析
    # ==========================================
    st.markdown('<div class="card">', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📈 工资曲线", "🏙️ 迁移分析"])

    with tab1:
        fig1 = go.Figure()

        # 对照组（高中）
        fig1.add_trace(go.Scatter(
            x=exp_vec, y=w_base, name="对照组 (高中毕业)",
            line=dict(color='#cbd5e1', width=2, dash='dot'),
            hovertemplate='工龄: %{x:.0f}年<br>工资指数: %{y:.1f}<extra></extra>'
        ))

        # 实验组
        fig1.add_trace(go.Scatter(
            x=exp_vec, y=w_exp, name=f'你的选择 ({edu_label})',
            line=dict(color=COLOR["primary"], width=4),
            fill='tonexty', fillcolor='rgba(37, 99, 235, 0.06)',
            hovertemplate=f'<b>工龄: %{{x:.0f}}年</b><br>工资: %{{y:.1f}}<extra></extra>'
        ))

        # 歧视后工资
        if disc > 0:
            fig1.add_trace(go.Scatter(
                x=exp_vec, y=w_disc, name=f'歧视影响 (-{disc}%)',
                line=dict(color=COLOR["danger"], width=2, dash='dot'),
                hovertemplate='工龄: %{x:.0f}年<br>歧视后: %{y:.1f}<extra></extra>'
            ))
            fig1.add_trace(go.Scatter(
                x=np.concatenate([exp_vec, exp_vec[::-1]]),
                y=np.concatenate([w_disc, w_exp[::-1]]),
                fill='toself', fillcolor='rgba(239, 68, 68, 0.06)',
                line=dict(width=0), hoverinfo='skip', name='歧视损失'
            ))

        # 盈亏平衡点
        if be_idx and diff_cum[-1] > 0:
            fig1.add_vline(
                x=exp_vec[be_idx], line_dash="dash", line_color=COLOR["success"],
                annotation_text=f"回本 ≈{exp_vec[be_idx]:.0f}年",
                annotation_font=dict(color=COLOR["success"], size=11)
            )
            fig1.add_trace(go.Scatter(
                x=[exp_vec[be_idx]], y=[w_exp[be_idx]],
                mode='markers', name='📌 回本点',
                marker=dict(size=14, color=COLOR["success"], symbol='star',
                           line=dict(width=2, color='white'))
            ))

        # 真实数据基准线
        if real_wage:
            fig1.add_hline(
                y=real_wage, line_dash="dash", line_color=COLOR["warning"],
                annotation_text=f"🇨🇳 2024年{edu_label_full}均值≈{real_wage}元",
                annotation_position="bottom right",
                annotation_font=dict(size=11, color=COLOR["warning"])
            )

        fig1.update_layout(
            xaxis_title="工龄 (年)", yaxis_title="月工资指数",
            template="plotly_white",
            height=400, margin=dict(l=40, r=20, t=10, b=40),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            hovermode='x unified'
        )
        st.plotly_chart(fig1, use_container_width=True)
        if real_wage:
            st.caption(f"📊 {DATA_SOURCES['wage_2024']}")

    with tab2:
        if migrate and migrate_npv is not None:
            fig2 = go.Figure()
            colors_m = [COLOR["danger"] if v < 0 else COLOR["success"] for v in migrate_npv]
            fig2.add_trace(go.Bar(
                x=migrate_years, y=migrate_npv, marker_color=colors_m,
                hovertemplate='第%{x}年<br>累计NPV: %{y:.1f}k<extra></extra>',
                name='累计净收益'
            ))
            fig2.update_layout(
                xaxis_title="年份", yaxis_title="累计净收益 (k)",
                template="plotly_white",
                height=380, margin=dict(l=40, r=20, t=10, b=40)
            )
            st.plotly_chart(fig2, use_container_width=True)
            st.caption(f"📊 {DATA_SOURCES['migrant']}：农民工月均收入 {CHINA_MIGRANT_WAGE_2024} 元")

            be_arr = np.where(migrate_npv > 0)[0]
            if len(be_arr) > 0:
                st.success(f"✅ **值得迁移** — 第 **{be_arr[0]+1}** 年收回成本，净收益 **{migrate_npv[-1]:+.0f}k**")
            else:
                st.error(f"❌ **不建议迁移** — {len(migrate_years)} 年内无法回本")
        else:
            st.info("🏠 **你选择了留在家乡**。开启上方「城市迁移决策」探索外出闯荡的收益与代价。")

    st.markdown('</div>', unsafe_allow_html=True)

    # ==========================================
    # AI 诊断报告
    # ==========================================
    st.markdown('<div class="card">', unsafe_allow_html=True)
    render_card_header("💡 你的职业决策诊断")

    col_d1, col_d2 = st.columns([3, 2])

    with col_d1:
        # 教育投资诊断
        if premium > 80:
            st.markdown(f"🎓 **教育回报极高**：选择 **{edu_label_full}** 使终身收入提升 **{premium:.0f}%**。学历信号价值很高。")
        elif premium > 30:
            st.markdown(f"📚 **教育回报可观**：{edu_label_full} 带来 **{premium:.0f}%** 终身收入提升。关注回本年限。")
        else:
            st.markdown(f"⚠️ **教育回报有限**：{edu_label_full} 仅带来 {premium:.0f}% 提升。考虑机会成本是否过高。")

        # 培训诊断
        if "一般" in train_type:
            st.markdown("🏋️ **一般培训**使整条曲线向上平移——可迁移技能跟着你走。")
        elif "特殊" in train_type:
            st.markdown("🔧 **特殊培训**前期工资低（你在'交学费'），后期曲线更陡——前提是不离开这家公司。")

        # 迁移诊断
        if migrate and migrate_npv is not None:
            be_arr = np.where(migrate_npv > 0)[0]
            if len(be_arr) > 0:
                st.markdown(f"🏙️ **城市迁移是理性的**：第 **{be_arr[0]+1}** 年实现净收益。")
            else:
                st.markdown(f"🏠 **留在家乡更明智**：城市工资溢价无法覆盖搬迁和心理成本。")

        # 歧视诊断
        if disc > 15:
            st.markdown(f"🚨 **市场存在显著歧视**（{disc}%）——相同人力资本，不公平竞争。这不是你的问题。")

        # 真实数据对比
        if real_wage:
            dev = (w_exp[0] / real_wage - 1) * 100
            if abs(dev) > 20:
                st.markdown(f"📊 **模型与现实偏离**：起薪与{edu_label_full}实际均值偏差 **{dev:+.0f}%**。明瑟方程的局限性——真实世界远比模型复杂。")

    with col_d2:
        st.markdown("##### 🔮 对比你的预测")
        user_ans = st.session_state.get("micro_pred_answer", "")
        if premium > 100:
            truth_letter = "C"
        elif premium > 20:
            truth_letter = "B"
        else:
            truth_letter = "A"
        if disc > 10 or "特殊" in train_type:
            truth_letter = "D"

        if truth_letter in user_ans:
            st.success(f"✅ 直觉很准！\n\n预测：{user_ans}\n实际：教育溢价 {premium:.0f}%")
        else:
            st.warning(f"🤔 有偏差\n\n预测：{user_ans}\n实际：教育溢价 {premium:.0f}%\n\n直觉与模型之间——这就是经济学。")

        st.markdown("---")
        st.markdown("##### 📋 你的参数速览")
        st.markdown(f"""
        - 学历：{edu_label_full} ({edu} 年)
        - 培训：{train_type}
        - 歧视：{disc}%
        - 迁移：{"是" if migrate else "否"}
        """)

    st.markdown('</div>', unsafe_allow_html=True)

    # ==========================================
    # 课程思政
    # ==========================================
    st.markdown('<div class="card">', unsafe_allow_html=True)
    render_card_header("🏛️ 深度思考：人力资本投资的社会意义")

    st.markdown("""
    **1. 个体职业韧性 (Career Resilience)**
    > 你今天的教育投资，不仅是工资条上的数字变化，更是面对技术变革时的「抗风险能力」。
    > 当 AI 替代低技能岗位时，受过高等教育的人有更强的能力转型、适应、甚至创造新岗位。

    **2. 乡村振兴的人才命题**
    > 如果每个受过高等教育的人都涌入大城市，县城的产业谁来支撑？
    > 当你的迁移 NPV 为负时，也许那不是失败——而是家乡的发展潜力正在追赶城市。

    **3. 超越明瑟方程**
    > 明瑟方程衡量的只是**可货币化的工资回报**，但教育的价值远不止于此——
    > 认知边界的拓展、社交网络的质量、对下一代的文化传递……
    > 这些「非货币收益」无法用模型计算，但它们可能才是教育最深的红利。
    """)

    st.markdown('</div>', unsafe_allow_html=True)

    # 参数校准
    with st.expander("📐 底层参数校准说明 (Methodology)", expanded=False):
        st.markdown("""
### 明瑟收入方程参数校准

| 参数 | 校准依据 | 来源 |
|------|---------|------|
| 教育回报率 (年均 8-10%) | 中国城镇教育回报率微观估计 | 李实, 丁赛 (2003) |
| 工作经验回报 (二次型，峰值30年) | 标准明瑟方程 + CHIP 数据 | Mincer (1974) + 赵西亮 (2017) |
| 中国工资基准 (分学历) | 城镇单位就业人员平均工资 | 中国统计年鉴 2024 |
| 歧视系数默认 10% | 性别/户籍工资差异 Oaxaca 分解 | 王美艳 (2005) + 李实等 (2014) |
        """)
