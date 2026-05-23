"""
实验报告生成模板
用于各实验室的实验报告生成
"""

from datetime import datetime
import streamlit as st


def generate_lab_report(lab_type: str, params: dict, results: dict) -> str:
    """
    生成实验报告 Markdown 文本
    
    lab_type: "micro" | "market" | "macro" | "labor_supply"
    params: 参数字典
    results: 结果字典 (包含计算结果、分析文本等)
    """
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    date_str = datetime.now().strftime('%Y%m%d')
    
    # 基准对比（如果有的话）
    baseline_section = ""
    if "baseline_comparison" in results:
        bc = results["baseline_comparison"]
        baseline_section = f"""
## 二、与真实数据基准对比
| 指标 | 本次实验值 | 中国2024年基准值 | 差异 |
|------|-----------|-----------------|------|
"""
        for item in bc:
            baseline_section += f"| {item['label']} | {item['experiment']} | {item['baseline']} | {item['diff']} |\n"
    
    # 反思题
    reflection = results.get("reflection_questions", "")
    reflection_section = ""
    if reflection:
        reflection_section = f"""
## 四、反思与讨论
{reflection}
"""
    
    # 课程思政
    ideology = results.get("ideology_text", "")
    ideology_section = ""
    if ideology:
        ideology_section = f"""
## 五、课程思政思考
{ideology}
"""
    
    # 生成标题
    lab_names = {
        "micro": "个体职业发展仿真实验报告",
        "market": "企业决策仿真实验报告",
        "macro": "宏观政策仿真实验报告",
        "labor_supply": "劳动供给决策仿真实验报告",
    }
    title = lab_names.get(lab_type, "仿真实验报告")
    
    report = f"""# {title}
**实验时间**: {now}
**学生姓名**: ___________

## 一、实验参数设定
"""
    for key, val in params.items():
        report += f"- **{key}**: {val}\n"
    
    report += baseline_section
    
    # 实验结果分析
    analysis_text = results.get("analysis", "")
    if analysis_text:
        analysis_text = analysis_text.replace("\n", "\n")
        report += f"""
## 三、实验结果分析
{analysis_text}
"""
    
    report += reflection_section
    report += ideology_section
    
    # 结论
    conclusion = results.get("conclusion", "")
    if conclusion:
        report += f"""
## 六、实验结论
{conclusion}
"""
    
    return report


def generate_report_download(report_text: str, filename_prefix: str, label: str = "📥 下载实验报告 (.md)"):
    """
    渲染报告预览区和下载按钮
    """
    from datetime import datetime
    
    # 报告预览
    st.text_area("报告预览 (Markdown)", report_text, height=200)
    
    date_str = datetime.now().strftime('%Y%m%d')
    st.download_button(
        label=label,
        data=report_text,
        file_name=f"{filename_prefix}_Report_{date_str}.md",
        mime="text/markdown",
        type="primary"
    )
