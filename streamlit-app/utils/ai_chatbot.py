"""
Assistant IA MEAL basé sur Gemini 2.0 Flash
Analyse contextuelle des données nutrition
"""
import streamlit as st
from typing import Dict, List, Optional
import pandas as pd
import json


def get_gemini_client():
    """
    Initialise le client Gemini avec la clé API depuis secrets.
    
    Returns:
        Instance du modèle Gemini ou None si non configuré
    """
    try:
        import google.generativeai as genai
        
        api_key = st.secrets.get("gemini", {}).get("api_key", "")
        
        if not api_key:
            return None
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        return model
        
    except ImportError:
        st.error("⚠️ Package google-generativeai non installé. Exécutez: pip install google-generativeai")
        return None
    except Exception as e:
        st.error(f"⚠️ Erreur initialisation Gemini: {e}")
        return None


def build_meal_context(df_depistage: pd.DataFrame, 
                       df_enrolled: pd.DataFrame,
                       kpis: Dict = None) -> str:
    """
    Construit le contexte MEAL pour le prompt système.
    
    Args:
        df_depistage: DataFrame des dépistages
        df_enrolled: DataFrame des enrôlements
        kpis: KPIs calculés (optionnel)
    
    Returns:
        Chaîne de contexte formatée
    """
    context_parts = []
    
    # Cadre conceptuel MEAL
    context_parts.append("""
## CADRE CONCEPTUEL MEAL - PROGRAMME NUTRITION

Tu es un analyste MEAL expert spécialisé dans les programmes de nutrition communautaire.

### Définitions Clés:
- **MAS (Malnutrition Aiguë Sévère)**: MUAC < 115mm ou œdèmes bilatéraux. Urgence médicale.
- **MAM (Malnutrition Aiguë Modérée)**: MUAC entre 115-125mm. Nécessite suivi.
- **MUAC (Mid-Upper Arm Circumference)**: Périmètre brachial, indicateur anthropométrique clé.
- **Dépistage**: Identification des cas de malnutrition dans la communauté.
- **Enrôlement**: Admission dans le programme de prise en charge.
- **MAMBA**: Supplément nutritionnel thérapeutique (Ready-to-Use Therapeutic Food).

### Indicateurs de Performance:
- **Taux de couverture**: % enfants dépistés / population cible
- **Taux d'admission**: % enfants enrôlés / enfants éligibles dépistés
- **Taux de guérison**: % enfants ayant atteint le poids cible
- **Taux d'abandon**: % enfants ayant quitté le programme prématurément

### Contexte Organisationnel:
- Organisation: CARIS Foundation International
- Zone: Haïti
- Population cible: Enfants < 5 ans, femmes enceintes et allaitantes
""")
    
    # Structure des données dépistage
    if not df_depistage.empty:
        context_parts.append(f"""
## DONNÉES DE DÉPISTAGE

### Colonnes disponibles:
{', '.join(df_depistage.columns.tolist())}

### Statistiques descriptives:
- Nombre total de dépistages: {len(df_depistage)}
- Bureaux actifs: {df_depistage['office'].nunique() if 'office' in df_depistage.columns else 'N/A'}
- Communes couvertes: {df_depistage['commune'].nunique() if 'commune' in df_depistage.columns else 'N/A'}
""")
        
        # Distribution des types de malnutrition
        if 'manutrition_type' in df_depistage.columns:
            dist = df_depistage['manutrition_type'].value_counts().to_dict()
            context_parts.append(f"""
### Distribution des types de malnutrition:
{json.dumps(dist, indent=2, ensure_ascii=False)}
""")
        
        # Éligibilité
        if 'eligible' in df_depistage.columns:
            elig = df_depistage['eligible'].value_counts().to_dict()
            context_parts.append(f"""
### Éligibilité:
{json.dumps(elig, indent=2, ensure_ascii=False)}
""")
    
    # Structure des données enrôlement
    if not df_enrolled.empty:
        context_parts.append(f"""
## DONNÉES D'ENRÔLEMENT

### Colonnes disponibles:
{', '.join(df_enrolled.columns.tolist())}

### Statistiques:
- Nombre total d'enfants enrôlés: {len(df_enrolled)}
- Enfants actifs: {len(df_enrolled[df_enrolled['actif'] == True]) if 'actif' in df_enrolled.columns else 'N/A'}
""")
        
        # Provenance des enrôlements
        if 'enrrolled_where' in df_enrolled.columns:
            prov = df_enrolled['enrrolled_where'].value_counts().to_dict()
            context_parts.append(f"""
### Provenance des enrôlements:
{json.dumps(prov, indent=2, ensure_ascii=False)}
""")
    
    # KPIs si fournis
    if kpis:
        context_parts.append(f"""
## KPIs ACTUELS

- Période: {kpis.get('period', 'N/A')}
- Dépistages: {kpis.get('total_depistages', 0)}
- Éligibles: {kpis.get('depistages_eligibles', 0)}
- Enrôlés: {kpis.get('total_enrolled', 0)}
- Cas MAS: {kpis.get('cas_mas', 0)}
- Cas MAM: {kpis.get('cas_mam', 0)}
- Taux d'admission: {kpis.get('taux_admission', 0)}%
- Proportion MAS: {kpis.get('proportion_mas', 0)}%
""")
    
    # Instructions de réponse
    context_parts.append("""
## INSTRUCTIONS DE RÉPONSE

1. **Précision**: Base tes réponses uniquement sur les données fournies.
2. **Prudence**: Signale les limites des données quand pertinent.
3. **Orientation décision**: Propose des recommandations actionnables.
4. **Langage**: Réponds en français, utilise un ton professionnel.
5. **Format**: Structure tes réponses avec des titres et listes quand approprié.
6. **Calculs**: Montre tes calculs quand tu fais des analyses quantitatives.
""")
    
    return "\n".join(context_parts)


def query_gemini(prompt: str, 
                 context: str,
                 chat_history: List[Dict] = None) -> str:
    """
    Envoie une requête à Gemini avec le contexte MEAL.
    
    Args:
        prompt: Question de l'utilisateur
        context: Contexte MEAL formaté
        chat_history: Historique de conversation (optionnel)
    
    Returns:
        Réponse de Gemini
    """
    model = get_gemini_client()
    
    if model is None:
        return "⚠️ L'assistant IA n'est pas configuré. Veuillez ajouter votre clé API Gemini dans `.streamlit/secrets.toml`:\n\n```toml\n[gemini]\napi_key = \"votre_clé_api\"\n```"
    
    # Construire le prompt complet
    full_prompt = f"""
{context}

---

## QUESTION DE L'UTILISATEUR

{prompt}

---

Réponds de manière analytique, prudente et orientée décision, en te basant sur les données et le contexte MEAL fournis ci-dessus.
"""
    
    try:
        # Générer la réponse
        response = model.generate_content(full_prompt)
        
        if response and response.text:
            return response.text
        else:
            return "⚠️ Aucune réponse générée. Veuillez reformuler votre question."
            
    except Exception as e:
        error_msg = str(e)
        
        if "quota" in error_msg.lower():
            return "⚠️ Quota API dépassé. Veuillez réessayer plus tard."
        elif "api_key" in error_msg.lower():
            return "⚠️ Clé API invalide. Vérifiez votre configuration dans secrets.toml."
        else:
            return f"⚠️ Erreur lors de la génération: {error_msg}"


def get_suggested_questions() -> List[str]:
    """
    Retourne une liste de questions suggérées pour l'utilisateur.
    
    Returns:
        Liste de questions
    """
    return [
        "Quel bureau présente la plus forte proportion de cas MAS ce mois-ci ?",
        "Quelle est la tendance des dépistages sur les 3 derniers mois ?",
        "Calcule le taux d'admission global et par bureau.",
        "Identifie les communes avec le plus de cas de malnutrition.",
        "Compare la performance entre les différents bureaux.",
        "Quels sont les facteurs de risque potentiels pour les cas MAS ?",
        "Propose des recommandations pour améliorer le taux d'admission.",
        "Analyse la répartition géographique des cas de malnutrition."
    ]


def format_chat_message(role: str, content: str) -> Dict:
    """
    Formate un message pour l'historique de chat.
    
    Args:
        role: "user" ou "assistant"
        content: Contenu du message
    
    Returns:
        Dictionnaire formaté
    """
    return {
        "role": role,
        "content": content
    }


def initialize_chat_history():
    """Initialise l'historique de chat dans session_state."""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []


def add_to_chat_history(role: str, content: str):
    """Ajoute un message à l'historique."""
    initialize_chat_history()
    st.session_state.chat_history.append(format_chat_message(role, content))


def clear_chat_history():
    """Efface l'historique de chat."""
    st.session_state.chat_history = []
