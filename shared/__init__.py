from .styles import SHARED_CSS, COLOR, CARD_CSS, PAGE_BANNER_CSS
from .config import SCHOOL_NAME, DEPARTMENT, AUTHOR_NAME, COMPETITION_INFO, DATA_SOURCES
from .data import (
    CHINA_WAGE_BY_EDU_2024,
    CHINA_WAGE_BY_EDU_2023,
    CHINA_BEVERIDGE_BASELINE,
    CHINA_MIGRANT_WAGE_2024,
    EDUCATION_LABELS,
)
from .algorithms import (
    calc_mincer,
    calc_migration_npv,
    calc_derived_demand,
    calc_ces_demand,
    calc_beveridge,
    calc_income_substitution_effect,
)
from .components import (
    render_page_banner,
    render_card_header,
    render_metric_card,
    render_challenge_banner,
    render_predict_verify,
)
from .reports import generate_lab_report, generate_report_download
