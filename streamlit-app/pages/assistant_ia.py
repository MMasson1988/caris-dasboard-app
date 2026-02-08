"""
Page Assistant IA - Chatbot MEAL basé sur Gemini 2.0 Flash
"""
import streamlit as st
import pandas as pd

# Imports locaux
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.data_loader import load_depistage, load_enrolled, get_data_summary
from utils.kpi_calculator import calculate_kpis
from utils.ai_chatbot import (
    query_gemini, build_meal_context, get_suggested_questions,
    initialize_chat_history, add_to_chat_history, clear_chat_history,
    get_gemini_client
)


def render_assistant():
    """Affiche la page de l'assistant IA MEAL."""
    
    st.title("🤖 Assistant IA MEAL")
    st.markdown("---")
    
    # Description
    st.markdown("""
    <div style='background-color: #e3f2fd; padding: 15px; border-radius: 10px; border-left: 4px solid #2196f3; margin-bottom: 20px;'>
        <h4 style='margin: 0; color: #1565c0;'>💡 Assistant Analytique Intelligent</h4>
        <p style='margin: 10px 0 0 0;'>
            Posez vos questions sur les données nutrition en langage naturel. 
            L'assistant utilise <strong>Gemini 2.0 Flash</strong> pour analyser les données 
            et fournir des réponses contextualisées selon le cadre MEAL.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Vérifier la configuration Gemini
    model = get_gemini_client()
    
    if model is None:
        st.error("""
        ⚠️ **Configuration Gemini requise**
        
        Pour utiliser l'assistant IA, ajoutez votre clé API Gemini dans `.streamlit/secrets.toml`:
        
        ```toml
        [gemini]
        api_key = "votre_clé_api_gemini"
        ```
        
        Obtenez une clé API gratuite sur: [Google AI Studio](https://aistudio.google.com/app/apikey)
        """)
        
        # Mode démo sans API
        st.markdown("---")
        st.markdown("### 📚 Mode Démonstration")
        st.info("L'assistant fonctionne en mode démonstration. Les réponses sont des exemples statiques.")
        
    # Charger les données pour le contexte
    with st.spinner("Chargement du contexte analytique..."):
        df_depistage = load_depistage()
        df_enrolled = load_enrolled()
        kpis = calculate_kpis(df_depistage, df_enrolled, "current_month")
    
    # Sidebar avec informations contextuelles
    with st.sidebar:
        st.markdown("### 📊 Contexte Chargé")
        
        if not df_depistage.empty:
            st.metric("Dépistages", len(df_depistage))
        if not df_enrolled.empty:
            st.metric("Enrôlés", len(df_enrolled))
        
        st.markdown("---")
        
        # Bouton pour effacer l'historique
        if st.button("🗑️ Effacer la conversation", use_container_width=True):
            clear_chat_history()
            st.rerun()
    
    # Construire le contexte MEAL
    context = build_meal_context(df_depistage, df_enrolled, kpis)
    
    # Initialiser l'historique
    initialize_chat_history()
    
    # ============================================
    # INTERFACE DE CHAT
    # ============================================
    
    # Questions suggérées
    st.markdown("### 💡 Questions Suggérées")
    
    suggested = get_suggested_questions()
    
    cols = st.columns(2)
    for i, question in enumerate(suggested[:6]):
        with cols[i % 2]:
            if st.button(f"💬 {question[:50]}...", key=f"suggest_{i}", use_container_width=True):
                st.session_state.pending_question = question
    
    st.markdown("---")
    
    # Afficher l'historique de conversation
    st.markdown("### 💬 Conversation")
    
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.get("chat_history", []):
            if message["role"] == "user":
                with st.chat_message("user", avatar="👤"):
                    st.markdown(message["content"])
            else:
                with st.chat_message("assistant", avatar="🤖"):
                    st.markdown(message["content"])
    
    # Zone de saisie
    st.markdown("---")
    
    # Vérifier si une question suggérée a été cliquée
    if "pending_question" in st.session_state:
        user_input = st.session_state.pending_question
        del st.session_state.pending_question
    else:
        user_input = st.chat_input("Posez votre question sur les données nutrition...")
    
    if user_input:
        # Ajouter la question à l'historique
        add_to_chat_history("user", user_input)
        
        # Afficher immédiatement la question
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_input)
        
        # Générer la réponse
        with st.spinner("🔄 Analyse en cours..."):
            if model is not None:
                response = query_gemini(user_input, context, st.session_state.get("chat_history", []))
            else:
                # Réponse démo
                response = generate_demo_response(user_input, kpis, df_depistage)
        
        # Ajouter la réponse à l'historique
        add_to_chat_history("assistant", response)
        
        # Afficher la réponse
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(response)
        
        # Recharger pour mettre à jour l'historique complet
        st.rerun()
    
    # ============================================
    # INFORMATIONS SUPPLÉMENTAIRES
    # ============================================
    st.markdown("---")
    
    with st.expander("📚 Capacités de l'Assistant"):
        st.markdown("""
        **L'assistant peut vous aider à:**
        
        - 📊 **Analyser les KPIs** : Interpréter les indicateurs de performance
        - 🔍 **Explorer les données** : Identifier des patterns et tendances
        - 🏢 **Comparer les bureaux** : Performance relative entre zones
        - ⚠️ **Détecter les anomalies** : Cas nécessitant attention
        - 💡 **Recommander des actions** : Suggestions basées sur l'analyse
        
        **Limites:**
        - Analyse basée uniquement sur les données chargées
        - Ne remplace pas l'expertise MEAL humaine
        - Peut nécessiter validation des calculs complexes
        """)
    
    with st.expander("📋 Données Disponibles"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Dépistages:**")
            if not df_depistage.empty:
                st.write(f"- Colonnes: {len(df_depistage.columns)}")
                st.write(f"- Enregistrements: {len(df_depistage)}")
                st.write(f"- Bureaux: {df_depistage['office'].nunique() if 'office' in df_depistage.columns else 'N/A'}")
        
        with col2:
            st.markdown("**Enrôlements:**")
            if not df_enrolled.empty:
                st.write(f"- Colonnes: {len(df_enrolled.columns)}")
                st.write(f"- Enregistrements: {len(df_enrolled)}")
                st.write(f"- Actifs: {len(df_enrolled[df_enrolled['actif'] == True]) if 'actif' in df_enrolled.columns else 'N/A'}")


def generate_demo_response(question: str, kpis: dict, df: pd.DataFrame) -> str:
    """
    Génère une réponse de démonstration sans API Gemini.
    
    Args:
        question: Question de l'utilisateur
        kpis: KPIs calculés
        df: DataFrame de dépistage
    
    Returns:
        Réponse formatée
    """
    question_lower = question.lower()
    
    if "mas" in question_lower and "bureau" in question_lower:
        if not df.empty and 'office' in df.columns and 'manutrition_type' in df.columns:
            mas_by_office = df[df['manutrition_type'] == 'MAS'].groupby('office').size()
            if not mas_by_office.empty:
                top_office = mas_by_office.idxmax()
                top_count = mas_by_office.max()
                return f"""
**Analyse des cas MAS par bureau:**

Le bureau avec la plus forte proportion de cas MAS est **{top_office}** avec **{top_count} cas**.

**Répartition complète:**
{mas_by_office.to_string()}

**Recommandation:** 
Il serait pertinent d'investiguer les causes potentielles dans la zone de {top_office} 
et de renforcer les activités de sensibilisation communautaire.
"""
        return "Données insuffisantes pour cette analyse. Veuillez vérifier que les données sont chargées."
    
    elif "tendance" in question_lower or "évolution" in question_lower:
        return f"""
**Analyse des tendances:**

Basé sur les données actuelles:
- Total dépistages (mois courant): **{kpis.get('total_depistages', 0)}**
- Cas MAS: **{kpis.get('cas_mas', 0)}** ({kpis.get('proportion_mas', 0)}%)
- Cas MAM: **{kpis.get('cas_mam', 0)}** ({kpis.get('proportion_mam', 0)}%)

Pour une analyse de tendance complète, consultez l'onglet "Tendances" du Dashboard 
qui affiche l'évolution hebdomadaire et mensuelle.
"""
    
    elif "taux" in question_lower and "admission" in question_lower:
        return f"""
**Taux d'admission:**

Le taux d'admission global est de **{kpis.get('taux_admission', 0)}%**.

Cela signifie que sur {kpis.get('depistages_eligibles', 0)} enfants éligibles dépistés, 
{kpis.get('total_enrolled', 0)} ont été effectivement enrôlés dans le programme.

**Interprétation:**
- Taux > 70%: Bonne performance
- Taux 40-70%: Performance moyenne, actions d'amélioration recommandées
- Taux < 40%: Performance insuffisante, investigation requise
"""
    
    else:
        return f"""
**Résumé des données disponibles:**

📊 **KPIs du mois courant:**
- Dépistages: {kpis.get('total_depistages', 0)}
- Éligibles: {kpis.get('depistages_eligibles', 0)}
- Enrôlés: {kpis.get('total_enrolled', 0)}
- Cas MAS: {kpis.get('cas_mas', 0)}
- Cas MAM: {kpis.get('cas_mam', 0)}
- Taux d'admission: {kpis.get('taux_admission', 0)}%

N'hésitez pas à poser une question plus spécifique sur ces données 
ou à utiliser les questions suggérées ci-dessus.

*Note: Mode démonstration actif. Pour des analyses avancées, configurez l'API Gemini.*
"""
