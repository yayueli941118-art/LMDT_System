"""
核心算法引擎
包含：明瑟方程、迁移NPV、派生需求(CES)、贝弗里奇曲线、收入/替代效应分解
"""

import numpy as np

# ==========================================
# 明瑟收入方程
# ==========================================
def calc_mincer(edu, exp, gen_t=0, spec_t=0, disc=0):
    """
    明瑟收入方程模拟
    edu: 受教育年限
    exp: 工龄（可传标量或向量）
    gen_t: 一般培训投入
    spec_t: 特殊培训投入
    disc: 市场歧视系数(%)
    返回: (工资指数, 歧视后工资指数)
    """
    base = 7.0
    r = 0.08 + (0.004 * gen_t) + (0.002 * spec_t)
    ln_w = base + r * edu + 0.05 * exp - 0.0006 * (exp**2)
    wage = np.exp(ln_w)
    wage_disc = wage * (1 - disc / 100)
    return wage, wage_disc


# ==========================================
# 迁移 NPV 计算
# ==========================================
def calc_migration_npv(w_home, w_city, cost_move, cost_psych, years=20):
    """
    劳动力流动净现值计算
    w_home: 家乡月薪(k)
    w_city: 城市月薪(k)
    cost_move: 一次性搬迁成本(k)
    cost_psych: 年度心理成本(k)
    years: 计算年限
    返回: (年份数组, 累计NPV数组)
    """
    t = np.arange(1, years + 1)
    benefit = (w_city - w_home) * 12  # 年度收益
    costs = np.array([cost_move + cost_psych] + [cost_psych] * (years - 1))
    net = benefit - costs
    cum_npv = np.cumsum(net / (1.05 ** t))
    return t, cum_npv


# ==========================================
# 派生需求（简单反比模型 - 旧版兼容）
# ==========================================
def calc_derived_demand(capital, tech_type, prod_price, w_range=None):
    """
    希克斯-马歇尔派生需求
    capital: 资本存量
    tech_type: "中性技术" / "劳动替代型" / "劳动互补型"
    prod_price: 产品价格指数
    """
    if w_range is None:
        w = np.linspace(5, 100, 100)
    else:
        w = w_range
    if tech_type == "劳动互补型":
        tech_factor = 1.5
    elif tech_type == "劳动替代型":
        tech_factor = 0.6
    else:
        tech_factor = 1.0
    demand = (prod_price * capital * tech_factor * 10) / w
    return w, demand


# ==========================================
# CES 生产函数 & 劳动需求（进阶替代弹性）
# ==========================================
def ces_output(L, K, sigma, A=1.0, alpha=0.6):
    """
    CES 生产函数: Y = A * (α·K^ρ + (1-α)·L^ρ)^(1/ρ)
    其中 ρ = (σ-1)/σ
    """
    eps = 1e-12
    L_safe = max(L, eps)
    rho = (sigma - 1) / sigma
    if abs(rho) < 1e-6:  # σ≈1, 趋近Cobb-Douglas
        return A * (K ** alpha) * (L_safe ** (1 - alpha))
    val = alpha * (K ** rho) + (1 - alpha) * (L_safe ** rho)
    if val <= 0:
        val = eps
    return A * val ** (1 / rho)


def ces_mpl(L, K, sigma, A=1.0, alpha=0.6):
    """CES 边际劳动产出"""
    eps = 1e-12
    L_safe = max(L, eps)
    rho = (sigma - 1) / sigma
    if abs(rho) < 1e-6:
        return A * (1 - alpha) * (K ** alpha) * (L_safe ** (-alpha))
    val = alpha * (K ** rho) + (1 - alpha) * (L_safe ** rho)
    if val <= 0:
        val = eps
    return A * (1 - alpha) * (L_safe ** (rho - 1)) * (val ** (1 / rho - 1))


def calc_ces_demand(K, sigma, prod_price, w_range=None):
    """
    用 CES 函数数值求解最优劳动需求
    解 VMP = P * MPL = w
    """
    if w_range is None:
        w_range = np.linspace(5, 100, 80)
    L_opt = []
    for w in w_range:
        # 简化为解析反函数逼近
        if sigma <= 0.95:
            # 低替代弹性：劳动需求弹性小
            L_star = (prod_price * K * 12 / w) ** (0.7)
        elif sigma >= 1.5:
            # 高替代弹性：劳动需求弹性大
            L_star = (prod_price * K * 8 / (w * sigma)) ** 1.5
        else:
            # 中等弹性
            L_star = (prod_price * K * 10 / w) ** (1.0 / sigma)
        L_opt.append(max(0.5, L_star))
    return np.array(L_opt), w_range


# ==========================================
# 贝弗里奇曲线
# ==========================================
def calc_beveridge(mismatch, policy_effect, ai_risk):
    """
    结构性失业诊断
    mismatch: 技能错配度 (0-2.0)
    policy_effect: 政策修正 (0/1)
    ai_risk: AI冲击 (%)
    """
    u = np.linspace(0.5, 15, 100)
    k = 20 + (mismatch * 50) + (ai_risk * 0.6) - (policy_effect * 15)
    v = k / u
    return u, v


# ==========================================
# 收入效应 vs 替代效应分解
# ==========================================
def calc_income_substitution_effect(wage_initial, wage_new, beta=0.5):
    """
    基于柯布-道格拉斯效用函数 U = L^β * C^(1-β)
    计算工资变动后的收入效应与替代效应分解
    
    wage_initial: 初始工资率 (元/小时)
    wage_new: 新工资率 (元/小时)
    beta: 闲暇偏好参数 (0<β<1)，β越大越偏好闲暇
    
    返回: dict with
    - L_initial: 初始最优劳动供给
    - L_substitution: 替代效应后的劳动供给（希克斯补偿需求）
    - L_final: 最终最优劳动供给
    - C_initial, C_substitution, C_final: 各点消费
    - income_effect: 收入效应导致的劳动供给变化
    - substitution_effect: 替代效应导致的劳动供给变化
    - total_effect: 总变化
    """
    T = 24  # 总可用时间
    
    # 点A：初始均衡
    L_initial = T * (1 - beta)  # CD效用下最优劳动供给
    C_initial = wage_initial * L_initial
    
    # 点B：替代效应（补偿预算线：按新高工资率，但保持旧效用水平）
    # 在CD效用下，希克斯补偿需求 = 初始需求调整
    full_income = wage_initial * T  # 初始全部工作时间收入
    L_substitution = T * (1 - beta) * (wage_new / wage_initial) ** (beta)
    L_substitution = min(L_substitution, T - 0.5)  # 至少留0.5h闲暇
    C_substitution = wage_new * L_substitution
    
    # 点C：最终均衡（新高工资率下的实际选择）
    L_final = T * (1 - beta)
    C_final = wage_new * L_final
    
    # 效应分解
    substitution_effect = L_substitution - L_initial  # 纯替代效应（劳动增加）
    income_effect = L_final - L_substitution  # 收入效应（可能减少劳动）
    total_effect = L_final - L_initial
    
    return {
        "wage_initial": wage_initial,
        "wage_new": wage_new,
        "L_initial": L_initial,
        "C_initial": C_initial,
        "U_initial": (L_initial ** beta) * (C_initial ** (1 - beta)),
        "L_substitution": L_substitution,
        "C_substitution": C_substitution,
        "L_final": L_final,
        "C_final": C_final,
        "substitution_effect": substitution_effect,
        "income_effect": income_effect,
        "total_effect": total_effect,
        "leisure_initial": T - L_initial,
        "leisure_final": T - L_final,
    }
