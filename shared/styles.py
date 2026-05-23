"""
共享色彩系统 & CSS 模板
定义全局色板、卡片样式、页面Banner样式
"""

# ==========================================
# 全局色板
# ==========================================
COLOR = {
    "primary": "#1e3a8a",
    "primary_light": "#3b82f6",
    "success": "#10b981",
    "danger": "#ef4444",
    "warning": "#f59e0b",
    "neutral": "#64748b",
    "bg": "#f1f5f9",
    "card_bg": "#ffffff",
    "border": "#e2e8f0",
    "text_dark": "#0f172a",
    "text_light": "#64748b",
    # 各实验室主题色
    "micro": "#3b82f6",
    "market": "#10b981",
    "macro": "#8b5cf6",
}

# ==========================================
# 共享 CSS 模板 — 使用 __COLOR__ / __DARK__ / __LIGHT__ 占位符
# 避免与 CSS 原生花括号冲突
# ==========================================
_SHARED_CSS_TEMPLATE = """
<style>
    /* 全局字体与布局 */
    html, body, [class*="css"] {{ font-family: 'Microsoft YaHei', sans-serif !important; background-color: #f1f5f9; }}
    .block-container {{ padding-top: 3.5rem !important; padding-bottom: 5rem !important; max-width: 98% !important; }}
    
    /* 隐藏 Streamlit 默认头部 */
    header {{visibility: hidden;}}
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}

    p, li, .stMarkdown {{ font-size: 16px !important; line-height: 1.6 !important; }}

    /* ===== 卡片通用样式 ===== */
    .card {{
        background-color: #ffffff;
        border-radius: 12px;
        padding: 25px;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        border: 1px solid #e2e8f0;
        transition: all 0.3s ease;
    }}
    .card:hover {{
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
        border-color: #3b82f6;
        transform: translateY(-2px);
    }}

    /* ===== 卡片头部（带左侧色条） ===== */
    .card-header {{
        font-size: 22px;
        font-weight: 700;
        margin-bottom: 15px;
        border-left: 5px solid __COLOR__;
        padding-left: 12px;
        color: __DARK__;
    }}

    /* ===== 指标显示 ===== */
    .metric-value {{ font-size: 32px; font-weight: 800; }}
    .metric-label {{ font-size: 16px; color: #64748b; font-weight: 500; }}

    .metric-positive {{ color: #10b981; }}
    .metric-negative {{ color: #ef4444; }}
    .metric-neutral {{ color: #64748b; }}

    /* ===== 页面顶部 Banner ===== */
    .page-banner {{
        background: linear-gradient(135deg, __DARK__ 0%, __LIGHT__ 100%);
        color: white;
        padding: 20px 30px;
        border-radius: 12px;
        margin-bottom: 25px;
        box-shadow: 0 4px 10px rgba(37, 99, 235, 0.3);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }}
    
    /* ===== 挑战模式卡片 ===== */
    .challenge-card {{
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border: 2px solid #f59e0b;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
    }}
    .challenge-icon {{ font-size: 36px; display: block; margin-bottom: 8px; }}

    /* ===== 预测区域 ===== */
    .predict-box {{
        background: #eff6ff;
        border: 2px solid #3b82f6;
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
    }}

    /* ===== 思政标签 ===== */
    .policy-tag {{
        display: inline-block;
        background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 600;
        margin: 2px 4px;
    }}
    .policy-tag-green {{
        background: linear-gradient(135deg, #059669 0%, #10b981 100%);
    }}
</style>
"""


def get_lab_css(color: str, dark: str, light: str) -> str:
    """生成特定实验室的主题 CSS（安全替换，不触发format冲突）"""
    return (_SHARED_CSS_TEMPLATE
            .replace("__COLOR__", color)
            .replace("__DARK__", dark)
            .replace("__LIGHT__", light))


# 向后兼容：SHARED_CSS 是模板函数别名
def SHARED_CSS(color: str = "#3b82f6", dark: str = "#1e3a8a", light: str = "#3b82f6") -> str:
    return get_lab_css(color, dark, light)


# 兼容旧接口
CARD_CSS = "card"
PAGE_BANNER_CSS = "page-banner"
