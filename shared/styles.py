"""
共享色彩系统 & CSS 模板 — 学术极简风
全局主题由 .streamlit/config.toml 统一管控，CSS 仅做微调
"""

# ==========================================
# 语义化全局色板（严格遵循经济学/HR预警直觉）
# ==========================================
COLOR = {
    "primary": "#2563eb",        # 学术蓝
    "primary_light": "#60a5fa",
    "success": "#10b981",        # 翠绿 — 积极/效率提升/向原点回归
    "danger": "#ef4444",         # 警示红 — 贝弗里奇外移/失业飙升/福利陷阱
    "warning": "#f59e0b",        # 暖橙 — 中性/过渡
    "neutral": "#64748b",
    "bg": "#f8fafc",
    "card_bg": "#ffffff",
    "border": "#e2e8f0",
    "text_dark": "#0f172a",
    "text_light": "#64748b",
    # 各实验室主题色
    "micro": "#2563eb",
    "market": "#10b981",
    "macro": "#8b5cf6",
}

# ==========================================
# 全局轻量 CSS（不使用任何动态颜色注入，由 config.toml 统一主题）
# ==========================================
GLOBAL_CSS = """
<style>
    /* 全局 */
    .block-container { padding-top: 2.5rem !important; padding-bottom: 3rem !important; max-width: 98% !important; }
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    p, li, .stMarkdown { font-size: 15px !important; line-height: 1.7 !important; }

    /* 卡片通用 */
    .card {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 22px;
        margin-bottom: 18px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
        border: 1px solid #e2e8f0;
    }

    /* 卡片头部（左侧学术蓝色条） */
    .card-header {
        font-size: 20px;
        font-weight: 700;
        margin-bottom: 14px;
        border-left: 4px solid #2563eb;
        padding-left: 10px;
        color: #0f172a;
    }

    /* 指标值 */
    .metric-value { font-size: 28px; font-weight: 800; }
    .metric-label { font-size: 14px; color: #64748b; font-weight: 500; }
    .metric-positive { color: #10b981; }
    .metric-negative { color: #ef4444; }
    .metric-neutral { color: #64748b; }

    /* 页面 Banner（学术蓝渐变） */
    .page-banner {
        background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%);
        color: white;
        padding: 18px 28px;
        border-radius: 10px;
        margin-bottom: 22px;
        box-shadow: 0 2px 8px rgba(37, 99, 235, 0.2);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    /* 挑战任务卡 */
    .challenge-card {
        background: #f8fafc;
        border-left: 4px solid #2563eb;
        padding: 15px;
        margin-bottom: 20px;
        border-radius: 0 8px 8px 0;
    }

    /* 预测验证区域 */
    .predict-box {
        background: #eff6ff;
        border: 2px solid #2563eb;
        border-radius: 10px;
        padding: 18px;
        margin: 12px 0;
    }

    /* 思政/政策标签 */
    .policy-tag {
        display: inline-block;
        background: #2563eb;
        color: white;
        padding: 3px 10px;
        border-radius: 16px;
        font-size: 12px;
        font-weight: 600;
        margin: 2px 3px;
    }
    .policy-tag-green {
        background: #10b981;
    }
    .policy-tag-red {
        background: #ef4444;
    }
    .policy-tag-orange {
        background: #f59e0b;
    }

    /* 侧边栏 */
    section[data-testid="stSidebar"] {
        background-color: #f1f5f9 !important;
        border-right: 1px solid #e2e8f0 !important;
    }
</style>
"""


def SHARED_CSS(**kwargs) -> str:
    """向后兼容：返回全局 CSS（不再接受主题参数，由 config.toml 统一管控）"""
    return GLOBAL_CSS


CARD_CSS = "card"
PAGE_BANNER_CSS = "page-banner"
