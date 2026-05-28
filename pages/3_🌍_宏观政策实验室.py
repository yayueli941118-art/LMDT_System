"""
宏观政策实验室 — 贝弗里奇曲线 + AI冲击 + 政策沙盘 + 新质生产力
学术极简风 · 前测拦截 · 挑战任务卡
"""

import streamlit as st
import numpy as np
import plotly.graph_objects as go
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from shared import (
    COLOR, SHARED_CSS,
    render_page_banner, render_card_header,
    render_challenge_card, render_predict_gate, render_policy_tag,
    calc_beveridge,
    generate_lab_report, generate_report_download,
    CHINA_BEVERIDGE_BASELINE, DATA_SOURCES,
)

st.set_page_config(page_title="宏观政策实验室", page_icon="🌍", layout="wide")
st.markdown(SHARED_CSS(), unsafe_allow_html=True)

render_page_banner("🌍", "宏观政策实验室", "Macro Lab · Beveridge Curve", "purple")

# ==========================================
# 侧边栏 — 仅保留全局重置 + 导航
# ==========================================
with st.sidebar:
    st.header("⚙️ 全局控制")

    def _reset_macro():
        for key in list(st.session_state.keys()):
            if key.startswith(("ai_", "mis_", "pol_", "macro_", "bc_")):
                del st.session_state[key]

    st.button("🔄 重置所有参数", use_container_width=True, on_click=_reset_macro)
    st.divider()
    st.markdown("##### 🏛️ 政策百科")
    st.caption("**最低工资** → 保障低端收入，可能降低低技能就业")
    st.caption("**技能重塑补贴** → 降低错配，新质生产力核心")
    st.caption("**失业救济金** → 安全网，过高推高保留工资")
    st.divider()
    st.page_link("🏠_综合门户首页.py", label="🏠 返回门户", use_container_width=True)

# ==========================================
# 挑战任务卡
# ==========================================
render_challenge_card(
    title="市长挑战",
    description="AI替代指数高达 <b style='color:#ef4444;'>70%</b>，请在不动用救济金的前提下，将失业率控制在 <b style='color:#10b981;'>5% 以内</b>。"
)
with st.expander("📋 更多挑战任务", expanded=False):
    st.markdown("##### 🤖 AI冲击应对")
    st.caption("AI冲击70% → 选最优政策组合使贝弗里奇曲线尽可能接近理想状态。可叠加。")
    st.markdown("##### 🌐 新质生产力战略")
    st.caption("设置技能错配度1.5 → 开启「技能重塑补贴」→ 观察曲线回移幅度。")

# ==========================================
# 前测拦截 — 必须先预测才能实验
# ==========================================
gate_unlocked = render_predict_gate(
    question="**当AI技术冲击增强时，贝弗里奇曲线会如何变化？**",
    options=["A. 向原点靠近（匹配效率提升）", "B. 向右上方移动（匹配效率下降）", "C. 没有变化"],
    var_name="macro_bc"
)

if gate_unlocked:
    # 前测反馈
    user_ans = st.session_state.get("macro_bc_answer", "")
    if "B" in user_ans:
        st.success("✅ 预测正确！AI冲击导致结构性失业加剧，贝弗里奇曲线外移。")
    else:
        st.info("📚 让我们看看实际结果——实验结果会给你答案。")

    # ==========================================
    # 参数区 — 滑块紧贴图表上方
    # ==========================================
    st.markdown('<div class="card">', unsafe_allow_html=True)
    render_card_header("🎛️ 宏观数据驾驶舱", color=COLOR["macro"])

    c_ai, c_mis, c_pol = st.columns([1, 1, 2])
    with c_ai:
        ai_risk = st.slider(
            "🤖 AI 替代冲击 (%)", 0, 100, 30, key="ai_main",
            help="模拟AI/自动化对旧技能岗位的替代程度"
        )
    with c_mis:
        mismatch = st.slider(
            "🔧 技能错配度", 0.0, 2.0, 0.8, 0.1, key="mis_main",
            help="0=无错配, 2.0=严重错配"
        )
    with c_pol:
        policy = st.multiselect(
            "📋 政策工具箱",
            ["最低工资调整", "技能重塑补贴(Reskilling)", "失业救济金"],
            key="pol_main",
            help="可多选，政策效果可叠加。推荐：技能重塑补贴"
        )
        policy_score = 1.0 if "技能重塑补贴(Reskilling)" in policy else 0
        if "技能重塑补贴(Reskilling)" in policy:
            render_policy_tag("🚀 新质生产力 · 技能重塑", "green")

    st.markdown('</div>', unsafe_allow_html=True)

    # ==========================================
    # 贝弗里奇曲线 + 右侧诊断
    # ==========================================
    st.markdown('<div class="card">', unsafe_allow_html=True)
    render_card_header("🧬 结构性失业诊断 (Beveridge Curve)", color=COLOR["macro"])

    # 政策副作用
    policy_penalty_u = 0.0
    policy_penalty_v = 0.0
    if "最低工资调整" in policy:
        policy_penalty_u += 0.15
        policy_penalty_v -= 0.10
    if "失业救济金" in policy:
        policy_penalty_u += 0.20
        policy_penalty_v += 0.15

    _adj_mismatch = mismatch + policy_penalty_u
    _adj_policy = policy_score - policy_penalty_v * 0.5
    u, v = calc_beveridge(_adj_mismatch, _adj_policy, ai_risk)
    u_base, v_base = calc_beveridge(0, 0, 0)

    col_chart, col_diag = st.columns([3, 1])

    with col_chart:
        fig1 = go.Figure()

        # 1. 理想曲线
        fig1.add_trace(go.Scatter(
            x=u_base, y=v_base, name="理想高效市场",
            line=dict(color='#cbd5e1', dash='dot', width=2),
            hoverinfo='skip'
        ))

        # 2. AI冲击前路径
        u_noai, v_noai = calc_beveridge(mismatch, policy_score, 0)
        fig1.add_trace(go.Scatter(
            x=u_noai, y=v_noai, name="AI冲击前路径",
            line=dict(color=COLOR["macro"], width=2, dash='dot'),
            hoverinfo='skip'
        ))

        # 3. 当前实时曲线
        fig1.add_trace(go.Scatter(
            x=u, y=v, name="当前市场状态",
            line=dict(color=COLOR["danger"], width=4),
            hovertemplate='<b>失业率: %{x:.1f}%</b><br>空缺率: %{y:.1f}%<extra></extra>'
        ))

        # 4. 当前决策点
        current_u = u[len(u)//2]
        current_v = v[len(v)//2]
        fig1.add_trace(go.Scatter(
            x=[current_u], y=[current_v],
            mode='markers+text',
            name='当前位置',
            marker=dict(size=14, color=COLOR["danger"], line=dict(width=2, color='white')),
            text=["📍"],
            textposition="top center"
        ))

        # 5. 中国数据基准点
        fig1.add_trace(go.Scatter(
            x=[CHINA_BEVERIDGE_BASELINE["urban_unemployment"]],
            y=[CHINA_BEVERIDGE_BASELINE["job_vacancy_ratio"]],
            mode='markers', name='中国2024实际',
            marker=dict(size=12, color=COLOR["success"], symbol='star',
                       line=dict(width=1.5, color='white'))
        ))

        # 外移标注
        if ai_risk >= 30:
            fig1.add_annotation(
                x=5.5, y=20,
                text="↗ 结构性失业加剧",
                showarrow=True, arrowhead=2, ax=50, ay=-50,
                font=dict(color=COLOR["danger"], size=13)
            )

        fig1.update_layout(
            xaxis_title="失业率 U (%)", yaxis_title="职位空缺率 V (%)",
            template="plotly_white",
            height=430,
            margin=dict(l=20, r=20, t=10, b=20),
            yaxis=dict(range=[0, 35]),
            xaxis=dict(range=[0, 15]),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02)
        )
        st.plotly_chart(fig1, use_container_width=True)
        st.caption(f"{DATA_SOURCES['beveridge']}，城镇调查失业率: {CHINA_BEVERIDGE_BASELINE['urban_unemployment']}%")

    with col_diag:
        st.markdown("##### 📊 实时诊断")

        # 使用 st.metric 代替自定义 render_metric_card
        ai_delta = "inverse" if ai_risk > 50 else "normal"
        st.metric("AI 冲击指数", f"{ai_risk}%",
                  delta="⚠️ 高危" if ai_risk > 70 else ("⚠️ 关注" if ai_risk > 50 else "正常"),
                  delta_color=ai_delta)

        st.metric("技能错配度", f"{mismatch:.1f}",
                  delta="严重" if mismatch > 1.0 else "可控",
                  delta_color="inverse" if mismatch > 1.0 else "normal")

        # 诊断
        if mismatch >= 0.8 and not policy:
            st.error("🚨 **典型的结构性失业**\n\n高失业率（7.8%）与高空缺率（5.15%）并存。")
        elif "最低工资调整" in policy and mismatch >= 0.8 and "技能重塑补贴(Reskilling)" not in policy:
            st.error("🚨 **需求侧干预失效**\n\n价格下限无法解决技能错配。")
        elif "技能重塑补贴(Reskilling)" in policy and mismatch >= 0.8:
            st.success("✅ **供给侧改革奏效**\n\n技能重塑抵消错配，失业率回落至 3.4%。")
        else:
            if ai_risk > 70:
                st.error("🚨 **极度危险**\n\nAI大规模替代，匹配效率崩塌。")
            elif mismatch > 1.0:
                st.warning(f"⚠️ **结构性失业**\n\n高失业+高空缺并存")
            else:
                st.success("✅ **运行良好**\n\n主要为摩擦性失业。")

        if "技能重塑补贴(Reskilling)" in policy:
            st.info("✅ **新质生产力 · 技能重塑**\n\n曲线正向原点回归。")
        if "最低工资调整" in policy:
            st.warning("⚠️ **最低工资副作用**\n\n可能降低低技能需求")
        if "失业救济金" in policy:
            st.info("ℹ️ **救济金效应**\n\n提供安全网，需注意保留工资上升")

    st.markdown('</div>', unsafe_allow_html=True)

    # ==========================================
    # 政策组合报告
    # ==========================================
    st.markdown('<div class="card">', unsafe_allow_html=True)
    render_card_header("📊 政策组合效果报告", color=COLOR["macro"])

    if not policy:
        st.warning("⚠️ 当前未实施任何干预政策，市场处于自然演化状态。")
        st.markdown("""
        > 💡 **建议**：在上方政策工具箱中选择至少一项政策进行干预实验。
        > 推荐从「技能重塑补贴」开始——这是应对AI冲击最有效的供给侧政策。
        """)
    else:
        for p in policy:
            if p == "最低工资调整":
                st.markdown("""
                **📌 最低工资调整**
                - ✅ 保障低收入者基本生活
                - ⚠️ 可能导致低技能劳动力需求沿D曲线收缩
                - 📖 理论依据：最低工资的就业效应（Card & Krueger, 1994）
                """)
            elif p == "技能重塑补贴(Reskilling)":
                st.markdown("""
                **🚀 技能重塑补贴**
                - ✅ 降低结构性错配，应对AI冲击最有效的长期手段
                - 🏛️ 符合国家「新质生产力」战略
                - 📖 政策方向：人社部「十四五」职业技能培训规划
                """)
                st.markdown("""
                <div style="background:#f3e8ff; border:1px solid #8b5cf6; border-radius:8px; padding:12px; margin:10px 0;">
                <strong>🏛️ 课程思政 · 新质生产力</strong><br>
                <span style="font-size:14px;">从"人口红利"转向"人才红利"。技能重塑补贴正是这一国家战略
                在劳动力市场政策中的体现：投资人力资本，使劳动者从被AI替代的岗位
                转向AI难以替代的高技能岗位。</span>
                </div>
                """, unsafe_allow_html=True)
            elif p == "失业救济金":
                st.markdown("""
                **🛡️ 失业救济金**
                - ✅ 提供社会安全网，保障失业者基本生活
                - ⚠️ 过高可能增加"保留工资"，延长失业持续时间
                - 📖 关键设计：期限限制 + 递减发放 + 与培训挂钩
                """)

    st.markdown('</div>', unsafe_allow_html=True)

    # ==========================================
    # 实验报告
    # ==========================================
    st.markdown('<div class="card">', unsafe_allow_html=True)
    render_card_header("📝 实验报告生成", color=COLOR["macro"])

    params = {
        "AI替代冲击": f"{ai_risk}%",
        "技能错配指数": f"{mismatch:.1f}",
        "实施政策": ", ".join(policy) if policy else "无",
    }

    analysis_text = f"""
### 1. 结构性失业诊断
本次模拟了 **{ai_risk}%** 的AI技术替代冲击。
{'极端AI冲击下，贝弗里奇曲线剧烈右上方移动，旧技能劳动者被大规模淘汰。' if ai_risk > 70 else 'AI冲击尚在可控范围内。'}

### 2. 政策干预效果
采用政策组合：{'、'.join(policy) if policy else '未实施任何干预'}。
{'技能重塑补贴有效促进了劳动力技能升级，使贝弗里奇曲线向原点回归。' if '技能重塑补贴(Reskilling)' in policy else '缺乏针对性培训政策，结构性错配难以短期自动修复。'}
"""

    results_pack = {
        "analysis": analysis_text,
        "reflection_questions": """
1. 为什么单纯提高最低工资对AI冲击的结构性失业效果有限？
2. 投资于技能重塑 vs 发放失业救济金，哪个更可持续？
3. "新质生产力"战略中，高校应如何调整培养方案？
""",
        "ideology_text": f"""
{'技能重塑补贴体现了国家「新质生产力」战略在劳动力市场领域的实践路径。' if '技能重塑补贴(Reskilling)' in policy else '建议启用技能重塑政策，观察供给侧干预如何体现新质生产力的人才战略。'}""",
        "conclusion": "技术冲击引发的结构性失业，单纯需求侧刺激效果有限，必须配合供给侧技能重塑政策。"
    }

    report_text = generate_lab_report("macro", params, results_pack)
    generate_report_download(report_text, "Macro_Lab")
    st.markdown('</div>', unsafe_allow_html=True)

    # 参数校准
    with st.expander("📐 底层参数校准说明 (Methodology)", expanded=False):
        st.markdown("""
### 贝弗里奇曲线参数校准

| 参数 | 校准依据 | 来源 |
|------|---------|------|
| 匹配效率 μ (0.5) | 中国劳动力市场匹配效率估计 | Pissarides (2000) |
| 贝弗里奇曲率 | Cobb-Douglas M=μ·U⁰·⁵V⁰·⁵ | Petrongolo & Pissarides (2001) |
| 自然失业率 (≈5%) | 城镇调查失业率长期均值 | 国家统计局 (2024) |
| AI替代冲击 默认30% | AI暴露度加权平均 | Felten et al. (2023) + 麦肯锡 |
| 技能错配指数 | 制造业技能缺口估计 | 人社部《制造业人才发展规划指南》 |
        """)
