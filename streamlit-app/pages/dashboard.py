"""
Page Dashboard - KPIs et visualisations MEAL
"""
import streamlit as st
import pandas as pd
from io import BytesIO

# Imports locaux
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.data_loader import (
    load_depistage, load_enrolled, 
    get_unique_offices, get_mas_cases, refresh_data
)
from utils.kpi_calculator import (
    calculate_kpis, calculate_kpis_by_office,
    calculate_weekly_trend, calculate_monthly_trend,
    calculate_malnutrition_distribution, get_period_label
)
from components.charts import (
    create_bar_chart_by_office, create_malnutrition_pie,
    create_weekly_trend, create_monthly_trend,
    create_comparison_chart, create_mas_alert_chart,
    CARIS_COLORS
)


def render_dashboard():
    """Dashboard NextAdmin style avec navigation latérale et header sombre."""
    # --- CSS NextAdmin-like ---
    st.markdown("""
    <style>
    body, .stApp { background-color: #181C2A !important; }
    .nextadmin-sidebar {
        background: #20243A;
        color: #fff;
        height: 100vh;
        width: 240px;
        position: fixed;
        left: 0; top: 0; bottom: 0;
        z-index: 100;
        padding: 30px 0 0 0;
        border-right: 1px solid #23263A;
    }
    .nextadmin-sidebar .logo {
        font-size: 1.6em;
        font-weight: bold;
        color: #6C63FF;
        margin-bottom: 2.5em;
        text-align: center;
        letter-spacing: 2px;
    }
    .nextadmin-sidebar ul { list-style: none; padding: 0; }
    .nextadmin-sidebar li { margin: 1.2em 0; }
    .nextadmin-sidebar a {
        color: #fff;
        text-decoration: none;
        font-size: 1.08em;
        display: flex;
        align-items: center;
        padding: 0.5em 2em;
        border-left: 4px solid transparent;
        transition: all 0.2s;
    }
    .nextadmin-sidebar a.selected, .nextadmin-sidebar a:hover {
        background: #23263A;
        color: #6C63FF;
        border-left: 4px solid #6C63FF;
    }
    .nextadmin-header {
        margin-left: 240px;
        background: #23263A;
        color: #fff;
        height: 70px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 2.5em;
        border-bottom: 1px solid #23263A;
        position: sticky;
        top: 0;
        z-index: 99;
    }
    .nextadmin-header .title {
        font-size: 1.5em;
        font-weight: 600;
        letter-spacing: 1px;
    }
    .nextadmin-header .header-actions {
        display: flex;
        align-items: center;
        gap: 1.5em;
    }
    .nextadmin-header .avatar {
        width: 38px; height: 38px;
        border-radius: 50%;
        background: #444;
        display: flex; align-items: center; justify-content: center;
        font-size: 1.2em;
        color: #fff;
        border: 2px solid #6C63FF;
    }
    .nextadmin-main {
        margin-left: 240px;
        padding: 2.5em 2em 2em 2em;
        background: #181C2A;
        min-height: 100vh;
    }
    .kpi-row { display: flex; gap: 1.5em; margin-bottom: 2em; }
    .kpi-card {
        background: #23263A;
        border-radius: 12px;
        padding: 1.5em 1.2em;
        flex: 1;
        color: #fff;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        display: flex; flex-direction: column; align-items: flex-start;
        min-width: 0;
    }
    .kpi-card .kpi-icon {
        font-size: 2em;
        margin-bottom: 0.3em;
    }
    .kpi-card .kpi-value {
        font-size: 2.1em;
        font-weight: 700;
        margin-bottom: 0.1em;
    }
    .kpi-card .kpi-label {
        font-size: 1.1em;
        opacity: 0.8;
    }
    .kpi-success .kpi-value { color: #28A745; }
    .kpi-warning .kpi-value { color: #FFA500; }
    .kpi-danger .kpi-value { color: #DC3545; }
    </style>
    """, unsafe_allow_html=True)

    # --- Sidebar ---
    st.markdown("""
    <div class="nextadmin-sidebar">
      <div class="logo">NextAdmin</div>
      <ul>
        <li><a href="/dashboard" class="selected"> <span style='font-size:1.2em;margin-right:0.7em;'>📊</span> Dashboard</a></li>
        <li><a href="/alertes"> <span style='font-size:1.2em;margin-right:0.7em;'>🚨</span> Alertes</a></li>
        <li><a href="/assistant_ia"> <span style='font-size:1.2em;margin-right:0.7em;'>🤖</span> Assistant IA</a></li>
        <li><a href="#"> <span style='font-size:1.2em;margin-right:0.7em;'>📁</span> Rapports</a></li>
      </ul>
    </div>
    """, unsafe_allow_html=True)

    # --- Header ---
    st.markdown("""
    <div class="nextadmin-header">
      <div class="title">Dashboard</div>
      <div class="header-actions">
        <span style="font-size:1.3em;cursor:pointer;">🔔</span>
        <span style="font-size:1.3em;cursor:pointer;">🌙</span>
        <span class="avatar">JS</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # --- Main Content ---
    st.markdown('<div class="nextadmin-main">', unsafe_allow_html=True)

    # Contrôles en haut (dans la zone principale)
    col_refresh, col_period, col_office = st.columns([1, 2, 2])
    with col_refresh:
        if st.button("🔄 Rafraîchir", use_container_width=True):
            refresh_data()
            st.rerun()
    with col_period:
        period = st.selectbox(
            "📅 Période",
            options=["current_month", "previous_month", "current_week", "previous_week", "last_3_months", "all"],
            format_func=get_period_label,
            index=0
        )
    with col_office:
        offices = get_unique_offices(load_depistage())
        selected_office = st.selectbox(
            "🏢 Bureau",
            options=["Tous"] + offices,
            index=0
        )

    # Charger les données
    with st.spinner("Chargement des données..."):
        df_depistage = load_depistage()
        df_enrolled = load_enrolled()

    if df_depistage.empty and df_enrolled.empty:
        st.error("""
        ⚠️ **Données non disponibles**
        
        Les fichiers de données n'ont pas été trouvés dans `outputs/NUTRITION/`.
        
        Fichiers attendus:
        - `depistage_filtered.xlsx`
        - `enroled_final.xlsx`
        
        Veuillez exécuter le pipeline de données ou vérifier les chemins.
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        return

    if selected_office != "Tous":
        df_depistage = df_depistage[df_depistage['office'] == selected_office]
        df_enrolled = df_enrolled[df_enrolled['office'] == selected_office] if 'office' in df_enrolled.columns else df_enrolled

    kpis = calculate_kpis(df_depistage, df_enrolled, period)

    # --- KPI Cards ---
    st.markdown('<div class="kpi-row">', unsafe_allow_html=True)
    st.markdown(f'''
        <div class="kpi-card">
            <div class="kpi-icon">🔍</div>
            <div class="kpi-value">{kpis['total_depistages']}</div>
            <div class="kpi-label">Dépistages</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-icon">👶</div>
            <div class="kpi-value">{kpis['total_enrolled']}</div>
            <div class="kpi-label">Enrôlés</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-icon">🏢</div>
            <div class="kpi-value">{kpis['nb_bureaux']}</div>
            <div class="kpi-label">Bureaux actifs</div>
        </div>
        <div class="kpi-card {'kpi-success' if kpis['taux_admission'] >= 70 else ('kpi-warning' if kpis['taux_admission'] >= 40 else 'kpi-danger')}">
            <div class="kpi-icon">📈</div>
            <div class="kpi-value">{kpis['taux_admission']}%</div>
            <div class="kpi-label">Taux d'admission</div>
        </div>
    ''', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="kpi-row">', unsafe_allow_html=True)
    st.markdown(f'''
        <div class="kpi-card kpi-danger">
            <div class="kpi-icon">🚨</div>
            <div class="kpi-value">{kpis['cas_mas']}</div>
            <div class="kpi-label">Cas MAS</div>
        </div>
        <div class="kpi-card kpi-warning">
            <div class="kpi-icon">⚠️</div>
            <div class="kpi-value">{kpis['cas_mam']}</div>
            <div class="kpi-label">Cas MAM</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-icon">✅</div>
            <div class="kpi-value">{kpis['depistages_eligibles']}</div>
            <div class="kpi-label">Éligibles</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-icon">📍</div>
            <div class="kpi-value">{kpis['nb_communes']}</div>
            <div class="kpi-label">Communes</div>
        </div>
    ''', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    # --- Reste du dashboard (visualisations, tabs, data) ---
    # On conserve tout le code existant après les KPIs
    # ============================================
    # SECTION VISUALISATIONS
    # ============================================
    st.markdown("### 📈 Visualisations")

    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Par Bureau", 
        "🍩 Malnutrition", 
        "📈 Tendances",
        "🗃️ Données"
    ])

    with tab1:
        st.markdown("#### Performance par Bureau")
        office_stats = calculate_kpis_by_office(df_depistage, df_enrolled, period)
        if not office_stats.empty:
            col_chart1, col_chart2 = st.columns(2)
            with col_chart1:
                fig_dep = create_bar_chart_by_office(
                    office_stats, 
                    'depistages',
                    "Dépistages par Bureau",
                    "Nombre de dépistages"
                )
                st.plotly_chart(fig_dep, use_container_width=True, key="fig_dep")
            with col_chart2:
                fig_mas = create_bar_chart_by_office(
                    office_stats,
                    'proportion_mas',
                    "Proportion MAS par Bureau (%)",
                    "Pourcentage"
                )
                st.plotly_chart(fig_mas, use_container_width=True, key="fig_mas")
            st.markdown("##### 📋 Tableau détaillé")
            st.dataframe(
                office_stats.style.background_gradient(cmap='Greens', subset=['depistages', 'enrolled'])
                           .background_gradient(cmap='Reds', subset=['cas_mas', 'proportion_mas']),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("Aucune donnée par bureau disponible pour cette période.")

    with tab2:
        st.markdown("#### Distribution des Types de Malnutrition")
        col_pie, col_details = st.columns([1, 1])
        with col_pie:
            fig_pie = create_malnutrition_pie(df_depistage, "Répartition MAS / MAM / Normal")
            st.plotly_chart(fig_pie, use_container_width=True, key="fig_pie")
        with col_details:
            distribution = calculate_malnutrition_distribution(df_depistage)
            if not distribution.empty:
                st.markdown("##### Détail de la distribution")
                for _, row in distribution.iterrows():
                    icon = "🚨" if row['type'] == 'MAS' else ("⚠️" if row['type'] == 'MAM' else "✅")
                    st.markdown(f"""
                    <div style="padding: 10px; margin: 5px 0; background: #23263A; border-radius: 8px; border-left: 4px solid {'#dc3545' if row['type']=='MAS' else ('#ffc107' if row['type']=='MAM' else '#28a745')}; color: #fff;">
                        {icon} <strong>{row['type']}</strong>: {row['count']} cas ({row['percentage']}%)
                    </div>
                    """, unsafe_allow_html=True)
            mas_cases = get_mas_cases(df_depistage)
            if len(mas_cases) > 0:
                st.warning(f"⚠️ **Attention**: {len(mas_cases)} cas MAS détectés. Consultez l'onglet Alertes pour plus de détails.")

    with tab3:
        st.markdown("#### Évolution Temporelle")
        col_weekly, col_monthly = st.columns(2)
        with col_weekly:
            weekly_data = calculate_weekly_trend(df_depistage)
            if not weekly_data.empty:
                fig_weekly = create_weekly_trend(weekly_data, "Dépistages par semaine")
                st.plotly_chart(fig_weekly, use_container_width=True, key="fig_weekly")
            else:
                st.info("Données hebdomadaires insuffisantes")
        with col_monthly:
            monthly_data = calculate_monthly_trend(df_depistage)
            if not monthly_data.empty:
                fig_monthly = create_monthly_trend(monthly_data, "Dépistages par mois")
                st.plotly_chart(fig_monthly, use_container_width=True, key="fig_monthly")
            else:
                st.info("Données mensuelles insuffisantes")

    with tab4:
        st.markdown("#### Exploration des Données")
        data_choice = st.radio(
            "Sélectionnez le jeu de données:",
            ["Dépistages", "Enrôlements"],
            horizontal=True,
            key="data_choice_radio"
        )
        df_display = df_depistage if data_choice == "Dépistages" else df_enrolled
        if not df_display.empty:
            st.markdown(f"**{len(df_display)} enregistrements**")
            with st.expander("🔍 Filtres avancés"):
                filter_cols = st.multiselect(
                    "Colonnes à afficher",
                    options=df_display.columns.tolist(),
                    default=df_display.columns[:10].tolist(),
                    key="filter_cols_multiselect"
                )
            if filter_cols:
                df_filtered = df_display[filter_cols]
            else:
                df_filtered = df_display
            st.dataframe(df_filtered, use_container_width=True, height=400)
            st.markdown("##### 📥 Export")
            @st.cache_data
            def convert_df_to_excel(df):
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False, sheet_name='Données')
                return output.getvalue()
            excel_data = convert_df_to_excel(df_filtered)
            st.download_button(
                label="📥 Télécharger en Excel",
                data=excel_data,
                file_name=f"meal_nutrition_{data_choice.lower()}_{period}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.info("Aucune donnée disponible")

    # ============================================
    # PIED DE PAGE
    # ============================================
    st.markdown("---")
    st.caption(f"📅 Période: {get_period_label(period)} | 🔄 Dernière mise à jour: données en cache (TTL: 1h)")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ============================================
    # SECTION VISUALISATIONS
    # ============================================
    st.markdown("### 📈 Visualisations")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Par Bureau", 
        "🍩 Malnutrition", 
        "📈 Tendances",
        "🗃️ Données"
    ])
    
    with tab1:
        st.markdown("#### Performance par Bureau")
        
        office_stats = calculate_kpis_by_office(df_depistage, df_enrolled, period)
        
        if not office_stats.empty:
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                fig_dep = create_bar_chart_by_office(
                    office_stats, 
                    'depistages',
                    "Dépistages par Bureau",
                    "Nombre de dépistages"
                )
                st.plotly_chart(fig_dep, use_container_width=True)
            
            with col_chart2:
                fig_mas = create_bar_chart_by_office(
                    office_stats,
                    'proportion_mas',
                    "Proportion MAS par Bureau (%)",
                    "Pourcentage"
                )
                st.plotly_chart(fig_mas, use_container_width=True)
            
            # Tableau détaillé
            st.markdown("##### 📋 Tableau détaillé")
            st.dataframe(
                office_stats.style.background_gradient(cmap='Greens', subset=['depistages', 'enrolled'])
                           .background_gradient(cmap='Reds', subset=['cas_mas', 'proportion_mas']),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("Aucune donnée par bureau disponible pour cette période.")
    
    with tab2:
        st.markdown("#### Distribution des Types de Malnutrition")
        
        col_pie, col_details = st.columns([1, 1])
        
        with col_pie:
            fig_pie = create_malnutrition_pie(df_depistage, "Répartition MAS / MAM / Normal")
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col_details:
            distribution = calculate_malnutrition_distribution(df_depistage)
            if not distribution.empty:
                st.markdown("##### Détail de la distribution")
                for _, row in distribution.iterrows():
                    icon = "🚨" if row['type'] == 'MAS' else ("⚠️" if row['type'] == 'MAM' else "✅")
                    st.markdown(f"""
                    <div style="padding: 10px; margin: 5px 0; background: #f8f9fa; border-radius: 8px; border-left: 4px solid {'#dc3545' if row['type']=='MAS' else ('#ffc107' if row['type']=='MAM' else '#28a745')};">
                        {icon} <strong>{row['type']}</strong>: {row['count']} cas ({row['percentage']}%)
                    </div>
                    """, unsafe_allow_html=True)
            
            # Alerte MAS si présents
            mas_cases = get_mas_cases(df_depistage)
            if len(mas_cases) > 0:
                st.warning(f"⚠️ **Attention**: {len(mas_cases)} cas MAS détectés. Consultez l'onglet Alertes pour plus de détails.")
    
    with tab3:
        st.markdown("#### Évolution Temporelle")
        
        col_weekly, col_monthly = st.columns(2)
        
        with col_weekly:
            weekly_data = calculate_weekly_trend(df_depistage)
            if not weekly_data.empty:
                fig_weekly = create_weekly_trend(weekly_data, "Dépistages par semaine")
                st.plotly_chart(fig_weekly, use_container_width=True)
            else:
                st.info("Données hebdomadaires insuffisantes")
        
        with col_monthly:
            monthly_data = calculate_monthly_trend(df_depistage)
            if not monthly_data.empty:
                fig_monthly = create_monthly_trend(monthly_data, "Dépistages par mois")
                st.plotly_chart(fig_monthly, use_container_width=True)
            else:
                st.info("Données mensuelles insuffisantes")
    
    with tab4:
        st.markdown("#### Exploration des Données")
        
        data_choice = st.radio(
            "Sélectionnez le jeu de données:",
            ["Dépistages", "Enrôlements"],
            horizontal=True
        )
        
        df_display = df_depistage if data_choice == "Dépistages" else df_enrolled
        
        if not df_display.empty:
            st.markdown(f"**{len(df_display)} enregistrements**")
            
            # Filtres dynamiques
            with st.expander("🔍 Filtres avancés"):
                filter_cols = st.multiselect(
                    "Colonnes à afficher",
                    options=df_display.columns.tolist(),
                    default=df_display.columns[:10].tolist()
                )
            
            if filter_cols:
                df_filtered = df_display[filter_cols]
            else:
                df_filtered = df_display
            
            # Afficher le tableau
            st.dataframe(df_filtered, use_container_width=True, height=400)
            
            # Bouton d'export
            st.markdown("##### 📥 Export")
            
            @st.cache_data
            def convert_df_to_excel(df):
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False, sheet_name='Données')
                return output.getvalue()
            
            excel_data = convert_df_to_excel(df_filtered)
            
            st.download_button(
                label="📥 Télécharger en Excel",
                data=excel_data,
                file_name=f"meal_nutrition_{data_choice.lower()}_{period}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.info("Aucune donnée disponible")
    
    # ============================================
    # PIED DE PAGE
    # ============================================
    st.markdown("---")
    st.caption(f"📅 Période: {get_period_label(period)} | 🔄 Dernière mise à jour: données en cache (TTL: 1h)")
