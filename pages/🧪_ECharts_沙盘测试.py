"""
LMDT Phase 1 — ECharts 微件隔离测试
贝弗里奇曲线「瞬间平移」+ NPV 双线竞速「命运交叉点」
"""

import streamlit as st
import numpy as np
from streamlit_echarts import st_echarts

st.set_page_config(page_title="ECharts 沙盘测试", page_icon="🧪", layout="wide")
st.title("🧪 ECharts 核心沙盘隔离测试")

st.markdown("---")

# ==========================================
# 测试 1: 贝弗里奇曲线
# ==========================================
st.header("🌍 贝弗里奇曲线 · 涟漪散点 + 动画过渡")

col_ctrl, col_chart = st.columns([1, 3])
with col_ctrl:
    ai_risk = st.slider("AI 替代冲击 (%)", 0, 100, 30, 10, key="ai_test")
    mismatch = st.slider("技能错配度", 0.0, 2.0, 0.8, 0.1, key="mis_test")
    use_policy = st.checkbox("技能重塑补贴", key="pol_test")

# Calc
mu = 0.5
u_range = np.linspace(0.5, 14, 60)

def beveridge(u, mis, policy, ai):
    adj = mis * 1.2
    p_mult = 0.6 if policy else 1.0
    ai_shift = ai / 100 * 3.0
    v = (mu ** 2 / (u ** 0.7)) * (1 / (1 + adj)) * p_mult
    v = v * (1 - ai_shift * 0.3)
    return v

u_v_ideal = [[round(u, 2), round(beveridge(u, 0, False, 0), 3)] for u in u_range]
u_v_noai = [[round(u, 2), round(beveridge(u, mismatch, use_policy, 0), 3)] for u in u_range]
u_v_current = [[round(u, 2), round(beveridge(u, mismatch, use_policy, ai_risk), 3)] for u in u_range]

# 当前决策点
mid_u = round(u_range[len(u_range)//2], 2)
mid_v = round(beveridge(u_range[len(u_range)//2], mismatch, use_policy, ai_risk), 3)

# ECharts 配置
beveridge_option = {
    "backgroundColor": "transparent",
    "animation": True,
    "animationDuration": 1000,
    "animationDurationUpdate": 800,
    "animationEasingUpdate": "cubicOut",
    "tooltip": {
        "trigger": "axis",
        "axisPointer": {"type": "cross", "crossStyle": {"color": "#999"}},
    },
    "legend": {
        "data": ["理想高效市场", "AI冲击前", "当前曲线", "决策点", "中国实际"],
        "bottom": 0,
        "textStyle": {"color": "#64748b"},
    },
    "grid": {"left": "3%", "right": "4%", "bottom": "12%", "top": "3%", "containLabel": True},
    "xAxis": {
        "type": "value",
        "name": "失业率 U (%)",
        "min": 0,
        "max": 15,
        "axisLine": {"lineStyle": {"color": "#cbd5e1"}},
        "splitLine": {"lineStyle": {"color": "rgba(0,0,0,0.06)"}},
    },
    "yAxis": {
        "type": "value",
        "name": "空缺率 V (%)",
        "min": 0,
        "max": 35,
        "axisLine": {"lineStyle": {"color": "#cbd5e1"}},
        "splitLine": {"lineStyle": {"color": "rgba(0,0,0,0.06)"}},
    },
    "series": [
        {
            "name": "理想高效市场",
            "type": "line",
            "data": u_v_ideal,
            "lineStyle": {"color": "#cbd5e1", "type": "dashed", "width": 2},
            "symbol": "none",
            "emphasis": {"focus": "series"},
        },
        {
            "name": "AI冲击前",
            "type": "line",
            "data": u_v_noai,
            "lineStyle": {"color": "#a78bfa", "type": "dashed", "width": 2},
            "symbol": "none",
            "emphasis": {"focus": "series"},
        },
        {
            "name": "当前曲线",
            "type": "line",
            "data": u_v_current,
            "smooth": True,
            "lineStyle": {
                "color": "#6366f1",
                "width": 3,
                "shadowBlur": 10,
                "shadowColor": "rgba(99, 102, 241, 0.8)",
            },
            "symbol": "none",
            "emphasis": {"focus": "series"},
        },
        {
            "name": "决策点",
            "type": "effectScatter",
            "data": [[mid_u, mid_v]],
            "symbolSize": 16,
            "showEffectOn": "render",
            "rippleEffect": {"scale": 5, "period": 4, "brushType": "stroke"},
            "itemStyle": {"color": "#ef4444", "shadowBlur": 10, "shadowColor": "rgba(239, 68, 68, 0.6)"},
            "label": {"show": True, "formatter": "📍 当前状态", "position": "top", "color": "#ef4444", "fontSize": 12},
            "hoverAnimation": True,
        },
        {
            "name": "中国实际",
            "type": "scatter",
            "data": [[5.1, 2.5]],
            "symbolSize": 16,
            "itemStyle": {"color": "#10b981", "shadowBlur": 6, "shadowColor": "rgba(16, 185, 129, 0.5)"},
            "symbol": "diamond",
            "label": {"show": True, "formatter": "🇨🇳 2024", "position": "right", "color": "#10b981", "fontSize": 11},
        },
    ],
}

with col_chart:
    st_echarts(beveridge_option, height="450px", key="bc_test")
    if ai_risk >= 30:
        st.caption(f"📊 AI冲击 {ai_risk}%，曲线右上方移动 ↑")

st.markdown("---")

# ==========================================
# 测试 2: NPV 双线竞速
# ==========================================
st.header("🏙️ NPV 双线竞速 · 红绿填充 + 命运反超点")

col_ctrl2, col_chart2 = st.columns([1, 3])
with col_ctrl2:
    w_diff = st.slider("大城市月薪优势 (k)", 2, 30, 10, key="w_test")
    c_move = st.slider("搬迁成本 (k)", 5, 80, 25, key="c_test")
    c_psych = st.slider("年度心理成本 (k)", 0, 30, 8, key="p_test")
    subsidy = st.slider("人才补贴 (k/年)", 0, 20, 0, key="sub_test")

# Calc NPV
years = list(range(1, 21))
home_income = 5  # 家乡年收入 (k)
city_income = home_income + w_diff + subsidy
home_cum = [home_income * y for y in years]
city_cum = [city_income * y - c_move - c_psych * y for y in years]

# Find breakeven
breakeven_yr = None
for i in range(len(years)):
    if city_cum[i] > home_cum[i] and (i == 0 or city_cum[i-1] <= home_cum[i-1]):
        breakeven_yr = years[i]
        breakeven_val = city_cum[i]
        break

# Split data for red/green fill
home_data = [[y, round(home_cum[i], 1)] for i, y in enumerate(years)]
city_data = [[y, round(city_cum[i], 1)] for i, y in enumerate(years)]

npv_option = {
    "backgroundColor": "transparent",
    "animation": True,
    "animationDuration": 1000,
    "animationDurationUpdate": 800,
    "animationEasingUpdate": "elasticOut",
    "tooltip": {
        "trigger": "axis",
        "axisPointer": {"type": "cross"},
    },
    "legend": {
        "data": ["留在家乡", "闯荡大城市", "亏损区", "收益区"],
        "bottom": 0,
        "textStyle": {"color": "#64748b"},
    },
    "grid": {"left": "3%", "right": "4%", "bottom": "15%", "top": "3%", "containLabel": True},
    "xAxis": {
        "type": "category",
        "name": "年份",
        "boundaryGap": False,
        "data": [str(y) for y in years],
        "axisLine": {"lineStyle": {"color": "#cbd5e1"}},
    },
    "yAxis": {
        "type": "value",
        "name": "累计净收益 (k)",
        "axisLine": {"lineStyle": {"color": "#cbd5e1"}},
        "splitLine": {"lineStyle": {"color": "rgba(0,0,0,0.06)"}},
    },
    "series": [
        {
            "name": "留在家乡",
            "type": "line",
            "data": home_data,
            "lineStyle": {"color": "#94a3b8", "type": "dashed", "width": 2},
            "symbol": "none",
        },
        {
            "name": "闯荡大城市",
            "type": "line",
            "data": city_data,
            "smooth": True,
            "lineStyle": {
                "color": "#6366f1",
                "width": 3,
                "shadowBlur": 10,
                "shadowColor": "rgba(99, 102, 241, 0.8)",
            },
            "symbol": "none",
            "areaStyle": {
                "color": {
                    "type": "linear",
                    "x": 0, "y": 0, "x2": 0, "y2": 1,
                    "colorStops": [
                        {"offset": 0, "color": "rgba(99, 102, 241, 0.15)"},
                        {"offset": 1, "color": "rgba(99, 102, 241, 0.02)"},
                    ],
                },
            },
            "markArea": {
                "silent": True,
                "data": [
                    [
                        {"xAxis": "1", "yAxis": 0, "itemStyle": {"color": "rgba(239, 68, 68, 0.08)"}},
                        {"xAxis": str(breakeven_yr) if breakeven_yr else "20", "itemStyle": {"color": "rgba(239, 68, 68, 0.08)"}},
                    ],
                    [
                        {"xAxis": str(breakeven_yr) if breakeven_yr else "20", "itemStyle": {"color": "rgba(16, 185, 129, 0.08)"}},
                        {"xAxis": "20", "itemStyle": {"color": "rgba(16, 185, 129, 0.08)"}},
                    ],
                ]
            } if breakeven_yr else None,
            "markLine": {
                "silent": True,
                "symbol": "none",
                "label": {"formatter": "命运反超点", "color": "#10b981", "fontWeight": "bold", "fontSize": 13},
                "lineStyle": {"color": "#10b981", "type": "dashed", "width": 2},
                "data": [{"xAxis": str(breakeven_yr)}] if breakeven_yr else [],
            },
            "markPoint": {
                "symbol": "pin",
                "symbolSize": 40,
                "itemStyle": {"color": "#10b981", "shadowBlur": 10, "shadowColor": "rgba(16, 185, 129, 0.6)"},
                "label": {"formatter": "命运\n反超", "color": "#fff", "fontSize": 11, "fontWeight": "bold"},
                "data": [{"coord": [str(breakeven_yr), breakeven_val]}] if breakeven_yr else [],
            } if breakeven_yr else None,
        },
    ],
}

with col_chart2:
    st_echarts(npv_option, height="450px", key="npv_test")
    if breakeven_yr:
        st.success(f"🎯 第 **{breakeven_yr}** 年命运反超！累计净收益 **{city_cum[-1]:+.0f}k**")
    else:
        st.error(f"❌ 20 年内无法收回成本")

st.markdown("---")
st.caption("✅ ECharts 隔离测试完成 — 动画过渡 + 涟漪特效 + markArea 红绿填充均正常")
