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
    """Affiche le dashboard principal."""
    
    st.title("📊 Dashboard MEAL Nutrition")
    st.markdown("---")
    
    # Contrôles en haut
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
    
    # Charger les données
    with st.spinner("Chargement des données..."):
        df_depistage = load_depistage()
        df_enrolled = load_enrolled()
    
    # Vérifier si les données existent
    if df_depistage.empty and df_enrolled.empty:
        st.error("""
        ⚠️ **Données non disponibles**
        
        Les fichiers de données n'ont pas été trouvés dans `outputs/NUTRITION/`.
        
        Fichiers attendus:
        - `depistage_filtered.xlsx`
        - `enroled_final.xlsx`
        
        Veuillez exécuter le pipeline de données ou vérifier les chemins.
        """)
        return
    
    # Filtre bureau
    with col_office:
        offices = get_unique_offices(df_depistage)
        selected_office = st.selectbox(
            "🏢 Bureau",
            options=["Tous"] + offices,
            index=0
        )
    
    # Appliquer filtre bureau
    if selected_office != "Tous":
        df_depistage = df_depistage[df_depistage['office'] == selected_office]
        df_enrolled = df_enrolled[df_enrolled['office'] == selected_office] if 'office' in df_enrolled.columns else df_enrolled
    
    # Calculer les KPIs
    kpis = calculate_kpis(df_depistage, df_enrolled, period)
    
    # ============================================
    # SECTION KPIs
    # ============================================
    st.markdown("### 🎯 Indicateurs Clés de Performance")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-icon">🔍</div>
            <div class="kpi-value">{}</div>
            <div class="kpi-label">Dépistages</div>
        </div>
        """.format(kpis['total_depistages']), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-icon">👶</div>
            <div class="kpi-value">{}</div>
            <div class="kpi-label">Enrôlés</div>
        </div>
        """.format(kpis['total_enrolled']), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-icon">🏢</div>
            <div class="kpi-value">{}</div>
            <div class="kpi-label">Bureaux actifs</div>
        </div>
        """.format(kpis['nb_bureaux']), unsafe_allow_html=True)
    
    with col4:
        taux_color = "kpi-success" if kpis['taux_admission'] >= 70 else ("kpi-warning" if kpis['taux_admission'] >= 40 else "kpi-danger")
        st.markdown("""
        <div class="kpi-card {}">
            <div class="kpi-icon">📈</div>
            <div class="kpi-value">{}%</div>
            <div class="kpi-label">Taux d'admission</div>
        </div>
        """.format(taux_color, kpis['taux_admission']), unsafe_allow_html=True)
    
    # Deuxième ligne de KPIs
    col5, col6, col7, col8 = st.columns(4)
    
    with col5:
        st.markdown("""
        <div class="kpi-card kpi-danger">
            <div class="kpi-icon">🚨</div>
            <div class="kpi-value">{}</div>
            <div class="kpi-label">Cas MAS</div>
        </div>
        """.format(kpis['cas_mas']), unsafe_allow_html=True)
    
    with col6:
        st.markdown("""
        <div class="kpi-card kpi-warning">
            <div class="kpi-icon">⚠️</div>
            <div class="kpi-value">{}</div>
            <div class="kpi-label">Cas MAM</div>
        </div>
        """.format(kpis['cas_mam']), unsafe_allow_html=True)
    
    with col7:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-icon">✅</div>
            <div class="kpi-value">{}</div>
            <div class="kpi-label">Éligibles</div>
        </div>
        """.format(kpis['depistages_eligibles']), unsafe_allow_html=True)
    
    with col8:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-icon">📍</div>
            <div class="kpi-value">{}</div>
            <div class="kpi-label">Communes</div>
        </div>
        """.format(kpis['nb_communes']), unsafe_allow_html=True)
    
    st.markdown("---")
    
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
