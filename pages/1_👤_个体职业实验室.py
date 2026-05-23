"""
个体职业实验室 — 工资画像 + 流动决策 + 收入/替代效应入口
国赛优化版：参数靠图、图表标注、真实数据基准、挑战模式、预测验证、乡村振兴
"""

import streamlit as st
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from shared import (
    COLOR, SHARED_CSS,
    render_page_banner, render_metric_card, render_card_header,
    render_challenge_banner, render_predict_verify, render_policy_tag,
    calc_mincer, calc_migration_npv,
    generate_lab_report, generate_report_download,
    CHINA_WAGE_BY_EDU_2024, CHINA_MIGRANT_WAGE_2024, EDUCATION_LABELS, DATA_SOURCES,
)

# ==========================================
# 页面配置
# ==========================================
st.set_page_config(page_title="个体职业实验室", page_icon="👤", layout="wide")
st.markdown(SHARED_CSS(color=COLOR["primary_light"], dark=COLOR["primary"], light=COLOR["primary_light"]), unsafe_allow_html=True)

render_page_banner("👤", "个体职业发展实验室", "Micro Lab", "blue")

# ==========================================
# 侧边栏：全局控制
# ==========================================
with st.sidebar:
    st.header("⚙️ 全局设置")
    st.caption("核心实验参数已移至图表旁，此处为辅助功能")
    
    def _reset_micro():
        for key in list(st.session_state.keys()):
            if key.startswith(("edu_", "gen_", "spec_", "disc_", "wdiff_", "cmove_", "cpsych_", "rural_", "micro_")):
                del st.session_state[key]
    
    st.button("🔄 重置所有参数", use_container_width=True, on_click=_reset_micro)
    st.divider()
    st.markdown("##### 📎 快捷入口")
    st.page_link("pages/1b_⚖️_劳动供给决策.py", label="⚖️ 收入/替代效应分解 →", use_container_width=True)
    st.page_link("🏠_综合门户首页.py", label="🏠 返回门户", use_container_width=True)

# ==========================================
# 挑战模式
# ==========================================
render_challenge_banner("micro", [
    ("🎓", "教育投资回报最大化", "在歧视系数为0%的情况下，找到使起薪溢价最高的受教育年限组合"),
    ("🌾", "乡村振兴返乡决策", "调整城乡工资差和心理成本，找到一个「返乡优于进城」的参数组合，并开启乡村振兴补贴观察变化"),
])

# ==========================================
# 模块一：人力资本工资画像
# ==========================================
st.markdown('<div class="card">', unsafe_allow_html=True)
render_card_header("💎 模块一：职业生涯工资画像 (Wage-Age Profile)", color=COLOR["primary_light"], dark_color=COLOR["primary"])

# 预测-验证
pred_done, pred_correct, pred_answer = render_predict_verify(
    question="增加「特殊培训投入」，你认为整条工资曲线会如何变化？",
    options=["A. 整体向上平移", "B. 斜率变陡（前期低后期高）", "C. 没有变化"],
    correct_answer="B. 斜率变陡（前期低后期高）",
    var_name="micro_wp"
)

# 实验参数（在图表旁）
st.markdown("**📌 调节实验参数**")
c_edu, c_gen, c_spec, c_disc = st.columns(4)
with c_edu:
    edu = st.slider("受教育年限", 9, 22, 16, help="9=初中, 12=高中, 16=本科, 19=硕士, 22=博士", key="edu_main")
with c_gen:
    gen_t = st.slider("一般培训投入", 0, 10, 5, help="可迁移技能（如沟通、管理）", key="gen_main")
with c_spec:
    spec_t = st.slider("特殊培训投入", 0, 10, 3, help="企业专属技能，前期降低工资曲线", key="spec_main")
with c_disc:
    disc = st.slider("市场歧视程度 (%)", 0, 40, 15, help="非生产率因素的工资减损", key="disc_main")

# 计算
exp_vec = np.linspace(0, 40, 100)
w_base, _ = calc_mincer(12, exp_vec, 0, 0, 0)
w_exp, w_disc = calc_mincer(edu, exp_vec, gen_t, spec_t, disc)

# 真实数据基准
real_wage = CHINA_WAGE_BY_EDU_2024.get(edu)
edu_label = EDUCATION_LABELS.get(edu, f"{edu}年")

col_chart, col_metrics = st.columns([3, 1])

with col_chart:
    fig1 = go.Figure()
    
    # 对照组
    fig1.add_trace(go.Scatter(
        x=exp_vec, y=w_base, name='对照组 (高中)',
        line=dict(color='#cbd5e1', dash='dash', width=2),
        hovertemplate='工龄: %{x}年<br>工资: %{y:.1f}<br>对照组 (高中)<extra></extra>'
    ))
    
    # 实验组
    fig1.add_trace(go.Scatter(
        x=exp_vec, y=w_exp, name=f'实验组 ({edu_label})',
        line=dict(color=COLOR["primary_light"], width=4),
        mode='lines',
        hovertemplate='工龄: %{x}年<br>工资: %{y:.1f}<br>💡 教育投资提升了整条工资曲线<br>实验组 ({edu_label})<extra></extra>'
    ))
    
    # 歧视后工资
    if disc > 0:
        fig1.add_trace(go.Scatter(
            x=exp_vec, y=w_disc, name=f'歧视后 ({disc}%)',
            line=dict(color=COLOR["danger"], width=2, dash='dot'),
            hovertemplate='工龄: %{x}年<br>工资: %{y:.1f}<br>⚠️ 歧视导致工资下降{disc}%<extra></extra>'
        ))
        # 填充歧视损失区域
        fig1.add_trace(go.Scatter(
            x=np.concatenate([exp_vec, exp_vec[::-1]]),
            y=np.concatenate([w_disc, w_exp[::-1]]),
            fill='toself', fillcolor='rgba(239, 68, 68, 0.08)',
            line=dict(width=0), hoverinfo='skip', name='歧视损失'
        ))
    
    # 峰值标注
    peak_idx = np.argmax(w_exp)
    fig1.add_trace(go.Scatter(
        x=[exp_vec[peak_idx]], y=[w_exp[peak_idx]],
        mode='markers', name='职业巅峰',
        marker=dict(size=14, color=COLOR["warning"], symbol='star', line=dict(width=2, color='white')),
        hovertemplate=f'🌟 职业巅峰<br>工龄: {exp_vec[peak_idx]:.0f}年<br>工资: {w_exp[peak_idx]:.1f}<br>💡 此时经验回报达到最高<extra></extra>'
    ))
    
    # 真实数据基准线
    if real_wage:
        fig1.add_hline(
            y=real_wage, line_dash="dash", line_color=COLOR["success"],
            annotation_text=f"2024年{edu_label}实际平均月薪 ≈{real_wage}元",
            annotation_position="bottom right",
            annotation_font=dict(size=11, color=COLOR["success"])
        )
    
    fig1.update_layout(
        xaxis_title="工龄 (Year)", yaxis_title="工资指数",
        template="plotly_white", height=400,
        margin=dict(l=20, r=20, t=10, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        hovermode='x unified'
    )
    st.plotly_chart(fig1, use_container_width=True)
    
    # 数据来源说明
    st.caption(DATA_SOURCES["wage_2024"])

with col_metrics:
    st.markdown("##### 📊 关键指标")
    render_metric_card("起薪预测", f"{w_exp[0]:.1f}", "neutral")
    
    premium = ((w_exp[20] / w_base[20]) - 1) * 100
    p_color = "positive" if premium > 0 else "negative"
    render_metric_card("教育溢价 (中期)", f"+{premium:.1f}%", p_color)
    
    if disc > 0:
        render_metric_card("歧视损失", f"-{disc}%", "negative")
    
    if real_wage:
        diff_pct = ((w_exp[0] / real_wage) - 1) * 100
        d_color = "positive" if diff_pct > 0 else "negative"
        render_metric_card(f"vs 中国{edu_label}基准", f"{diff_pct:+.1f}%", d_color)

st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 模块二：劳动力流动
# ==========================================
st.markdown('<div class="card">', unsafe_allow_html=True)
render_card_header("🚀 模块二：劳动力流动回报分析 (Migration NPV)", color=COLOR["primary_light"], dark_color=COLOR["primary"])

st.markdown("**📌 调节流动参数**")
c_wd, c_mv, c_ps, c_rural = st.columns(4)
with c_wd:
    w_diff = st.slider("城乡月薪差 (k)", 1, 30, 8, key="wdiff_main")
with c_mv:
    c_move = st.number_input("搬迁成本 (k)", 0, 100, 20, key="cmove_main")
with c_ps:
    c_psych = st.slider("心理成本 (k/年)", 0, 50, 10, key="cpsych_main")
with c_rural:
    rural_policy = st.checkbox("🌾 乡村振兴补贴", value=False, key="rural_main",
                               help="假设政府实施返乡创业补贴，每年降低心理成本5k")

# 乡村振兴政策效果
if rural_policy:
    render_policy_tag("🏡 国家乡村振兴战略 · 返乡创业补贴生效：心理成本每年降低5000元", "green")
    c_psych_eff = max(0, c_psych - 5)
else:
    c_psych_eff = c_psych

# 计算
years, npv = calc_migration_npv(5, 5 + w_diff, c_move, c_psych_eff)
breakeven = np.where(npv > 0)[0]

col_npv, col_npv_info = st.columns([3, 1])

with col_npv:
    colors_npv = [COLOR["danger"] if v < 0 else COLOR["success"] for v in npv]
    fig2 = go.Figure(go.Bar(
        x=years, y=npv, marker_color=colors_npv,
        hovertemplate='第%{x}年<br>累计NPV: %{y:.1f}k<extra></extra>',
        name='累计净收益'
    ))
    fig2.update_layout(
        xaxis_title="年份", yaxis_title="累计净收益 (k)",
        template="plotly_white", height=350,
        margin=dict(l=20, r=20, t=10, b=20)
    )
    st.plotly_chart(fig2, use_container_width=True)
    
    st.caption(f"基准线 — {DATA_SOURCES['migrant']}：2024年农民工月均收入 {CHINA_MIGRANT_WAGE_2024} 元")

with col_npv_info:
    st.markdown("##### 💡 决策建议")
    if len(breakeven) > 0:
        st.success(f"✅ **值得迁移**\n\n预计在第 **{breakeven[0]+1}** 年收回成本并开始盈利。")
        final_npv = npv[-1]
        render_metric_card("最终累计NPV", f"{final_npv:+.0f}k", "positive" if final_npv > 0 else "negative")
    else:
        st.error("❌ **不值得迁移**\n\n心理/搬迁成本过高，长期收益无法覆盖成本。")
        render_metric_card("最终累计NPV", f"{npv[-1]:+.0f}k", "negative")
    
    if rural_policy:
        # 对比无政策情况
        _, npv_no_policy = calc_migration_npv(5, 5 + w_diff, c_move, c_psych)
        delta = npv[-1] - npv_no_policy[-1]
        render_metric_card("乡村振兴政策增益", f"+{delta:.0f}k", "positive")
        st.caption("🏡 政策使返乡/留守本地更具吸引力")

# 乡村振兴政策解释
if rural_policy:
    st.markdown("""
    <div style="background:#ecfdf5; border:1px solid #10b981; border-radius:8px; padding:12px; margin-top:10px;">
    <strong>🏡 课程思政 · 乡村振兴</strong><br>
    <span style="font-size:14px;">国家乡村振兴战略通过财政补贴、创业扶持、基础设施改善等政策工具，
    有效降低了劳动力流动的心理成本和实际成本，为县域经济发展留住了人才。
    本次模拟显示，补贴使心理成本降低，让"留下来"成为更理性的经济决策。</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 实验报告
# ==========================================
st.markdown('<div class="card">', unsafe_allow_html=True)
render_card_header("📝 实验报告生成", color=COLOR["primary_light"], dark_color=COLOR["primary"])

params = {
    "受教育年限": f"{edu} 年 ({edu_label})",
    "一般培训": f"{gen_t}",
    "特殊培训": f"{spec_t}",
    "歧视系数": f"{disc}%",
    "城乡月薪差": f"{w_diff}k",
    "搬迁成本": f"{c_move}k",
    "心理成本": f"{c_psych_eff}k",
    "乡村振兴补贴": "已开启" if rural_policy else "未开启",
}

baseline_comparison = []
if real_wage:
    baseline_comparison.append({
        "label": "起薪",
        "experiment": f"{w_exp[0]:.1f}",
        "baseline": f"{real_wage} 元",
        "diff": f"{((w_exp[0] / real_wage) - 1) * 100:+.1f}%"
    })
baseline_comparison.append({
    "label": "教育溢价",
    "experiment": f"+{premium:.1f}%",
    "baseline": "约+10%~30%（中国实际）",
    "diff": "—"
})

analysis_text = f"""
### 1. 人力资本回报
根据明瑟收入方程模拟，当前教育投入下，职业中期教育溢价为 **{premium:.1f}%**。
{f'市场存在 {disc}% 的歧视系数，导致显著的非生产率工资差异。' if disc > 0 else '市场环境公平，无显著歧视损失。'}
与2024年中国{edu_label}实际平均工资（≈{real_wage}元）相比，模型预测起薪{'偏高' if premium > 0 else '偏低'}。

### 2. 劳动力流动决策
基于NPV模型，{f'迁移是理性选择，预计第{breakeven[0]+1}年盈亏平衡。' if len(breakeven) > 0 else '迁移非理性，成本无法覆盖收益。'}
{f'乡村振兴补贴政策生效后，留守本地的经济吸引力显著提升。' if rural_policy else ''}
"""

results_pack = {
    "analysis": analysis_text,
    "baseline_comparison": baseline_comparison,
    "reflection_questions": """
1. 当歧视系数从0增加到30%时，教育投资回报率如何变化？这对教育政策有何启示？
2. 为什么乡村振兴补贴降低心理成本后，原本不值得迁移的情况可能变成"返乡创业"优于"外出打工"？
3. 请对比一般培训与特殊培训对工资曲线的不同影响，并解释为什么企业不愿意为一般培训付费。
""",
    "ideology_text": f"""
{'乡村振兴战略通过降低劳动力流动成本，有效促进了城乡均衡发展。'
 '本次实验模拟了补贴政策对劳动者流动决策的影响，体现了国家政策在优化劳动力资源配置中的关键作用。'
 if rural_policy else '本次实验未开启乡村振兴政策选项。建议在后续实验中尝试开启，观察国家政策对个体职业决策的引导作用。'}""",
    "conclusion": f"验证了教育投资的边际递减规律、歧视的市场扭曲效应，{'以及乡村振兴政策对劳动力流动的积极引导作用。' if rural_policy else '以及心理成本对劳动力流动的阻碍作用。'}"
}

report_text = generate_lab_report("micro", params, results_pack)
generate_report_download(report_text, "Micro_Lab")
st.markdown('</div>', unsafe_allow_html=True)
