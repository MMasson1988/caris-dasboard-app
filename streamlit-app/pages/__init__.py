"""
Pages package initialization
"""
from .dashboard import render_dashboard
from .rapport_html import render_rapport
from .alertes import render_alertes
from .assistant_ia import render_assistant

__all__ = [
    'render_dashboard',
    'render_rapport',
    'render_alertes',
    'render_assistant'
]
