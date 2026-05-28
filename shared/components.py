"""
可复用 UI 组件
Banner、卡片头部、指标卡、挑战模式、预测验证、任务卡
"""

import streamlit as st
from .config import SCHOOL_NAME, DEPARTMENT, AUTHOR_NAME, COMPETITION_INFO
from .styles import COLOR


def render_page_banner(icon: str, title: str, subtitle: str = "", theme: str = "blue"):
    """
    渲染实验室页面顶部 Banner
    theme: "blue" | "green" | "purple"
    """
    themes = {
        "blue": ("#1e3a8a", "#2563eb"),
        "green": ("#065f46", "#10b981"),
        "purple": ("#4c1d95", "#8b5cf6"),
    }
    dark, light = themes.get(theme, themes["blue"])

    sub_html = f'<div style="font-size:14px; margin-top:4px; opacity:0.85;">{subtitle}</div>' if subtitle else ""

    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, {dark} 0%, {light} 100%);
        color: white;
        padding: 18px 28px;
        border-radius: 10px;
        margin-bottom: 22px;
        box-shadow: 0 2px 8px rgba(37, 99, 235, 0.2);
        display: flex;
        justify-content: space-between;
        align-items: center;
    ">
        <div>
            <div style="font-size:22px; font-weight:800;">
                {icon} {title}
                {f'<span style="font-size:16px; opacity:0.8; font-weight:400;"> · {subtitle}</span>' if subtitle else ''}
            </div>
            {sub_html}
        </div>
        <div style="background: rgba(255,255,255,0.18); padding: 4px 14px; border-radius: 16px; font-size:13px;">
            👩‍🏫 {AUTHOR_NAME}
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_card_header(title: str, color: str = None, dark_color: str = None):
    """渲染卡片标题"""
    c = color or COLOR["primary"]
    st.markdown(f"""
    <div style="
        font-size: 19px;
        font-weight: 700;
        margin-bottom: 12px;
        border-left: 4px solid {c};
        padding-left: 10px;
        color: #0f172a;
    ">{title}</div>
    """, unsafe_allow_html=True)


def render_metric_card(label: str, value, value_color: str = "neutral"):
    """
    渲染指标卡片 - 已废弃，建议使用 st.metric
    """
    colors = {"positive": COLOR["success"], "negative": COLOR["danger"], "neutral": COLOR["neutral"]}
    color = colors.get(value_color, value_color)
    st.markdown(f"""
    <div style='margin-bottom:8px;'>
        <div style='font-size:14px; color:{COLOR["text_light"]}; font-weight:500;'>{label}</div>
        <div style='font-size:28px; font-weight:800; color:{color};'>{value}</div>
    </div>
    """, unsafe_allow_html=True)


def render_challenge_card(title: str, description: str, theme: str = "blue"):
    """
    渲染「市长挑战任务卡」—— 沉浸式任务描述
    
    theme: "blue" | "green" | "purple"
    """
    color_map = {
        "blue": COLOR["primary"],
        "green": COLOR["success"],
        "purple": COLOR["macro"],
    }
    border_color = color_map.get(theme, COLOR["primary"])

    st.markdown(f"""
    <div style="
        background-color: #f8fafc;
        border-left: 4px solid {border_color};
        padding: 15px 18px;
        margin-bottom: 18px;
        border-radius: 0 8px 8px 0;
    ">
        <b>🎯 挑战任务：</b>{description}
    </div>
    """, unsafe_allow_html=True)


def render_challenge_banner(challenge_id: str, tasks: list):
    """
    渲染挑战任务栏（可折叠）
    tasks: [(emoji, title, description), ...]
    """
    with st.expander("🎯 今日挑战任务", expanded=True):
        for i, (emoji, title, desc) in enumerate(tasks):
            st.markdown(f"##### {emoji} 任务 {i+1}：{title}")
            st.markdown(f"*{desc}*")
            if i < len(tasks) - 1:
                st.divider()


def render_predict_gate(question: str, options: list, var_name: str):
    """
    前测拦截 — 必须回答预测题才能继续实验
    
    question: 预测问题
    options: 选项列表
    var_name: session_state 前缀
    
    返回: True 表示已解锁（可渲染后续内容），False 表示还在等待预测
    """
    done_key = f"{var_name}_done"
    answer_key = f"{var_name}_answer"

    if done_key not in st.session_state:
        st.session_state[done_key] = False

    if not st.session_state[done_key]:
        st.markdown("""
        <div style="
            background: #eff6ff;
            border: 2px solid #2563eb;
            border-radius: 10px;
            padding: 18px;
            margin: 12px 0;
        ">
        """, unsafe_allow_html=True)
        st.markdown(f"##### 🔮 先预测，再实验")
        st.markdown(f"*在调整任何参数之前，先做一个直觉判断：*")
        st.radio(question, options, key=f"{var_name}_radio")

        col_btn, _ = st.columns([1, 3])
        with col_btn:
            if st.button("✅ 确认预测，进入实验", key=f"{var_name}_btn", use_container_width=True):
                st.session_state[answer_key] = st.session_state[f"{var_name}_radio"]
                st.session_state[done_key] = True
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        return False
    else:
        user_answer = st.session_state.get(answer_key, "")
        st.info(f"📝 你的预测：**{user_answer}** — 实验结束后看看你的直觉准不准！")
        return True


def render_policy_tag(text: str, tag_type: str = "blue"):
    """渲染思政/政策标签"""
    cls_map = {"blue": "policy-tag", "green": "policy-tag-green",
               "red": "policy-tag-red", "orange": "policy-tag-orange"}
    cls = cls_map.get(tag_type, "policy-tag")
    st.markdown(f'<span class="{cls}">{text}</span>', unsafe_allow_html=True)
