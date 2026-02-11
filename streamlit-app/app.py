"""
Application Streamlit MEAL Nutrition - Point d'entrée principal
Caris Foundation International
"""
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from pathlib import Path

# Configuration de la page
st.set_page_config(
    page_title="CARIS MEAL Nutrition",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Chargement du CSS personnalisé
def load_css():
    css_file = Path(__file__).parent / "assets" / "style.css"
    if css_file.exists():
        with open(css_file) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# ============================================
# AUTHENTIFICATION
# ============================================

def load_config():
    """Charge la configuration d'authentification depuis secrets ou fichier YAML."""
    try:
        if "credentials" in st.secrets:
            credentials_dict = {"usernames": {}}
            for username, user_data in st.secrets["credentials"]["usernames"].items():
                credentials_dict["usernames"][username] = {
                    "email": user_data["email"],
                    "name": user_data["name"],
                    "password": user_data["password"]
                }
            
            config = {
                "credentials": credentials_dict,
                "cookie": {
                    "expiry_days": st.secrets["cookie"]["expiry_days"],
                    "key": st.secrets["cookie"]["key"],
                    "name": st.secrets["cookie"]["name"]
                }
            }
            return config
    except Exception as e:
        st.warning(f"Chargement depuis secrets.toml échoué: {e}")
    
    config_file = Path(__file__).parent / "config.yaml"
    if config_file.exists():
        with open(config_file) as file:
            config = yaml.load(file, Loader=SafeLoader)
        return config
    
    return {
        "credentials": {"usernames": {"admin": {"email": "admin@carisfoundation.org", "name": "Administrateur MEAL", "password": "$2b$12$Zq9xkJlAjZQjZQjZQjZQjOeYQjZQjZQjZQjZQjZQjZQjZQjZQjZQj"}}},
        "cookie": {"expiry_days": 30, "key": "caris_meal_nutrition_key", "name": "caris_meal_auth"}
    }

def init_authenticator():
    """Initialise l'authentificateur Streamlit."""
    config = load_config()
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days']
    )
    return authenticator, config

# ============================================
# SIDEBAR INSTITUTIONNELLE
# ============================================

def render_sidebar(authenticator, name):
    """
    Affiche la sidebar institutionnelle complète : Logo, Filtres Analytiques, 
    Navigation (Dashboard, Alertes, IA, Rapport) et Déconnexion.
    """
    with st.sidebar:
        # 1. LOGO ET IDENTIFICATION
        logo_path = Path(__file__).parent / "assets" / "logo.png"
        if logo_path.exists():
            st.image(str(logo_path), use_container_width=True)
        else:
            st.markdown("""
                <div style='text-align: center; padding: 15px; background: #2E8B57; border-radius: 10px; margin-bottom: 15px;'>
                    <h2 style='color: white; margin: 0;'>🏥 CARIS</h2>
                    <p style='color: #E0E0E0; margin: 0; font-size: 10px;'>Foundation International</p>
                </div>
            """, unsafe_allow_html=True)
        
        st.success(f"👤 **{name}**")
        st.markdown("---")

        # 2. FILTRES ANALYTIQUES (Synchronisés avec les pages)
        st.markdown("### 🔍 FILTRES ANALYTIQUES")
        
        from utils.data_loader import load_enrolled, get_unique_offices
        df_all = load_enrolled()

        if not df_all.empty:
            # 2.1 Filtre par Bureau
            offices = get_unique_offices(df_all)
            st.selectbox("🏢 Bureau", options=["Tous les Bureaux"] + offices, key="filter_office")

            # 2.2 Filtre par Commune
            communes = sorted(df_all['commune'].dropna().unique().tolist())
            st.multiselect("📍 Communes", options=communes, default=communes, key="filter_commune")

            # 2.3 Filtre Temporel (Colonne date_enrollement)
            if 'date_enrollement' in df_all.columns:
                min_date = df_all['date_enrollement'].min().date()
                max_date = df_all['date_enrollement'].max().date()
                st.date_input("📅 Période d'Enrôlement", value=(min_date, max_date), key="filter_date_range")
        else:
            st.warning("⚠️ Données non disponibles pour les filtres")

        st.markdown("---")

        # 3. MENU DE NAVIGATION
        st.markdown("### 📋 NAVIGATION")
        
        menu_options = {
            "📊 Dashboard": "dashboard",
            "📧 Alertes MAS": "alertes",
            "🤖 Assistant IA": "assistant",
            "📄 Rapport HTML": "rapport"
        }

        if "current_page" not in st.session_state:
            st.session_state.current_page = "dashboard"

        for label, page_key in menu_options.items():
            button_type = "primary" if st.session_state.current_page == page_key else "secondary"
            if st.button(label, key=f"nav_btn_{page_key}", use_container_width=True, type=button_type):
                st.session_state.current_page = page_key
                st.rerun()

        st.markdown("---")

        # 4. INFOS SYSTÈME ET DÉCONNEXION
        st.caption("Version 2.5.0 - NextAdmin UI")
        st.caption("Base de données : enrole_final")
        
        st.markdown("---")
        authenticator.logout("🚪 Déconnexion", "sidebar")


# ============================================
# APPLICATION PRINCIPALE
# ============================================

def main():
    """Point d'entrée principal de l'application avec routage des pages."""
    
    authenticator, config = init_authenticator()
    
    try:
        authenticator.login(location='main', fields={
            'Form name': 'Connexion - CARIS MEAL Nutrition',
            'Username': 'Nom d\'utilisateur',
            'Password': 'Mot de passe',
            'Login': 'Se connecter'
        })
    except Exception as e:
        st.error(f"Erreur d'authentification: {e}")
        return
    
    if st.session_state.get("authentication_status"):
        name = st.session_state.get("name", "Utilisateur")
        render_sidebar(authenticator, name)
        
        current_page = st.session_state.get("current_page", "dashboard")
        
        # --- ROUTAGE DES PAGES ---
        if current_page == "dashboard":
            from pages.dashboard import render_dashboard
            render_dashboard()
        
        elif current_page == "alertes":
            from pages.alertes import render_alertes
            render_alertes()
        
        elif current_page == "assistant":
            from pages.assistant_ia import render_assistant
            render_assistant()
        
        elif current_page == "rapport":
            from pages.rapport_html import render_rapport
            render_rapport()
        else:
            from pages.dashboard import render_dashboard
            render_dashboard()
            
    elif st.session_state.get("authentication_status") is False:
        st.error("❌ Nom d'utilisateur ou mot de passe incorrect")
        
    elif st.session_state.get("authentication_status") is None:
        st.warning("👋 Veuillez entrer vos identifiants pour accéder au système MEAL")
        
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("<div style='text-align: center; padding: 20px; background: #f8f9fa; border-radius: 10px;'><h3>📊 Dashboard</h3><p>KPIs en temps réel</p></div>", unsafe_allow_html=True)
        with col2:
            st.markdown("<div style='text-align: center; padding: 20px; background: #f8f9fa; border-radius: 10px;'><h3>🤖 Assistant IA</h3><p>Analyse par Gemini 2.0</p></div>", unsafe_allow_html=True)
        with col3:
            st.markdown("<div style='text-align: center; padding: 20px; background: #f8f9fa; border-radius: 10px;'><h3>📧 Alertes</h3><p>Détection automatique MAS</p></div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()