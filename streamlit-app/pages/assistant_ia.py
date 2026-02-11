"""
Page Assistant IA - Chatbot MEAL basé sur Gemini 2.0 Flash
Intégré avec les filtres interactifs et les logs d'alertes
"""
import streamlit as st
import pandas as pd

# Imports locaux
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.data_loader import load_depistage, load_enrolled
from utils.kpi_calculator import calculate_kpis
from utils.ai_chatbot import (
    query_gemini, build_meal_context, get_suggested_questions,
    initialize_chat_history, add_to_chat_history, clear_chat_history,
    get_gemini_client
)

def render_assistant():
    with st.spinner("Synchronisation avec les filtres en cours..."):
        # Charger les données brutes
        # Charger le fichier depistage_filtered.xlsx depuis output/NUTRITION/
        depistage_path = Path(__file__).parent.parent.parent / "output" / "NUTRITION" / "depistage_filtered.xlsx"
        if depistage_path.exists():
            df_depistage = pd.read_excel(depistage_path)
        else:
            st.warning(f"Fichier {depistage_path} introuvable. Les analyses de dépistage seront incomplètes.")
            df_depistage = pd.DataFrame()
        df_enrolled = load_enrolled()

        # Filtrage IA : uniquement enfants enrôlés entre 1er mai 2025 et aujourd'hui
        date_min = pd.to_datetime("2025-05-01").date()
        date_max = pd.Timestamp.today().date()
        if 'date_enrollement' in df_enrolled.columns:
            df_enrolled = df_enrolled[(df_enrolled['date_enrollement'].dt.date >= date_min) & (df_enrolled['date_enrollement'].dt.date <= date_max)]

        # Calcul des KPIs sur la sélection actuelle
        kpis = calculate_kpis(df_depistage, df_enrolled, "all")

        # 1b. AFFICHAGE DU DATATABLE DES BÉNÉFICIAIRES FILTRÉS
        st.markdown("### Liste des bénéficiaires filtrés")
        st.dataframe(df_enrolled, use_container_width=True)

        # 1c. RÉSUMÉ AUTOMATIQUE DES BÉNÉFICIAIRES FILTRÉS
        st.markdown("#### Résumé des bénéficiaires filtrés")
        total = len(df_enrolled)
        nb_communes = df_enrolled['commune'].nunique() if 'commune' in df_enrolled.columns else 0
        nb_bureaux = df_enrolled['office'].nunique() if 'office' in df_enrolled.columns else 0
        st.info(f"Total : {total} | Bureaux : {nb_bureaux} | Communes : {nb_communes}")

        # 1d. ALERTES MAS (MUAC <= 11)
        st.markdown("#### 🚨 Alertes MAS (MUAC ≤ 11)")
        if 'muac' in df_enrolled.columns and 'manutrition_type' in df_enrolled.columns:
            mas_alerts = df_enrolled[(df_enrolled['manutrition_type'] == 'MAS') & (df_enrolled['muac'] <= 11)]
            nb_alerts = len(mas_alerts)
            st.warning(f"{nb_alerts} bénéficiaires MAS avec MUAC ≤ 11 détectés.")
            if nb_alerts > 0:
                st.dataframe(mas_alerts[['name', 'office', 'commune', 'muac', 'date_enrollement']], use_container_width=True)
        else:
            st.info("Colonnes 'muac' ou 'manutrition_type' absentes dans les données.")
    """Affiche la page de l'assistant IA MEAL synchronisée avec les filtres."""
    
    st.markdown('<h1 style="color:white;">🤖 Assistant IA MEAL</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Description stylisée
    st.markdown("""
    <div style='background-color: #fff; padding: 15px; border-radius: 10px; border-left: 4px solid #7c3aed; margin-bottom: 20px;'>
        <h4 style='margin: 0; color: #7c3aed;'>💡 Intelligence Analytique Contextuelle</h4>
        <p style='margin: 10px 0 0 0; color: #343A40;'>
            Posez vos questions sur les données filtrées dans la barre latérale. 
            L'assistant analyse les <strong>1 299 enregistrements</strong> et l'historique des alertes 
            pour fournir des réponses expertes.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # 1. RÉCUPÉRATION ET FILTRAGE DES DONNÉES (Excel + Filtres Sidebar)
    with st.spinner("Synchronisation avec les filtres en cours..."):
        # Charger les données brutes
        df_depistage = load_depistage()
        df_enrolled = load_enrolled()
        
        # Application des filtres de la Sidebar (Bureau, Commune, Date)
        if st.session_state.get("filter_office") != "Tous les Bureaux":
            df_enrolled = df_enrolled[df_enrolled['office'] == st.session_state.filter_office]
            
        if "filter_commune" in st.session_state:
            df_enrolled = df_enrolled[df_enrolled['commune'].isin(st.session_state.filter_commune)]
            
        if "filter_date_range" in st.session_state and len(st.session_state.filter_date_range) == 2:
            start, end = st.session_state.filter_date_range
            df_enrolled = df_enrolled[(df_enrolled['date_enrollement'].dt.date >= start) & 
                                     (df_enrolled['date_enrollement'].dt.date <= end)]

        # Calcul des KPIs sur la sélection actuelle
        kpis = calculate_kpis(df_depistage, df_enrolled, "all")


    # 1b. AFFICHAGE DU DATATABLE DES BÉNÉFICIAIRES FILTRÉS
    st.markdown("### Liste des bénéficiaires filtrés")
    st.dataframe(df_enrolled, use_container_width=True)

    # 1c. RÉSUMÉ AUTOMATIQUE DES BÉNÉFICIAIRES FILTRÉS
    st.markdown("#### Résumé des bénéficiaires filtrés")
    total = len(df_enrolled)
    nb_communes = df_enrolled['commune'].nunique() if 'commune' in df_enrolled.columns else 0
    nb_bureaux = df_enrolled['office'].nunique() if 'office' in df_enrolled.columns else 0
    st.info(f"Total : {total} | Bureaux : {nb_bureaux} | Communes : {nb_communes}")

    # 1d. ALERTES MAS (MUAC <= 11)
    st.markdown("#### 🚨 Alertes MAS (MUAC ≤ 11)")
    if 'muac' in df_enrolled.columns and 'manutrition_type' in df_enrolled.columns:
        mas_alerts = df_enrolled[(df_enrolled['manutrition_type'] == 'MAS') & (df_enrolled['muac'] <= 11)]
        nb_alerts = len(mas_alerts)
        st.warning(f"{nb_alerts} bénéficiaires MAS avec MUAC ≤ 11 détectés.")
        if nb_alerts > 0:
            st.dataframe(mas_alerts[['name', 'office', 'commune', 'muac', 'date_enrollement']], use_container_width=True)
    else:
        st.info("Colonnes 'muac' ou 'manutrition_type' absentes dans les données.")
    
    # 2. CONFIGURATION GEMINI
    model = get_gemini_client()
    
    # Sidebar contextuelle
    with st.sidebar:
        st.markdown("### 📊 Focus Actuel")
        st.metric("Enregistrements analysés", len(df_enrolled))
        if st.button("🗑️ Effacer la conversation", use_container_width=True):
            clear_chat_history()
            st.rerun()

    # Construire le contexte MEAL enrichi (inclut les logs d'alertes via build_meal_context)
    context = build_meal_context(df_depistage, df_enrolled, kpis)
    
    initialize_chat_history()

    # 3. INTERFACE DE CHAT
    st.markdown("### 💡 Questions Suggérées")
    suggested = get_suggested_questions()
    
    cols = st.columns(2)
    for i, question in enumerate(suggested[:4]):
        with cols[i % 2]:
            if st.button(f"💬 {question}", key=f"suggest_{i}", use_container_width=True):
                st.session_state.pending_question = question

    st.markdown("---")
    
    # Conteneur de discussion
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.get("chat_history", []):
            avatar = "👤" if message["role"] == "user" else "🤖"
            with st.chat_message(message["role"], avatar=avatar):
                st.markdown(message["content"])

    # Zone de saisie
    if "pending_question" in st.session_state:
        user_input = st.session_state.pending_question
        del st.session_state.pending_question
    else:
        user_input = st.chat_input("Posez une question sur les enrôlements ou les alertes...")

    if user_input:
        add_to_chat_history("user", user_input)
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_input)
        
        with st.spinner("🔄 Analyse des données CARIS..."):
            if model is not None:
                # Appel à Gemini avec le contexte filtré
                response = query_gemini(user_input, context, st.session_state.chat_history)
            else:
                response = generate_demo_response(user_input, kpis, df_enrolled)
        
        add_to_chat_history("assistant", response)
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(response)
        st.rerun()

def generate_demo_response(question, kpis, df):
    """Réponse de secours si l'API n'est pas configurée."""
    # Détection de la question sur le taux d'admission
    if "taux d'admission" in question.lower():
        # Calcul global
        total_eligibles = df['eligible'].eq('yes').sum() if 'eligible' in df.columns else 0
        total_enrolled = len(df)
        taux_global = round((total_enrolled / total_eligibles) * 100, 1) if total_eligibles > 0 else 0.0
        # Calcul par bureau
        if 'office' in df.columns and 'eligible' in df.columns:
            bureau_stats = df.groupby('office').agg(
                eligibles=('eligible', lambda x: (x == 'yes').sum()),
                enrolled=('eligible', 'count')
            )
            bureau_stats['taux_admission'] = bureau_stats.apply(
                lambda row: round((row['enrolled'] / row['eligibles']) * 100, 1) if row['eligibles'] > 0 else 0.0,
                axis=1
            )
            bureau_table = bureau_stats[['taux_admission']].to_markdown()
        else:
            bureau_table = "Colonnes manquantes pour le calcul par bureau."
        return f"""
        **Taux d'admission global** : {taux_global}%

        **Taux d'admission par bureau :**
        {bureau_table}
        """
    return f"""
    **Mode Démonstration Actif**
    
    Sur la base de votre sélection actuelle :
    - Nombre d'enrôlements : {len(df)}
    - Bureau sélectionné : {st.session_state.get('filter_office', 'Tous')}
    - Taux d'admission : {kpis.get('taux_admission', 0)}%
    
    *Veuillez configurer votre clé API Gemini pour une analyse plus profonde.*
    """