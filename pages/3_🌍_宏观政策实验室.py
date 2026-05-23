"""
宏观政策实验室 — 贝弗里奇曲线 + AI冲击 + 政策沙盘 + 新质生产力
国赛优化版：真实数据基准、挑战模式、思政融合
"""

import streamlit as st
import numpy as np
import plotly.graph_objects as go
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from shared import (
    COLOR, SHARED_CSS,
    render_page_banner, render_metric_card, render_card_header,
    render_challenge_banner, render_predict_verify, render_policy_tag,
    calc_beveridge,
    generate_lab_report, generate_report_download,
    CHINA_BEVERIDGE_BASELINE, DATA_SOURCES,
)

st.set_page_config(page_title="宏观政策实验室", page_icon="🌍", layout="wide")
st.markdown(SHARED_CSS(color=COLOR["macro"], dark="#4c1d95", light="#8b5cf6"), unsafe_allow_html=True)

render_page_banner("🌍", "宏观政策实验室", "Macro Lab", "purple")

# ==========================================
# 侧边栏
# ==========================================
with st.sidebar:
    st.header("⚙️ 全局设置")
    
    def _reset_macro():
        for key in list(st.session_state.keys()):
            if key.startswith(("ai_", "mis_", "pol_", "macro_")):
                del st.session_state[key]
    
    st.button("🔄 重置所有参数", use_container_width=True, on_click=_reset_macro)
    st.divider()
    st.markdown("##### 🏛️ 政策百科")
    st.info("""
    **最低工资调整** → 保障低端收入，但可能降低低技能就业
    
    **技能重塑补贴** → 降低结构性错配，长期最优，符合新质生产力
    
    **失业救济金** → 社会安全网，过高可能推高保留工资
    """)
    st.divider()
    st.page_link("🏠_综合门户首页.py", label="🏠 返回门户", use_container_width=True)

# ==========================================
# 挑战模式
# ==========================================
render_challenge_banner("macro", [
    ("🤖", "AI冲击应对", "AI冲击设为70%，请选择最优政策组合使贝弗里奇曲线尽可能接近理想状态。\n提示：多项政策可叠加"),
    ("🌐", "新质生产力战略", "设置技能错配度为1.5，然后开启「技能重塑补贴」。观察曲线回移幅度，理解新质生产力战略的核心逻辑"),
])

# ==========================================
# 预测验证
# ==========================================
pred_done, pred_correct, pred_answer = render_predict_verify(
    question="当AI技术冲击增强时，贝弗里奇曲线会如何变化？",
    options=["A. 向原点靠近（匹配效率提升）", "B. 向右上方移动（匹配效率下降）", "C. 没有变化"],
    correct_answer="B. 向右上方移动（匹配效率下降）",
    var_name="macro_bc"
)

# ==========================================
# 参数区
# ==========================================
st.markdown('<div class="card">', unsafe_allow_html=True)
render_card_header("🎛️ 宏观数据驾驶舱", color=COLOR["macro"], dark_color="#4c1d95")

st.markdown("**📌 调节宏观参数**")
c_ai, c_mis, c_pol = st.columns([1, 1, 2])
with c_ai:
    ai_risk = st.slider("AI 替代冲击 (%)", 0, 100, 30, key="ai_main",
                        help="模拟AI/自动化对旧技能岗位的替代程度")
with c_mis:
    mismatch = st.slider("技能错配度", 0.0, 2.0, 0.8, 0.1, key="mis_main",
                        help="0=无错配, 2.0=严重错配")
with c_pol:
    policy = st.multiselect("政策工具箱", 
                            ["最低工资调整", "技能重塑补贴(Reskilling)", "失业救济金"],
                            key="pol_main",
                            help="可多选，政策效果可叠加")
    policy_score = 1.0 if "技能重塑补贴(Reskilling)" in policy else 0

# 新质生产力标签
if "技能重塑补贴(Reskilling)" in policy:
    render_policy_tag("🚀 新质生产力战略 · 技能重塑：培养适应AI时代的复合型人才", "green")

st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 模块一：贝弗里奇曲线
# ==========================================
st.markdown('<div class="card">', unsafe_allow_html=True)
render_card_header("🧬 结构性失业诊断 (Beveridge Curve)", color=COLOR["macro"], dark_color="#4c1d95")

# 计算
u, v = calc_beveridge(mismatch, policy_score, ai_risk)
u_base, v_base = calc_beveridge(0, 0, 0)

col_chart, col_diag = st.columns([3, 1])

with col_chart:
    fig1 = go.Figure()
    
    # 理想曲线
    fig1.add_trace(go.Scatter(
        x=u_base, y=v_base, name="理想高效市场",
        line=dict(color='#cbd5e1', dash='dot', width=2),
        hovertemplate='失业率: %{x:.1f}%<br>空缺率: %{y:.1f}%<br>理想状态<extra></extra>'
    ))
    
    # 当前曲线
    fig1.add_trace(go.Scatter(
        x=u, y=v, name="当前市场状态",
        line=dict(color=COLOR["macro"], width=5),
        hovertemplate='<b>失业率: %{x:.1f}%</b><br>空缺率: %{y:.1f}%<br>💡 当前市场匹配效率<extra></extra>'
    ))
    
    # 中国真实数据基准点
    fig1.add_trace(go.Scatter(
        x=[CHINA_BEVERIDGE_BASELINE["urban_unemployment"]],
        y=[CHINA_BEVERIDGE_BASELINE["job_vacancy_ratio"]],
        mode='markers',
        name='中国2024年实际数据',
        marker=dict(size=16, color=COLOR["success"], symbol='star', line=dict(width=2, color='white')),
        hovertemplate=(
            f'<b>🇨🇳 中国2024年</b><br>'
            f'城镇调查失业率: {CHINA_BEVERIDGE_BASELINE["urban_unemployment"]}%<br>'
            f'求人倍率: {CHINA_BEVERIDGE_BASELINE["job_vacancy_ratio"]}<br>'
            f'<extra></extra>'
        )
    ))
    
    # AI冲击极端的警告
    if ai_risk > 80:
        fig1.add_annotation(
            x=8, y=18,
            text="⚠️ AI冲击导致剧烈外移",
            showarrow=True, arrowhead=2, ax=0, ay=-40,
            font=dict(color=COLOR["danger"], size=14)
        )
    elif ai_risk > 50:
        fig1.add_annotation(
            x=6, y=12,
            text="AI造成结构性压力",
            showarrow=True, arrowhead=2, ax=0, ay=-30,
            font=dict(color=COLOR["warning"], size=12)
        )
    
    fig1.update_layout(
        xaxis_title="失业率 U (%)",
        yaxis_title="职位空缺率 V (%)",
        template="plotly_white", height=450,
        margin=dict(l=20, r=20, t=10, b=20),
        yaxis=dict(range=[0, 35]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        hovermode='x unified'
    )
    st.plotly_chart(fig1, use_container_width=True)
    
    st.caption(f"{DATA_SOURCES['beveridge']}，城镇调查失业率: {CHINA_BEVERIDGE_BASELINE['urban_unemployment']}%")

with col_diag:
    st.markdown("##### 📊 诊断结果")
    
    ai_color = "negative" if ai_risk > 50 else "neutral"
    render_metric_card("AI 冲击指数", f"{ai_risk}%", ai_color)
    render_metric_card("技能错配度", f"{mismatch:.1f}", "negative" if mismatch > 1.0 else "neutral")
    
    # 动态诊断文案
    if ai_risk > 70:
        st.error(f"🚨 **极度危险**\n\nAI大规模替代人工，贝弗里奇曲线显著外移，市场匹配效率崩塌。")
    elif mismatch > 1.0:
        st.warning("⚠️ **结构性失业**\n\n高失业与高空缺并存（U={:.1f}%, V={:.1f}%）。"
                  .format(u[len(u)//2], v[len(v)//2]))
    else:
        st.success("✅ **运行良好**\n\n市场主要为摩擦性失业。")
    
    if "技能重塑补贴(Reskilling)" in policy:
        st.info("✅ **新质生产力 · 技能重塑**\n\n补贴降低了结构性错配，曲线正向原点回归。")
        render_policy_tag("符合国家「新质生产力」战略", "green")
    
    if "最低工资调整" in policy:
        st.warning("⚠️ **最低工资副作用**\n\n可能降低低技能劳动力需求")
    
    if "失业救济金" in policy:
        st.info("ℹ️ **救济金效应**\n\n提供社会安全网，但需注意保留工资上升")

st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 模块二：政策组合报告
# ==========================================
st.markdown('<div class="card">', unsafe_allow_html=True)
render_card_header("📊 政策组合效果报告", color=COLOR["macro"], dark_color="#4c1d95")

if not policy:
    st.warning("⚠️ 当前未实施任何干预政策，市场处于自然演化状态。")
    st.markdown("""
    > 💡 **建议**：在上方政策工具箱中选择至少一项政策进行干预实验。
    > 推荐从「技能重塑补贴」开始——这是应对AI冲击最有效的供给侧政策。
    """)
else:
    for p in policy:
        if p == "最低工资调整":
            st.markdown(f"""
            **📌 最低工资调整**
            - ✅ 保障了低收入者基本生活
            - ⚠️ 可能导致低技能劳动力需求沿D曲线收缩
            - 📖 理论依据：最低工资的就业效应（Card & Krueger, 1994）
            """)
        elif p == "技能重塑补贴(Reskilling)":
            st.markdown(f"""
            **🚀 技能重塑补贴**
            - ✅ 降低结构性错配，应对AI冲击最有效的长期手段
            - 🏛️ 符合国家「新质生产力」战略——以劳动者技能升级驱动高质量发展
            - 📖 政策方向：人社部「十四五」职业技能培训规划
            """)
            st.markdown("""
            <div style="background: linear-gradient(135deg, #f3e8ff 0%, #ede9fe 100%); border: 1px solid #8b5cf6; border-radius: 8px; padding: 12px; margin: 10px 0;">
            <strong>🏛️ 课程思政 · 新质生产力</strong><br>
            <span style="font-size:14px;">2024年政府工作报告提出加快发展「新质生产力」。
            其核心要义之一就是劳动者素质的全面提升——从"人口红利"转向"人才红利"。
            技能重塑补贴正是这一国家战略在劳动力市场政策中的具体体现：
            通过投资人力资本，使劳动者从被AI替代的岗位转向AI难以替代的高技能岗位。</span>
            </div>
            """, unsafe_allow_html=True)
        elif p == "失业救济金":
            st.markdown(f"""
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
render_card_header("📝 实验报告生成", color=COLOR["macro"], dark_color="#4c1d95")

params = {
    "AI替代冲击": f"{ai_risk}%",
    "技能错配指数": f"{mismatch:.1f}",
    "实施政策": ", ".join(policy) if policy else "无",
}

analysis_text = f"""
### 1. 结构性失业诊断
本次实验模拟了 **{ai_risk}%** 的AI技术替代冲击。
{ '在极端AI冲击下，贝弗里奇曲线剧烈右上方移动，旧技能劳动者被大规模淘汰，新岗位招不到人。' if ai_risk > 70 else 'AI冲击尚在可控范围内，市场保持相对平衡。'}

### 2. 政策干预效果
本次采用政策组合：{'、'.join(policy) if policy else '未实施任何干预'}。
{ '技能重塑补贴有效促进了劳动力技能升级，使贝弗里奇曲线向原点回归，缓解了AI带来的结构性冲击。这体现了新质生产力战略中"人才红利"的核心逻辑。' if '技能重塑补贴(Reskilling)' in policy else '缺乏针对性培训政策，结构性错配难以在短期内自动修复。'}
"""

results_pack = {
    "analysis": analysis_text,
    "reflection_questions": """
1. 为什么单纯提高最低工资对AI冲击的结构性失业效果有限？这与周期性问题有何不同？
2. 技能重塑补贴需要财政支出。请从成本-收益角度分析：投资于技能重塑 vs 发放失业救济金，哪个更可持续？
3. "新质生产力"战略中，高校教育应如何调整培养方案来应对AI时代的劳动力需求变化？
""",
    "ideology_text": f"""
{'本次实验中的技能重塑补贴政策，体现了国家「新质生产力」战略在劳动力市场领域的实践路径：'
 '通过投资人力资本，推动劳动者从低技能、易被替代的岗位向高技能、AI互补的岗位转型。'
 '这不仅是经济效率问题，更是社会公平问题——避免技术鸿沟扩大社会分化。'
 if '技能重塑补贴(Reskilling)' in policy else '本次实验未启用技能重塑政策。建议在后续实验中尝试，观察供给侧干预如何体现新质生产力的人才战略。'}""",
    "conclusion": "技术冲击引发的结构性失业，单纯需求侧刺激效果有限，必须配合供给侧技能重塑政策。新质生产力战略的人才培养逻辑为本实验提供了政策理论基础。"
}

report_text = generate_lab_report("macro", params, results_pack)
generate_report_download(report_text, "Macro_Lab")
st.markdown('</div>', unsafe_allow_html=True)
