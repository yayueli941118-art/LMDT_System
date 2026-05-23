"""
📈 教师看板 — 班级学情诊断与靶向干预
支持上传学生报告(.md) → 自动解析 → 知识盲区检测 → 教学干预建议
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import re
from datetime import datetime
from collections import Counter
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from shared import COLOR, SHARED_CSS, render_page_banner, render_card_header

st.set_page_config(page_title="教师看板", page_icon="📈", layout="wide")
st.markdown(SHARED_CSS(color="#64748b", dark="#334155", light="#94a3b8"), unsafe_allow_html=True)

render_page_banner("📈", "教师看板 · 班级学情诊断", "Learning Analytics Dashboard", "blue")

# ==========================================
# 侧边栏
# ==========================================
with st.sidebar:
    st.header("📂 数据管理")
    st.markdown("""
    ### 使用说明
    1. 学生完成实验后下载报告 (.md)
    2. 批量上传至此页面
    3. 系统基于阈值规则辅助分析班级知识薄弱点
    
    ---
    ### 支持的报告类型
    - 个体职业发展仿真实验
    - 企业决策仿真实验
    - 宏观政策仿真实验
    - 劳动供给决策仿真实验
    """)
    st.page_link("🏠_综合门户首页.py", label="🏠 返回门户", use_container_width=True)

# ==========================================
# 上传与解析
# ==========================================
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown("""
<div style="display:flex; align-items:center; gap:10px; margin-bottom:15px;">
    <span style="font-size:36px;">📤</span>
    <span style="font-size:22px; font-weight:700; color:#334155;">批量上传学生实验报告</span>
</div>
""", unsafe_allow_html=True)

uploaded_files = st.file_uploader(
    "拖放或选择学生实验报告 (.md 文件)",
    type=["md", "txt"],
    accept_multiple_files=True
)

# ==========================================
# 解析引擎
# ==========================================
def parse_micro_report(content: str) -> dict:
    data = {"实验类型": "个体职业实验室"}
    for key, pat in {
        "受教育年限": r"\*\*受教育年限\*\*: (\d+)",
        "一般培训": r"\*\*一般培训\*\*: (\d+)",
        "特殊培训": r"\*\*特殊培训\*\*: (\d+)",
        "歧视系数": r"\*\*歧视系数\*\*: (\d+)%",
        "城乡月薪差": r"\*\*城乡月薪差\*\*: (\d+)",
        "乡村振兴补贴": r"\*\*乡村振兴补贴\*\*: (.+)",
    }.items():
        m = re.search(pat, content)
        if m:
            try: data[key] = int(m.group(1))
            except: data[key] = m.group(1)
    return data

def parse_market_report(content: str) -> dict:
    data = {"实验类型": "企业市场实验室"}
    for key, pat in {
        "资本存量": r"\*\*资本存量\*\*: (\d+)",
        "产品价格": r"\*\*产品价格\*\*: ([\d.]+)",
        "技术类型": r"\*\*技术类型\*\*: (.+)",
        "薪酬模式": r"\*\*薪酬模式\*\*: (.+)",
    }.items():
        m = re.search(pat, content)
        if m:
            try: data[key] = int(m.group(1))
            except:
                try: data[key] = float(m.group(1))
                except: data[key] = m.group(1)
    return data

def parse_macro_report(content: str) -> dict:
    data = {"实验类型": "宏观政策实验室"}
    for key, pat in {
        "AI替代冲击": r"\*\*AI替代冲击\*\*: (\d+)%",
        "技能错配指数": r"\*\*技能错配指数\*\*: ([\d.]+)",
        "实施政策": r"\*\*实施政策\*\*: (.+)",
    }.items():
        m = re.search(pat, content)
        if m:
            try: data[key] = int(m.group(1))
            except:
                try: data[key] = float(m.group(1))
                except: data[key] = m.group(1)
    return data

def parse_labor_supply_report(content: str) -> dict:
    data = {"实验类型": "劳动供给决策"}
    for key, pat in {
        "初始工资率": r"\*\*初始工资率\*\*: (\d+)",
        "新工资率": r"\*\*新工资率\*\*: (\d+)",
        "闲暇偏好": r"\*\*闲暇偏好 β\*\*: ([\d.]+)",
    }.items():
        m = re.search(pat, content)
        if m:
            try: data[key] = int(m.group(1))
            except:
                try: data[key] = float(m.group(1))
                except: data[key] = m.group(1)
    return data

def extract_student_name(content: str) -> str:
    m = re.search(r'\*\*学生姓名\*\*:\s*([^\n_]+)', content)
    if m:
        name = m.group(1).strip()
        if name and "___" not in name: return name
    return "(未填写)"

def extract_time(content: str) -> str:
    m = re.search(r'\*\*实验时间\*\*:\s*(\d{4}-\d{2}-\d{2}.+)', content)
    return m.group(1) if m else "未知"

# ==========================================
# 学情诊断引擎（新）
# ==========================================
# 各实验类型的知识盲区检测规则
DIAGNOSTIC_RULES = {
    "个体职业实验室": {
        "教育投资回报认知": {
            "check": lambda sub: any(
                v < 16 and "培训" not in str(sub.get("一般培训", "0"))
                for _, v in sub["受教育年限"].dropna().items()
            ) if "受教育年限" in sub.columns and len(sub) > 0 else False,
            "问题": "部分学生选择了低教育路径但未配置培训——可能低估了人力资本投资的终身回报",
            "干预": "建议在下节课展示「教育溢价时间序列图」，展示本科 vs 高中毕业生的终身收入差距（溢价倍数可达 1.5-2.5×）",
            "关联概念": ["人力资本理论", "明瑟收入方程", "教育信号假说"]
        },
        "歧视效应认知": {
            "check": lambda sub: any(v > 20 for v in sub["歧视系数"].dropna()) if "歧视系数" in sub.columns and len(sub) > 0 else False,
            "问题": "学生设置了高于 20% 的歧视系数——需确认学生是否理解歧视的福利损失",
            "干预": "建议在翻转课堂中让学生对比「歧视前 vs 歧视后」贝克尔模型图，计算歧视导致的年收入损失（歧视系数 30% → 年损失约 36k）",
            "关联概念": ["贝克尔偏好歧视模型", "统计性歧视", "拥挤假说"]
        }
    },
    "宏观政策实验室": {
        "AI冲击认知偏差": {
            "check": lambda sub: any(v > 80 for v in sub["AI替代冲击"].dropna()) if "AI替代冲击" in sub.columns and len(sub) > 0 else False,
            "问题": "学生将 AI 冲击设得过高（>80%）——可能存在「技术恐惧」偏差，低估了岗位创造效应",
            "干预": "建议重点复习「偏向性技术进步」概念：AI 替代了重复性岗位（替代效应），但也创造了AI训练师/提示工程师等新岗位（补偿效应）。推荐案例：19世纪工业革命中80%的织布工失业，但纺织业总就业量反而扩张了。",
            "关联概念": ["偏向性技术进步", "补偿效应", "创造性破坏"]
        },
        "财政政策盲区": {
            "check": lambda sub: not any("财政扩张" in str(p) for p in sub["实施政策"].dropna()) if "实施政策" in sub.columns and len(sub) > 0 and any(True for _ in sub["实施政策"]) else False,
            "问题": "班级中无一人选择财政扩张政策，可能误以为货币政策是唯一的宏观调控工具",
            "干预": "补充讲解：货币政策（降息降准）vs 财政政策（增支减税）各自的适用场景和时滞——经济衰退时财政政策往往比货币政策更有效（流动性陷阱）",
            "关联概念": ["流动性陷阱", "挤出效应", "自动稳定器"]
        }
    },
    "劳动供给决策": {
        "收入效应盲区": {
            "check": lambda sub: True,  # 总是需要检查
            "问题": "收入效应是劳动经济学中最容易被忽略的概念——多数学生只关注替代效应（工资涨→多工作）",
            "干预": "建议用「中彩票」作为极端案例：为什么中彩票的人会选择减少工作时间？因为收入效应完全压倒了替代效应。引导学生对比自己的仿真结果，找出生效拐点。",
            "关联概念": ["向后弯曲的劳动供给曲线", "收入效应", "替代效应", "希克斯分解"]
        }
    }
}

def diagnose_class(sub: pd.DataFrame, lab_type: str) -> list:
    """对某类实验的子集进行学情诊断"""
    diagnoses = []
    rules = DIAGNOSTIC_RULES.get(lab_type, {})
    for name, rule in rules.items():
        try:
            if rule["check"](sub):
                diagnoses.append({
                    "检测项": name,
                    "问题描述": rule["问题"],
                    "靶向干预": rule["干预"],
                    "关联概念": ", ".join(rule.get("关联概念", [])),
                    "受影响学生比例": f"{len(sub)} 份报告中检测到此模式"
                })
        except:
            pass
    return diagnoses

# 解析所有文件
all_data = []
if uploaded_files:
    for f in uploaded_files:
        content = f.read().decode("utf-8", errors="ignore")
        student = extract_student_name(content)
        time_str = extract_time(content)
        
        if "个体职业" in content:
            parsed = parse_micro_report(content)
        elif "企业决策" in content:
            parsed = parse_market_report(content)
        elif "宏观政策" in content:
            parsed = parse_macro_report(content)
        elif "劳动供给" in content:
            parsed = parse_labor_supply_report(content)
        else:
            parsed = {"实验类型": "无法识别"}
        
        parsed["学生姓名"] = student
        parsed["实验时间"] = time_str
        parsed["文件名"] = f.name
        all_data.append(parsed)

st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 汇总 + 诊断
# ==========================================
if all_data:
    df = pd.DataFrame(all_data)
    
    # ========== 概览卡片 ==========
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<span style="font-size:22px; font-weight:700; color:#334155;">📊 班级概览</span>', unsafe_allow_html=True)
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("上传报告数", len(all_data))
    with c2:
        types = df["实验类型"].value_counts()
        st.metric("实验类型数", len(types))
    with c3:
        filled = sum(1 for n in df["学生姓名"] if n != "(未填写)")
        st.metric("已署名", f"{filled}/{len(all_data)}")
    with c4:
        st.metric("主要实验", types.index[0] if len(types) > 0 else "—")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ========== ⚡ 阈值预警面板（基于数据的可视化辅助分析） ==========
    st.markdown('<div class="card" style="border: 2px solid #f59e0b;">', unsafe_allow_html=True)
    st.markdown('<span style="font-size:20px; font-weight:700; color:#d97706;">⚡ 阈值预警面板</span>', unsafe_allow_html=True)
    st.caption('基于预设教学阈值的自动学情提示（数据可视化辅助分析）')
    
    warning_count = 0
    
    # 检查1: 受教育年限过低
    if "受教育年限" in df.columns:
        edu_vals = pd.to_numeric(df["受教育年限"].dropna(), errors='coerce')
        if len(edu_vals) > 0 and edu_vals.mean() < 14:
            st.warning(f"⚠️ **人力资本投资认知预警**：班级平均受教育年限仅 {edu_vals.mean():.1f} 年（< 14 年阈值），{sum(edu_vals < 14)} 名学生的教育投资路径偏保守。建议讲解「教育溢价」实证数据。")
            warning_count += 1
    
    # 检查2: 歧视系数过高
    if "歧视系数" in df.columns:
        disc_vals = pd.to_numeric(df["歧视系数"].dropna(), errors='coerce')
        if len(disc_vals) > 0 and disc_vals.mean() > 15:
            st.warning(f"⚠️ **歧视效应认知预警**：班级平均歧视系数 {disc_vals.mean():.1f}%（> 15% 阈值），{sum(disc_vals > 20)} 名学生设置超过 20%。需确认学生是否理解贝克尔偏好歧视模型的福利损失机制。")
            warning_count += 1
    
    # 检查3: AI冲击认知偏差
    if "AI替代冲击" in df.columns:
        ai_vals = pd.to_numeric(df["AI替代冲击"].dropna(), errors='coerce')
        if len(ai_vals) > 0:
            high_ai = sum(ai_vals > 60)
            if high_ai > len(ai_vals) * 0.3:
                st.warning(f"⚠️ **AI冲击认知预警**：{high_ai}/{len(ai_vals)} ({100*high_ai//max(1,len(ai_vals))}%) 名学生将AI替代率设得过高（> 60%），可能存在「技术恐惧」偏差。建议重点复习「补偿效应」与「偏向性技术进步」概念。")
                warning_count += 1
            if len(ai_vals) > 0 and ai_vals.mean() < 15:
                st.info(f"💡 **AI冲击低估提示**：班级平均AI冲击 {ai_vals.mean():.1f}%（< 15% 阈值），部分学生可能低估技术变革速度。")
    
    # 检查4: 乡村振兴政策开启率
    if "乡村振兴补贴" in df.columns:
        rural_on = sum(1 for v in df["乡村振兴补贴"] if "已开启" in str(v))
        rural_rate = rural_on / max(1, len(df))
        if rural_rate < 0.3:
            st.warning(f"⚠️ **政策认知盲区**：仅有 {rural_on}/{len(df)} ({100*rural_rate:.0f}%) 的学生开启了乡村振兴补贴，低于 30% 阈值。建议补充讲解户籍制度对劳动力流动的影响及乡村振兴政策的经济学逻辑。")
            warning_count += 1
    
    # 检查5: 财政政策选择率
    if "实施政策" in df.columns:
        policy_strs = df["实施政策"].dropna().astype(str)
        fiscal_count = sum(1 for p in policy_strs if "财政" in p)
        if len(policy_strs) > 0 and fiscal_count == 0:
            st.info(f"💡 **财政政策盲区提示**：班级中无一人选择财政扩张政策。建议补充讲解：货币政策 vs 财政政策各自的适用场景——经济衰退时财政政策往往更有效（流动性陷阱）。")
    
    if warning_count == 0:
        st.success("✅ 当前上传数据的各项指标均在正常阈值范围内，暂未触发预警。")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ========== 🔥 学情诊断（新核心） ==========
    all_diagnoses = []
    for lab_type in df["实验类型"].unique():
        sub = df[df["实验类型"] == lab_type]
        diags = diagnose_class(sub, lab_type)
        all_diagnoses.extend([{**d, "实验类型": lab_type} for d in diags])
    
    if all_diagnoses:
        st.markdown('<div class="card" style="border: 2px solid #ef4444;">', unsafe_allow_html=True)
        st.markdown("""
        <div style="display:flex; align-items:center; gap:10px; margin-bottom:15px;">
            <span style="font-size:30px;">🏥</span>
            <span style="font-size:22px; font-weight:700; color:#dc2626;">学情诊断 · 靶向干预建议</span>
        </div>
        """, unsafe_allow_html=True)
        
        for i, diag in enumerate(all_diagnoses):
            with st.expander(f"🔴 {diag['实验类型']} → {diag['检测项']}", expanded=(i==0)):
                col_d1, col_d2 = st.columns([2, 1])
                with col_d1:
                    st.error(f"**问题描述：** {diag['问题描述']}")
                    st.success(f"**💊 靶向干预建议：** {diag['靶向干预']}")
                with col_d2:
                    st.markdown(f"**关联概念：**\n{diag['关联概念']}")
                    st.caption(diag['受影响学生比例'])
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ========== 知识盲区热力概览 ==========
    if all_diagnoses:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<span style="font-size:20px; font-weight:700; color:#334155;">🧠 班级知识盲区热力图</span>', unsafe_allow_html=True)
        
        # 构建盲区数据
        blindspot_data = []
        for diag in all_diagnoses:
            blindspot_data.append({
                "实验模块": diag["实验类型"],
                "盲区": diag["检测项"],
                "严重度": "🔴 需立即干预",
                "关联概念": diag["关联概念"]
            })
        
        st.dataframe(pd.DataFrame(blindspot_data), use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ========== 详细数据 ==========
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<span style="font-size:22px; font-weight:700; color:#334155;">📋 分实验类型统计</span>', unsafe_allow_html=True)
    
    for lab_type in df["实验类型"].unique():
        sub = df[df["实验类型"] == lab_type]
        st.markdown(f"### {lab_type} ({len(sub)} 份)")
        
        if lab_type == "个体职业实验室":
            col_a, col_b = st.columns(2)
            with col_a:
                if "受教育年限" in sub.columns:
                    edu_counts = sub["受教育年限"].value_counts().sort_index()
                    fig = px.bar(x=edu_counts.index, y=edu_counts.values,
                                labels={'x': '受教育年限', 'y': '人数'},
                                title='受教育年限分布',
                                color_discrete_sequence=[COLOR["primary_light"]])
                    st.plotly_chart(fig, use_container_width=True)
            with col_b:
                if "歧视系数" in sub.columns:
                    fig = px.histogram(sub, x="歧视系数", title='歧视系数设置分布',
                                      color_discrete_sequence=[COLOR["danger"]])
                    st.plotly_chart(fig, use_container_width=True)
            
            if "乡村振兴补贴" in sub.columns:
                rural_yes = sum(1 for v in sub["乡村振兴补贴"] if "已开启" in str(v))
                st.metric("开启乡村振兴补贴", f"{rural_yes}/{len(sub)} ({100*rural_yes//max(1,len(sub))}%)")
        
        elif lab_type == "企业市场实验室":
            col_a, col_b = st.columns(2)
            with col_a:
                if "技术类型" in sub.columns:
                    tech_counts = sub["技术类型"].value_counts()
                    fig = px.pie(values=tech_counts.values, names=tech_counts.index,
                                title='技术类型选择', color_discrete_sequence=[COLOR["market"], COLOR["primary_light"], COLOR["neutral"]])
                    st.plotly_chart(fig, use_container_width=True)
            with col_b:
                if "薪酬模式" in sub.columns:
                    pay_counts = sub["薪酬模式"].value_counts()
                    fig = px.pie(values=pay_counts.values, names=pay_counts.index,
                                title='薪酬模式选择', color_discrete_sequence=[COLOR["primary_light"], COLOR["market"], COLOR["warning"]])
                    st.plotly_chart(fig, use_container_width=True)
        
        elif lab_type == "宏观政策实验室":
            col_a, col_b = st.columns(2)
            with col_a:
                if "AI替代冲击" in sub.columns:
                    fig = px.histogram(sub, x="AI替代冲击", title='AI冲击参数分布',
                                      color_discrete_sequence=[COLOR["macro"]])
                    st.plotly_chart(fig, use_container_width=True)
            with col_b:
                all_policies = []
                for p_str in sub["实施政策"].dropna():
                    if p_str != "无":
                        for p in p_str.split(", "):
                            all_policies.append(p.strip())
                if all_policies:
                    policy_counts = Counter(all_policies)
                    fig = px.bar(x=list(policy_counts.keys()), y=list(policy_counts.values()),
                                labels={'x': '政策', 'y': '选择次数'},
                                title='政策工具选择频次', color_discrete_sequence=[COLOR["macro"]])
                    st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ========== 原始数据 + 导出 ==========
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.dataframe(df, use_container_width=True, hide_index=True)
    csv = df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        "📥 导出全班数据 (CSV)", csv,
        file_name=f"LMDT_Class_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv", type="primary"
    )
    st.markdown('</div>', unsafe_allow_html=True)

else:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.info("""
    ### 📭 暂无数据
    
    **操作步骤：**
    1. 学生在各实验室完成实验后，点击「📥 下载实验报告 (.md)」
    2. 收集全班 .md 文件
    3. 在此页面拖放上传 → 自动诊断
    
    *支持批量上传，后续版本将支持联机提交*
    """)
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 教学模式说明（P4 多用户并发）
# ==========================================
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown("""
<span style="font-size:20px; font-weight:700; color:#334155;">📖 本平台教学模式说明</span>

本系统采用 **"课前单机自主探究 + 课中小组投屏汇报"** 的混合教学模式：

| 阶段 | 教师 | 学生 | 平台角色 |
|------|------|------|---------|
| **课前** | 布置实验任务（如"探索 AI 冲击 ≥50% 的企业应对策略"） | 在个人设备上操作仿真，下载实验报告 | 个人探究工具 |
| **课中** | 收集报告 → 上传教师看板 → 获取学情诊断 | 小组讨论 → 投屏展示仿真结果 | 班级数据汇总 + 学情诊断 |
| **课后** | 根据诊断结果调整教学重点 | 撰写实验分析报告 | 靶向干预建议 |

> 💡 本平台定位为轻量化辅助教具，无需百万级并发能力。通过"单人异步操作 + 课堂集中汇总"规避 Streamlit session 限制，确保教学流畅性。
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
