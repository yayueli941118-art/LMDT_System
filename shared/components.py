"""
可复用 UI 组件
Banner、卡片头部、指标卡、挑战模式、预测-验证
"""

import streamlit as st
from .config import SCHOOL_NAME, DEPARTMENT, AUTHOR_NAME, COMPETITION_INFO


def render_page_banner(icon: str, title: str, subtitle: str = "", theme: str = "blue"):
    """
    渲染实验室页面顶部 Banner
    theme: "blue" | "green" | "purple"
    """
    themes = {
        "blue": ("#1e3a8a", "#3b82f6"),
        "green": ("#065f46", "#10b981"),
        "purple": ("#4c1d95", "#8b5cf6"),
    }
    dark, light = themes.get(theme, themes["blue"])

    sub_line = ""
    if subtitle:
        sub_line = f'<div style="font-size: 16px; margin-top:5px; opacity:0.9;">{subtitle}</div>'

    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, {dark} 0%, {light} 100%);
        color: white;
        padding: 20px 30px;
        border-radius: 12px;
        margin-bottom: 25px;
        box-shadow: 0 4px 10px rgba(37, 99, 235, 0.3);
        display: flex;
        justify-content: space-between;
        align-items: center;
    ">
        <div>
            <div style="font-size: 24px; font-weight: 800;">
                {icon} {title}
                <span style="font-size:18px; opacity:0.8; font-weight:400;">({subtitle})</span>
            </div>
            {sub_line}
        </div>
        <div style="background: rgba(255,255,255,0.2); padding: 5px 15px; border-radius: 20px; font-size: 14px;">
            👩‍🏫 课程负责人：{AUTHOR_NAME}
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_card_header(title: str, color: str = "#3b82f6", dark_color: str = "#1e3a8a"):
    """渲染卡片标题"""
    return st.markdown(f"""
    <div style="
        color: {dark_color};
        font-size: 22px;
        font-weight: 700;
        margin-bottom: 15px;
        border-left: 5px solid {color};
        padding-left: 12px;
    ">{title}</div>
    """, unsafe_allow_html=True)


def render_metric_card(label: str, value, value_color: str = "neutral"):
    """
    渲染指标卡片
    value_color: "positive" | "negative" | "neutral" | 自定义CSS颜色
    """
    colors = {"positive": "#10b981", "negative": "#ef4444", "neutral": "#64748b"}
    color = colors.get(value_color, value_color)
    st.markdown(f"""
    <div style='margin-bottom:10px;'>
        <div style='font-size:16px; color:#64748b; font-weight:500;'>{label}</div>
        <div style='font-size:32px; font-weight:800; color:{color};'>{value}</div>
    </div>
    """, unsafe_allow_html=True)


def render_challenge_banner(challenge_id: str, tasks: list):
    """
    渲染挑战任务栏
    tasks: [(emoji, title, description), ...]
    """
    with st.expander(f"🎯 今日挑战任务", expanded=True):
        for i, (emoji, title, desc) in enumerate(tasks):
            st.markdown(f"##### {emoji} 任务 {i+1}：{title}")
            st.markdown(f"*{desc}*")
            if i < len(tasks) - 1:
                st.divider()


def render_predict_verify(question: str, options: list, correct_answer: str, var_name: str):
    """
    预测-验证交互组件
    
    question: 预测问题
    options: 选项列表 ["A. 增加", "B. 减少", "C. 不变"]
    correct_answer: 正确答案（需与options中的某一项完全匹配）
    var_name: session_state 变量名前缀，用于存储状态
    
    返回: (已预测, 预测是否开始, 用户答案)
    """
    predict_key = f"{var_name}_predict"
    answer_key = f"{var_name}_answer"
    done_key = f"{var_name}_done"
    
    # 初始化
    if done_key not in st.session_state:
        st.session_state[done_key] = False
    
    if not st.session_state[done_key]:
        st.markdown('<div class="predict-box">', unsafe_allow_html=True)
        st.markdown(f"##### 🔮 先预测：{question}")
        st.radio("请选择你的预测：", options, key=predict_key)
        
        def _confirm_predict():
            st.session_state[answer_key] = st.session_state[predict_key]
            st.session_state[done_key] = True
        
        st.button("✅ 确认预测，开始实验", key=f"{var_name}_confirm", on_click=_confirm_predict)
        st.markdown('</div>', unsafe_allow_html=True)
        return False, False, None
    else:
        user_answer = st.session_state.get(answer_key)
        is_correct = (user_answer == correct_answer)
        if is_correct:
            st.success(f"✅ 预测正确！你的判断「{user_answer}」与实验结果一致。")
        else:
            # 提取正确项的前几个字符作为简洁提示
            st.info(f"📚 你的预测是「{user_answer}」，实际结果是「{correct_answer}」。让我们看看为什么——")
        return True, is_correct, user_answer


def render_policy_tag(text: str, tag_type: str = "red"):
    """渲染思政/政策标签"""
    cls = "policy-tag-green" if tag_type == "green" else "policy-tag"
    st.markdown(f'<span class="{cls}">{text}</span>', unsafe_allow_html=True)
