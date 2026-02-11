"""
Composants de visualisation Plotly interactifs
Graphiques MEAL pour le programme nutrition - Design NextAdmin v2.5
"""
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Optional, List


# Palette de couleurs institutionnelle CARIS & NextAdmin
CARIS_COLORS = {
    "primary": "#2E8B57",      # SeaGreen
    "secondary": "#3CB371",    # MediumSeaGreen
    "accent": "#00CED1",       # DarkTurquoise
    "warning": "#FFA500",      # Orange
    "danger": "#DC3545",       # Rouge
    "success": "#28A745",      # Vert succès
    "info": "#17A2B8",         # Bleu info
    "light": "#F8F9FA",        # Gris clair
    "dark": "#343A40",         # Gris foncé
    "next_violet": "#7c3aed",  # NextAdmin Violet
    "next_cyan": "#06b6d4",    # NextAdmin Cyan
    "next_bg": "#1e293b",      # NextAdmin Card BG
}

# ============================================
# COMPOSANTS NEXTADMIN (NOUVEAU)
# ============================================

def create_modern_area_chart(df: pd.DataFrame, x_col: str, y_col: str, title: str) -> go.Figure:
    """
    Imite le graphique 'Payments Overview' du style NextAdmin.
    Parfait pour l'évolution temporelle des enrôlements.
    """
    if df.empty:
        return create_empty_chart("Données insuffisantes pour le graphique temporel")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df[x_col], 
        y=df[y_col],
        mode='lines',
        line=dict(width=4, color=CARIS_COLORS["success"], shape='spline'),
        fill='tozeroy',
        fillcolor='rgba(40, 167, 69, 0.1)',
        name=y_col
    ))

    fig.update_layout(
        title=title,
        height=350,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#94a3b8"),
        margin=dict(l=0, r=0, t=40, b=0),
        xaxis=dict(showgrid=False, color="#94a3b8"),
        yaxis=dict(showgrid=True, gridcolor="#334155", color="#94a3b8"),
        hovermode='x unified'
    )
    return fig

def create_grouped_bar_v2(df: pd.DataFrame, x_col: str, y_cols: List[str], title: str) -> go.Figure:
    """
    Crée un graphique à barres groupées avec le code couleur NextAdmin (Violet/Cyan).
    Idéal pour comparer MAS vs MAM par Bureau.
    """
    if df.empty:
        return create_empty_chart("Données insuffisantes")

    fig = go.Figure()
    colors = [CARIS_COLORS["next_violet"], CARIS_COLORS["next_cyan"]]
    
    for i, col in enumerate(y_cols):
        if col in df.columns:
            fig.add_trace(go.Bar(
                name=col, 
                x=df[x_col], 
                y=df[col],
                marker_color=colors[i % len(colors)],
                marker_line_width=0,
                opacity=0.9
            ))
    
    fig.update_layout(
        barmode='group',
        title=title,
        height=350,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#94a3b8"),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="#334155"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=0, r=0, t=50, b=0)
    )
    return fig

# ============================================
# COMPOSANTS EXISTANTS (MIS À JOUR)
# ============================================

def create_kpi_gauge(value: float, 
                     title: str,
                     max_value: float = 100,
                     threshold_good: float = 70,
                     threshold_bad: float = 40) -> go.Figure:
    """Crée un gauge pour afficher un KPI en pourcentage."""
    if value >= threshold_good:
        bar_color = CARIS_COLORS["success"]
    elif value >= threshold_bad:
        bar_color = CARIS_COLORS["warning"]
    else:
        bar_color = CARIS_COLORS["danger"]
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': title, 'font': {'size': 16, 'color': '#94a3b8'}},
        number={'suffix': '%', 'font': {'size': 24, 'color': '#ffffff'}},
        gauge={
            'axis': {'range': [0, max_value], 'tickwidth': 1, 'tickcolor': "#94a3b8"},
            'bar': {'color': bar_color},
            'bgcolor': "rgba(255,255,255,0.05)",
            'steps': [
                {'range': [0, threshold_bad], 'color': 'rgba(220, 53, 69, 0.1)'},
                {'range': [threshold_bad, threshold_good], 'color': 'rgba(255, 165, 0, 0.1)'},
                {'range': [threshold_good, max_value], 'color': 'rgba(40, 167, 69, 0.1)'}
            ]
        }
    ))
    
    fig.update_layout(
        height=200,
        margin=dict(l=30, r=30, t=40, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
    )
    return fig

def create_malnutrition_pie(df: pd.DataFrame, title: str = "Répartition") -> go.Figure:
    """Graphique en anneau pour la distribution MAS/MAM/Normal."""
    if df.empty or 'manutrition_type' not in df.columns:
        return create_empty_chart("Données insuffisantes")
    
    dist = df['manutrition_type'].value_counts().reset_index()
    dist.columns = ['type', 'count']
    
    color_map = {'MAS': CARIS_COLORS["danger"], 'MAM': CARIS_COLORS["warning"], 'Normal': CARIS_COLORS["success"]}
    colors = [color_map.get(t, CARIS_COLORS["info"]) for t in dist['type']]
    
    fig = go.Figure(data=[go.Pie(
        labels=dist['type'], values=dist['count'], hole=0.5,
        marker=dict(colors=colors, line=dict(color='#1e293b', width=2)),
        textinfo='percent'
    )])
    
    fig.update_layout(
        title=title, height=350,
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#94a3b8"),
        legend=dict(orientation="h", y=-0.1),
        margin=dict(l=0, r=0, t=40, b=0)
    )
    return fig

def create_heatmap_by_commune(df: pd.DataFrame, value_column: str = 'count', title: str = "Concentration par Commune") -> go.Figure:
    """Heatmap avancée pour la répartition géographique."""
    if df.empty or 'commune' not in df.columns or 'office' not in df.columns:
        return create_empty_chart("Données géographiques manquantes")
    
    pivot = df.pivot_table(index='commune', columns='office', values=value_column, aggfunc='sum', fill_value=0)
    
    fig = px.imshow(
        pivot, title=title,
        labels=dict(x="Bureau", y="Commune", color="Volume"),
        color_continuous_scale=[[0, "#1e293b"], [0.5, CARIS_COLORS["next_cyan"]], [1, CARIS_COLORS["next_violet"]]]
    )
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#94a3b8"),
        margin=dict(l=0, r=0, t=50, b=0)
    )
    return fig

def create_empty_chart(message: str = "Aucune donnée disponible") -> go.Figure:
    """Crée un graphique vide stylisé avec un message."""
    fig = go.Figure()
    fig.add_annotation(
        text=f"📊 {message}", xref="paper", yref="paper",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=14, color="#94a3b8")
    )
    fig.update_layout(
        height=300, xaxis=dict(visible=False), yaxis=dict(visible=False),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig

# Fonctions legacy maintenues pour compatibilité
def create_bar_chart_by_office(df, value_column, title, x_label="Nombre", color_column=None):
    return create_grouped_bar_v2(df, 'office', [value_column], title)

def create_weekly_trend(df, title="Évolution"):
    return create_modern_area_chart(df, df.columns[0], df.columns[1], title)

def create_monthly_trend(df, title="Évolution Mensuelle"):
    return create_modern_area_chart(df, 'month', 'count', title)