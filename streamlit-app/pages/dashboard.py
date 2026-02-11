"""
Page Dashboard - KPIs et visualisations MEAL
Design NextAdmin v2.5 - CARIS Foundation
"""
import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime

# Imports locaux
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.data_loader import (
    load_depistage, load_enrolled, refresh_data
)
from utils.kpi_calculator import (
    calculate_kpis, get_period_label, get_comparison_metrics
)
from components.charts import (
    create_modern_area_chart, create_grouped_bar_v2
)

def render_dashboard():
    """Dashboard principal intégrant les filtres interactifs et les analyses de performance."""
    
    # 1. CHARGEMENT ET FILTRAGE DES DONNÉES
    df_all = load_enrolled()
    
    if df_all.empty:
        st.error("⚠️ Données non disponibles. Vérifiez le dossier outputs/NUTRITION/.")
        return

    # Application des filtres de la sidebar (Synchronisation temps réel)
    df = df_all.copy()
    
    if st.session_state.get("filter_office") != "Tous les Bureaux":
        df = df[df['office'] == st.session_state.filter_office]
    
    if "filter_commune" in st.session_state:
        df = df[df['commune'].isin(st.session_state.filter_commune)]
    
    if "filter_date_range" in st.session_state and len(st.session_state.filter_date_range) == 2:
        start, end = st.session_state.filter_date_range
        df = df[(df['date_enrollement'].dt.date >= start) & (df['date_enrollement'].dt.date <= end)]
        # Calcul des tendances via le comparateur temporel
        metrics_trend = get_comparison_metrics(df_all, start, end)
    else:
        metrics_trend = {"trend_dep": 0.0, "period_label": "vs Période précédente"}

    # 2. SECTION HEADER & KPIs (NextAdmin Style)
    st.markdown(f'<h1 style="color:white; margin-bottom:0;">Tableau de Bord MEAL</h1>', unsafe_allow_html=True)
    st.markdown(f'<p style="color:#94a3b8; margin-top:0;">Analyse de performance : {st.session_state.get("filter_office", "Global")}</p>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div class="kpi-card-v2">
                <div class="kpi-title">Enrôlements</div>
                <div class="kpi-value-v2">{len(df):,}</div>
                <div class="{"trend-up" if metrics_trend['trend_dep'] >= 0 else "trend-down"}">
                    {"▲" if metrics_trend['trend_dep'] >= 0 else "▼"} {abs(metrics_trend['trend_dep'])}% 
                    <span style="color:#94a3b8">{metrics_trend['period_label']}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        benef_total = int(df['household_number'].sum())
        st.markdown(f"""
            <div class="kpi-card-v2">
                <div class="kpi-title">Bénéficiaires Indirects</div>
                <div class="kpi-value-v2">{benef_total:,}</div>
                <div class="trend-up">Impact Famille</div>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        # On déduit les enfants actifs de la colonne 'actif' (yes/no)
        actifs = len(df[df['actif'] == 'yes'])
        st.markdown(f"""
            <div class="kpi-card-v2">
                <div class="kpi-title">Enfants Actifs</div>
                <div class="kpi-value-v2" style="color:#10b981;">{actifs}</div>
                <div class="trend-up">En cours de soin</div>
            </div>
        """, unsafe_allow_html=True)

    with col4:
        exeats = len(df[df['actif'] == 'no'])
        st.markdown(f"""
            <div class="kpi-card-v2">
                <div class="kpi-title">Enfants Exeatés</div>
                <div class="kpi-value-v2" style="color:#ef4444;">{exeats}</div>
                <div class="trend-down">Sorties de cohorte</div>
            </div>
        """, unsafe_allow_html=True)

    # 3. ANALYSES TEMPORELLES & GRAPHIQUES
    st.markdown("---")
    col_ts, col_age = st.columns([2, 1])

    with col_ts:
        st.markdown('<div class="chart-container-v2"><h3>📈 Évolution des Enrôlements</h3>', unsafe_allow_html=True)
        freq_choice = st.selectbox("Fréquence d'analyse", ["Jour", "Semaine", "Mois", "Année"], index=2, key="freq_selector")
        freq_map = {"Jour": "D", "Semaine": "W", "Mois": "M", "Année": "Y"}
        
        df_ts = df.set_index('date_enrollement').resample(freq_map[freq_choice]).size().reset_index(name='Nombre')
        fig_ts = create_modern_area_chart(df_ts, 'date_enrollement', 'Nombre', f"Enrôlements par {freq_choice}")
        st.plotly_chart(fig_ts, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_age:
        st.markdown('<div class="chart-container-v2"><h3>👶 Par Tranche d\'Âge</h3>', unsafe_allow_html=True)
        age_stats = df['age_range'].value_counts().reset_index()
        st.bar_chart(age_stats, x='age_range', y='count', color='#7c3aed')
        st.markdown('</div>', unsafe_allow_html=True)

    # 4. ANALYSE PAR AGENT ET IMPACT BUREAU
    col_agent, col_impact = st.columns(2)

    with col_agent:
        st.markdown('<div class="chart-container-v2"><h3>👤 Performance par Agent</h3>', unsafe_allow_html=True)
        agent_df = df['username'].value_counts().reset_index()
        agent_df.columns = ['Agent (Username)', 'Enrôlements']
        st.dataframe(agent_df, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_impact:
        st.markdown('<div class="chart-container-v2"><h3>🏠 Impact Social par Bureau</h3>', unsafe_allow_html=True)
        impact_stats = df.groupby('office').agg(
            menages_comptes=('has_household', lambda x: (x == 'yes').sum()),
            benef_indirects=('household_number', 'sum')
        ).reset_index()
        st.dataframe(impact_stats, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # 5. EXPLORATION DES DONNÉES FILTRÉES
    with st.expander("🗃️ Exploration des données filtrées"):
        st.dataframe(df, use_container_width=True)
        
        @st.cache_data
        def convert_df(df):
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False)
            return output.getvalue()
        
        st.download_button(
            label="📥 Télécharger la sélection actuelle (Excel)",
            data=convert_df(df),
            file_name=f"caris_export_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    # Footer
    st.markdown("---")
    st.caption(f"🔄 Dernière mise à jour: {datetime.now().strftime('%d/%m/%Y %H:%M')} | Source: enrole_final")