"""
企业市场实验室 — CES派生需求 + 薪酬设计 + 挑战模式
CES函数、图表标注、预测验证
"""

import streamlit as st
import numpy as np
import plotly.graph_objects as go
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from shared import (
    COLOR, SHARED_CSS,
    render_page_banner, render_card_header,
    render_challenge_card, render_predict_gate,
    calc_derived_demand, calc_ces_demand,
    generate_lab_report, generate_report_download,
)

st.set_page_config(page_title="企业市场实验室", page_icon="🏭", layout="wide")
st.markdown(SHARED_CSS(), unsafe_allow_html=True)

render_page_banner("🏭", "企业市场实验室", "Market Lab", "green")

# ==========================================
# 侧边栏 — 仅保留全局重置 + 导航
# ==========================================
with st.sidebar:
    st.header("⚙️ 全局控制")
    
    def _reset_market():
        for key in list(st.session_state.keys()):
            if key.startswith(("cap_", "price_", "tech_", "sigma_", "pay_", "market_")):
                del st.session_state[key]
    
    st.button("🔄 重置所有参数", use_container_width=True, on_click=_reset_market)
    st.divider()
    st.page_link("🏠_综合门户首页.py", label="🏠 返回门户", use_container_width=True)
    st.divider()
    st.markdown("##### 📎 深度模块")
    st.page_link("pages/2b_🏗️_要素配置沙盘.py", label="🏗️ 要素配置沙盘 (替代vs规模效应) →", use_container_width=True)

# ==========================================
# 模型选择（移到主区域）
# ==========================================
use_ces = st.toggle("🧪 启用CES高级模型", value=False,
                    help="关闭使用简单反比模型，开启使用CES（替代弹性可调）")

# ==========================================
# 挑战模式
# ==========================================
render_challenge_card(
    title="最优雇佣决策",
    description="资本存量设为 <b style='color:#2563eb;'>60</b>，产品价格 <b style='color:#2563eb;'>2.0</b>，劳动替代型技术。找到使企业雇佣 <b style='color:#10b981;'>50人</b> 的工资率。提示：观察需求曲线的反函数。",
    theme="green"
)
with st.expander("📋 更多挑战", expanded=False):
    st.markdown("##### 💰 效率工资之谜")
    st.caption("为什么企业愿意支付高于市场出清的工资？调整薪酬模式为「效率工资」，解释其理论逻辑。")

# 挑战模式约束
if "market_attempts" not in st.session_state:
    st.session_state.market_attempts = 3
    st.session_state.market_budget = 100

with st.expander("🎯 挑战规则", expanded=True):
    c1, c2 = st.columns(2)
    with c1:
        st.metric("剩余尝试次数", st.session_state.market_attempts)
    with c2:
        st.metric("剩余运营预算", f"{st.session_state.market_budget} 亿")

# ==========================================
# 模块一：派生需求
# ==========================================
st.markdown('<div class="card">', unsafe_allow_html=True)
render_card_header("📉 希克斯-马歇尔派生需求仿真", color=COLOR["market"], dark_color="#065f46")

# 预测-验证
gate_unlocked = render_predict_gate(
    question="**当技术进步为「劳动替代型」时，劳动需求曲线会如何变化？**",
    options=["A. 向右平移（需求增加）", "B. 向左平移（需求减少）", "C. 斜率变化但位置不变"],
    var_name="market_dd"
)
if gate_unlocked:
    user_ans = st.session_state.get("market_dd_answer", "")
    if "B" in user_ans:
        st.success("✅ 预测正确！劳动替代型技术减少劳动力需求，曲线左移。")
    else:
        st.info("📚 让我们看看实验结果——")
else:
    st.stop()

# 参数
st.markdown("**📌 调节实验参数**")
if use_ces:
    c_cap, c_price, c_tech, c_sigma = st.columns(4)
    with c_cap:
        capital = st.slider("资本存量 (K)", 10, 100, 50, key="cap_main")
    with c_price:
        prod_price = st.slider("产品价格指数 (P)", 1.0, 5.0, 2.0, 0.1, key="price_main")
    with c_tech:
        tech_type = st.selectbox("技术进步类型", ["中性技术", "劳动替代型", "劳动互补型"], key="tech_main")
    with c_sigma:
        sigma = st.slider("替代弹性 σ", 0.3, 3.0, 1.0, 0.1,
                         help="σ>1: 资本与劳动易替代；σ<1: 互补性强", key="sigma_main")
else:
    c_cap, c_price, c_tech = st.columns(3)
    with c_cap:
        capital = st.slider("资本存量 (K)", 10, 100, 50, key="cap_main2")
    with c_price:
        prod_price = st.slider("产品价格指数 (P)", 1.0, 5.0, 2.0, 0.1, key="price_main2")
    with c_tech:
        tech_type = st.selectbox("技术进步类型", ["中性技术", "劳动替代型", "劳动互补型"], key="tech_main2")
    sigma = 1.0

col_chart, col_info = st.columns([3, 1])

with col_chart:
    # CES 或简单模型计算
    if use_ces:
        L_demand, w_inv = calc_ces_demand(capital, sigma, prod_price)
        w_range_for_d = np.linspace(5, 100, 80)
    else:
        w_range_for_d, L_demand = calc_derived_demand(capital, tech_type, prod_price)
        w_inv = w_range_for_d
    
    fig1 = go.Figure()
    
    # 基准线（中性技术 + K=50）
    if tech_type != "中性技术" or capital != 50:
        w_ref, d_ref = calc_derived_demand(50, "中性技术", 2.0)
        fig1.add_trace(go.Scatter(
            x=d_ref, y=w_ref,
            mode='lines', name='基准 (中性技术, K=50)',
            line=dict(color='#cbd5e1', dash='dash', width=2),
            hovertemplate='雇佣: %{x:.0f}<br>工资: %{y:.1f}<br>基准线<extra></extra>'
        ))
    
    fig1.add_trace(go.Scatter(
        x=L_demand, y=w_inv,
        mode='lines', name=f'当前需求 ({"CES σ="+str(sigma) if use_ces else tech_type})',
        line=dict(color=COLOR["market"], width=4),
        hovertemplate='<b>雇佣人数: %{x:.0f}</b><br>工资率: %{y:.1f}<br>💡 工资越高，需求越少<extra></extra>'
    ))
    
    # 标注中点（近似均衡）
    mid = len(L_demand) // 2
    fig1.add_trace(go.Scatter(
        x=[L_demand[mid]], y=[w_inv[mid]],
        mode='markers', name='参考均衡',
        marker=dict(size=14, color=COLOR["success"], symbol='circle', line=dict(width=2, color='white')),
        hovertemplate=f'🔴 参考均衡点<br>W={w_inv[mid]:.1f}, L={L_demand[mid]:.0f}<extra></extra>'
    ))
    
    fig1.update_layout(
        xaxis_title="雇佣人数 (L)", yaxis_title="工资率 (W)",
        template="plotly_white", height=430,
        margin=dict(l=20, r=20, t=10, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        hovermode='x unified'
    )
    st.plotly_chart(fig1, use_container_width=True)

with col_info:
    st.markdown("##### 📊 关键参数")
    st.metric("资本存量", str(capital))
    st.metric("替代弹性 σ", f"{sigma:.1f}" if use_ces else "N/A (简单模型)")
    
    if tech_type == "劳动替代型":
        st.error("📉 **预警**\n\n机器正在替代人工，需求曲线左移。")
        st.metric("需求状态", "收缩", delta_color="inverse")
    elif tech_type == "劳动互补型":
        st.success("📈 **繁荣**\n\n技术进步增加劳动边际产出。")
        st.metric("需求状态", "扩张", delta_color="normal")
    else:
        st.info("⚖️ **平稳**\n\n技术对劳动需求无显著偏向。")
        st.metric("需求状态", "中性", delta_color="off")

st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 模块二：薪酬制度
# ==========================================
st.markdown('<div class="card">', unsafe_allow_html=True)
render_card_header("💰 薪酬激励制度设计", color=COLOR["market"], dark_color="#065f46")

pay_mode = st.radio("薪酬制度选择：",
                    ["计时工资", "计件工资", "效率工资"],
                    horizontal=True, key="pay_main",
                    help="效率工资：企业支付高于市场出清水平的工资以减少偷懒和流失")

if pay_mode == "效率工资":
    st.info("""
    ### 📘 知识点：效率工资 (Efficiency Wage)
    
    **理论基础**（Solow Condition）：企业支付高于市场出清水平的工资，因为：
    1. **减少偷懒** — 被解雇的代价更高，员工努力程度↑
    2. **降低流失率** — 减少招聘培训成本
    3. **吸引高质量劳动力** — 逆向选择问题的解决
    4. **改善员工健康** — 营养→生产率→更高工资的良性循环
    
    **政策含义**：最低工资制度可能不必然导致失业增加——当最低工资迫使企业支付"效率工资"时，生产率提升可能抵消成本。
    """)
else:
    st.write(f"当前选择：**{pay_mode}**")
    if pay_mode == "计时工资":
        st.caption("工资基于工作时间，适用于产出难以量化的工作。监督成本高时可能引发偷懒。")
    else:
        st.caption("工资基于产量，激励强但可能导致质量下降。适用于产出可精确衡量的岗位。")

st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 实验报告
# ==========================================
st.markdown('<div class="card">', unsafe_allow_html=True)
render_card_header("📝 实验报告生成", color=COLOR["market"], dark_color="#065f46")

params = {
    "资本存量": f"{capital}",
    "产品价格": f"{prod_price}",
    "技术类型": tech_type,
    "模型选择": f"CES(σ={sigma})" if use_ces else "简单反比模型",
    "薪酬模式": pay_mode,
}

analysis_text = f"""
### 1. 派生需求分析
{"使用CES生产函数（替代弹性σ=" + str(sigma) + "）模拟企业劳动需求。" if use_ces else "使用希克斯-马歇尔派生需求定理模拟。"}
{f'{tech_type}使劳动需求显著外移，表明该技术与劳动呈互补关系。' if tech_type == '劳动互补型' else f'{tech_type}对劳动产生明显替代效应，需求收缩。' if tech_type == '劳动替代型' else '技术进步中性，未产生偏向性影响。'}

### 2. 薪酬制度设计
选择**{pay_mode}**模式。
{f'效率工资有助于解决信息不对称，但增加显性薪酬成本。可能的净效果取决于生产率弹性和监测成本。' if pay_mode == '效率工资' else '计时/计件工资更依赖监督成本或产出可观测性。'}
"""

results_pack = {
    "analysis": analysis_text,
    "reflection_questions": """
1. 当替代弹性 σ > 1 时，资本价格下降对劳动需求有何影响？与 σ < 1 时的结果有何不同？
2. 效率工资理论如何解释"同工不同酬"现象？这与歧视有什么区别？
3. 假设你是一家制造企业的HR总监，面对AI自动化浪潮，你会如何调整薪酬策略？
""",
    "conclusion": f"验证了希克斯-马歇尔派生需求定理{'及其CES扩展' if use_ces else ''}，证明技术进步方向是决定劳动力需求弹性的关键变量。"
}

report_text = generate_lab_report("market", params, results_pack)
generate_report_download(report_text, "Market_Lab")
st.markdown('</div>', unsafe_allow_html=True)

with st.expander("📐 底层参数校准说明 (Methodology)", expanded=False):
    st.markdown("""
### CES 生产函数与要素配置参数校准

| 参数 | 校准依据 | 来源 |
|------|---------|------|
| CES 替代弹性 σ (默认 0.8) | 中国制造业资本-劳动替代弹性实证估计 | 陈诗一 (2011) 《经济研究》；白重恩等 (2008) |
| Cobb-Douglas α (默认 0.3) | 资本收入份额 ≈ 30% | 中国投入产出表 + 国民经济核算 |
| 稳岗补贴降幅 30% | 疫情期间社保减免幅度（企业端实际成本降幅） | 人社部发〔2020〕11号 + 各地实施细则 |
| 机器人年租金 20 万 | 工业机器人全生命周期年化成本（含维护） | IFR《世界机器人报告 2024》 |

### 学术参考
- 陈诗一 (2011). "中国工业分行业统计数据估算: 1980-2008." 《经济学(季刊)》.
- 白重恩, 钱震杰, 武康平 (2008). "中国工业部门要素分配份额决定因素研究." 《经济研究》.
- Klump, R., McAdam, P. & Willman, A. (2007). "Factor Substitution and Factor-Augmenting Technical Progress in the US." *REStat*.
- IFR (2024). *World Robotics Report*.
    """)
