"""
Composants de visualisation Plotly interactifs
Graphiques MEAL pour le programme nutrition
"""
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Optional, List


# Palette de couleurs institutionnelle CARIS
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
}

# Palette viridis pour graphiques
VIRIDIS_COLORS = px.colors.sequential.Viridis


def create_kpi_gauge(value: float, 
                     title: str,
                     max_value: float = 100,
                     threshold_good: float = 70,
                     threshold_bad: float = 40) -> go.Figure:
    """
    Crée un gauge pour afficher un KPI en pourcentage.
    
    Args:
        value: Valeur actuelle
        title: Titre du KPI
        max_value: Valeur maximale
        threshold_good: Seuil au-dessus duquel c'est bon
        threshold_bad: Seuil en-dessous duquel c'est mauvais
    
    Returns:
        Figure Plotly
    """
    # Déterminer la couleur
    if value >= threshold_good:
        bar_color = CARIS_COLORS["success"]
    elif value >= threshold_bad:
        bar_color = CARIS_COLORS["warning"]
    else:
        bar_color = CARIS_COLORS["danger"]
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        title={'text': title, 'font': {'size': 16}},
        number={'suffix': '%', 'font': {'size': 24}},
        gauge={
            'axis': {'range': [0, max_value], 'tickwidth': 1},
            'bar': {'color': bar_color},
            'bgcolor': CARIS_COLORS["light"],
            'steps': [
                {'range': [0, threshold_bad], 'color': '#ffebee'},
                {'range': [threshold_bad, threshold_good], 'color': '#fff3e0'},
                {'range': [threshold_good, max_value], 'color': '#e8f5e9'}
            ],
            'threshold': {
                'line': {'color': CARIS_COLORS["dark"], 'width': 2},
                'thickness': 0.75,
                'value': value
            }
        }
    ))
    
    fig.update_layout(
        height=200,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': CARIS_COLORS["dark"]}
    )
    
    return fig


def create_bar_chart_by_office(df: pd.DataFrame,
                                value_column: str,
                                title: str,
                                x_label: str = "Nombre",
                                color_column: str = None) -> go.Figure:
    """
    Crée un graphique à barres horizontales par bureau.
    
    Args:
        df: DataFrame avec colonnes 'office' et value_column
        value_column: Colonne à afficher
        title: Titre du graphique
        x_label: Label de l'axe X
        color_column: Colonne pour la couleur (optionnel)
    
    Returns:
        Figure Plotly
    """
    if df.empty or 'office' not in df.columns:
        return create_empty_chart("Données insuffisantes")
    
    df_sorted = df.sort_values(value_column, ascending=True)
    
    if color_column and color_column in df.columns:
        fig = px.bar(
            df_sorted,
            y='office',
            x=value_column,
            color=color_column,
            orientation='h',
            title=title,
            color_continuous_scale='Viridis',
            text=value_column
        )
    else:
        fig = px.bar(
            df_sorted,
            y='office',
            x=value_column,
            orientation='h',
            title=title,
            color=value_column,
            color_continuous_scale='Viridis',
            text=value_column
        )
    
    fig.update_traces(textposition='outside', textfont_size=12)
    
    fig.update_layout(
        height=max(400, len(df) * 35),
        xaxis_title=x_label,
        yaxis_title="Bureau",
        showlegend=False,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': CARIS_COLORS["dark"]}
    )
    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)')
    fig.update_yaxes(showgrid=False)
    
    return fig


def create_malnutrition_pie(df: pd.DataFrame,
                             title: str = "Répartition des types de malnutrition") -> go.Figure:
    """
    Crée un graphique en anneau pour la distribution des types de malnutrition.
    
    Args:
        df: DataFrame avec colonne 'manutrition_type'
        title: Titre du graphique
    
    Returns:
        Figure Plotly
    """
    if df.empty or 'manutrition_type' not in df.columns:
        return create_empty_chart("Données insuffisantes")
    
    distribution = df['manutrition_type'].value_counts().reset_index()
    distribution.columns = ['type', 'count']
    
    # Couleurs personnalisées par type
    color_map = {
        'MAS': CARIS_COLORS["danger"],
        'MAM': CARIS_COLORS["warning"],
        'Normal': CARIS_COLORS["success"]
    }
    
    colors = [color_map.get(t, CARIS_COLORS["info"]) for t in distribution['type']]
    
    fig = go.Figure(data=[go.Pie(
        labels=distribution['type'],
        values=distribution['count'],
        hole=0.4,
        marker_colors=colors,
        textinfo='label+percent',
        textposition='outside',
        textfont_size=14,
        pull=[0.05 if t == 'MAS' else 0 for t in distribution['type']]
    )])
    
    fig.update_layout(
        title=title,
        height=400,
        showlegend=True,
        legend=dict(orientation='h', yanchor='bottom', y=-0.1, xanchor='center', x=0.5),
        margin=dict(l=20, r=20, t=50, b=50),
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': CARIS_COLORS["dark"]}
    )
    
    # Ajouter le total au centre
    total = distribution['count'].sum()
    fig.add_annotation(
        text=f"<b>{total}</b><br>Total",
        x=0.5, y=0.5,
        font_size=18,
        showarrow=False
    )
    
    return fig


def create_weekly_trend(df: pd.DataFrame,
                        title: str = "Évolution hebdomadaire") -> go.Figure:
    """
    Crée un graphique de tendance hebdomadaire.
    
    Args:
        df: DataFrame avec colonnes 'week_start' ou 'week_label' et 'count'
        title: Titre du graphique
    
    Returns:
        Figure Plotly
    """
    if df.empty:
        return create_empty_chart("Données insuffisantes")
    
    x_col = 'week_label' if 'week_label' in df.columns else 'week_start'
    
    fig = go.Figure()
    
    # Ligne principale
    fig.add_trace(go.Scatter(
        x=df[x_col],
        y=df['count'],
        mode='lines+markers',
        name='Dépistages',
        line=dict(color=CARIS_COLORS["primary"], width=3),
        marker=dict(size=10, color=CARIS_COLORS["primary"]),
        fill='tozeroy',
        fillcolor=f'rgba(46, 139, 87, 0.1)'
    ))
    
    # Moyenne mobile (si assez de points)
    if len(df) >= 3:
        df['rolling_avg'] = df['count'].rolling(window=3, min_periods=1).mean()
        fig.add_trace(go.Scatter(
            x=df[x_col],
            y=df['rolling_avg'],
            mode='lines',
            name='Moyenne mobile (3 sem.)',
            line=dict(color=CARIS_COLORS["warning"], width=2, dash='dash')
        ))
    
    fig.update_layout(
        title=title,
        height=350,
        xaxis_title="Semaine",
        yaxis_title="Nombre",
        showlegend=True,
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        margin=dict(l=20, r=20, t=70, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        hovermode='x unified',
        font={'color': CARIS_COLORS["dark"]}
    )
    
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)')
    
    return fig


def create_monthly_trend(df: pd.DataFrame,
                         title: str = "Évolution mensuelle") -> go.Figure:
    """
    Crée un graphique de tendance mensuelle avec barres.
    
    Args:
        df: DataFrame avec colonnes 'month' et 'count'
        title: Titre du graphique
    
    Returns:
        Figure Plotly
    """
    if df.empty:
        return create_empty_chart("Données insuffisantes")
    
    fig = px.bar(
        df,
        x='month',
        y='count',
        title=title,
        color='count',
        color_continuous_scale='Viridis',
        text='count'
    )
    
    fig.update_traces(textposition='outside', textfont_size=12)
    
    fig.update_layout(
        height=350,
        xaxis_title="Mois",
        yaxis_title="Nombre",
        showlegend=False,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': CARIS_COLORS["dark"]}
    )
    
    fig.update_xaxes(tickangle=45, showgrid=False)
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)')
    
    return fig


def create_comparison_chart(df: pd.DataFrame,
                             metrics: List[str],
                             title: str = "Comparaison des métriques") -> go.Figure:
    """
    Crée un graphique de comparaison multi-métriques par bureau.
    
    Args:
        df: DataFrame avec 'office' et colonnes de métriques
        metrics: Liste des colonnes à comparer
        title: Titre du graphique
    
    Returns:
        Figure Plotly
    """
    if df.empty or 'office' not in df.columns:
        return create_empty_chart("Données insuffisantes")
    
    fig = go.Figure()
    
    colors = [CARIS_COLORS["primary"], CARIS_COLORS["warning"], 
              CARIS_COLORS["danger"], CARIS_COLORS["info"]]
    
    for i, metric in enumerate(metrics):
        if metric in df.columns:
            fig.add_trace(go.Bar(
                name=metric.replace('_', ' ').title(),
                x=df['office'],
                y=df[metric],
                marker_color=colors[i % len(colors)],
                text=df[metric],
                textposition='outside'
            ))
    
    fig.update_layout(
        title=title,
        height=400,
        xaxis_title="Bureau",
        yaxis_title="Valeur",
        barmode='group',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        margin=dict(l=20, r=20, t=70, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': CARIS_COLORS["dark"]}
    )
    
    fig.update_xaxes(tickangle=45, showgrid=False)
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)')
    
    return fig


def create_heatmap_by_commune(df: pd.DataFrame,
                               value_column: str = 'count',
                               title: str = "Carte de chaleur par commune") -> go.Figure:
    """
    Crée une heatmap des données par commune et bureau.
    
    Args:
        df: DataFrame avec 'commune', 'office' et value_column
        value_column: Colonne de valeurs
        title: Titre
    
    Returns:
        Figure Plotly
    """
    if df.empty:
        return create_empty_chart("Données insuffisantes")
    
    # Créer pivot table
    if 'commune' in df.columns and 'office' in df.columns:
        pivot = df.pivot_table(
            index='commune',
            columns='office',
            values=value_column if value_column in df.columns else df.columns[0],
            aggfunc='sum',
            fill_value=0
        )
    else:
        return create_empty_chart("Colonnes commune/office manquantes")
    
    fig = px.imshow(
        pivot,
        title=title,
        color_continuous_scale='Viridis',
        aspect='auto',
        text_auto=True
    )
    
    fig.update_layout(
        height=max(400, len(pivot) * 30),
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': CARIS_COLORS["dark"]}
    )
    
    return fig


def create_empty_chart(message: str = "Aucune donnée disponible") -> go.Figure:
    """
    Crée un graphique vide avec un message.
    
    Args:
        message: Message à afficher
    
    Returns:
        Figure Plotly vide
    """
    fig = go.Figure()
    
    fig.add_annotation(
        text=f"📊 {message}",
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.5,
        showarrow=False,
        font=dict(size=16, color=CARIS_COLORS["dark"])
    )
    
    fig.update_layout(
        height=300,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig


def create_mas_alert_chart(df_mas: pd.DataFrame,
                            title: str = "🚨 Cas MAS détectés") -> go.Figure:
    """
    Crée un graphique d'alerte pour les cas MAS.
    
    Args:
        df_mas: DataFrame des cas MAS
        title: Titre
    
    Returns:
        Figure Plotly
    """
    if df_mas.empty:
        return create_empty_chart("Aucun cas MAS détecté")
    
    # Distribution par bureau
    if 'office' in df_mas.columns:
        by_office = df_mas['office'].value_counts().reset_index()
        by_office.columns = ['office', 'count']
        
        fig = px.bar(
            by_office.sort_values('count', ascending=True),
            y='office',
            x='count',
            orientation='h',
            title=title,
            color='count',
            color_continuous_scale='Reds',
            text='count'
        )
        
        fig.update_traces(textposition='outside', textfont_size=14)
        
        fig.update_layout(
            height=max(300, len(by_office) * 40),
            xaxis_title="Nombre de cas MAS",
            yaxis_title="Bureau",
            showlegend=False,
            margin=dict(l=20, r=20, t=50, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font={'color': CARIS_COLORS["dark"]}
        )
        
        return fig
    
    return create_empty_chart("Colonne 'office' manquante")
