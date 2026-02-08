"""
Utils package initialization
"""
from .data_loader import (
    load_depistage,
    load_enrolled,
    load_waiting_list,
    load_club_data,
    load_suivi,
    get_data_path,
    filter_by_date,
    previous_week_bounds,
    current_week_bounds,
    previous_month_bounds,
    current_month_bounds,
    last_three_months_bounds,
    get_unique_offices,
    get_unique_communes,
    get_malnutrition_types,
    get_mas_cases,
    get_mam_cases,
    get_data_summary,
    refresh_data
)

from .kpi_calculator import (
    calculate_kpis,
    calculate_kpis_by_office,
    calculate_weekly_trend,
    calculate_monthly_trend,
    calculate_malnutrition_distribution,
    get_mas_alert_data,
    format_kpi_delta,
    get_period_label
)

from .email_service import (
    send_mas_alert,
    send_test_email,
    validate_email,
    get_smtp_config,
    create_mas_alert_email
)

from .ai_chatbot import (
    query_gemini,
    build_meal_context,
    get_suggested_questions,
    get_gemini_client,
    initialize_chat_history,
    add_to_chat_history,
    clear_chat_history
)

__all__ = [
    # Data loader
    'load_depistage',
    'load_enrolled',
    'load_waiting_list',
    'load_club_data',
    'load_suivi',
    'get_data_path',
    'filter_by_date',
    'previous_week_bounds',
    'current_week_bounds',
    'previous_month_bounds',
    'current_month_bounds',
    'last_three_months_bounds',
    'get_unique_offices',
    'get_unique_communes',
    'get_malnutrition_types',
    'get_mas_cases',
    'get_mam_cases',
    'get_data_summary',
    'refresh_data',
    
    # KPI calculator
    'calculate_kpis',
    'calculate_kpis_by_office',
    'calculate_weekly_trend',
    'calculate_monthly_trend',
    'calculate_malnutrition_distribution',
    'get_mas_alert_data',
    'format_kpi_delta',
    'get_period_label',
    
    # Email service
    'send_mas_alert',
    'send_test_email',
    'validate_email',
    'get_smtp_config',
    'create_mas_alert_email',
    
    # AI chatbot
    'query_gemini',
    'build_meal_context',
    'get_suggested_questions',
    'get_gemini_client',
    'initialize_chat_history',
    'add_to_chat_history',
    'clear_chat_history'
]
