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
        # Essayer de charger depuis st.secrets (pour déploiement Streamlit Cloud)
        if "credentials" in st.secrets:
            # Convertir les secrets en dictionnaire standard
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
    
    # Fallback: charger depuis config.yaml local
    config_file = Path(__file__).parent / "config.yaml"
    if config_file.exists():
        with open(config_file) as file:
            config = yaml.load(file, Loader=SafeLoader)
        return config
    
    # Configuration par défaut pour développement
    return {
        "credentials": {
            "usernames": {
                "admin": {
                    "email": "admin@carisfoundation.org",
                    "name": "Administrateur MEAL",
                    "password": "$2b$12$Zq9xkJlAjZQjZQjZQjZQjOeYQjZQjZQjZQjZQjZQjZQjZQjZQjZQj"
                }
            }
        },
        "cookie": {
            "expiry_days": 30,
            "key": "caris_meal_nutrition_key",
            "name": "caris_meal_auth"
        }
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
    """Affiche la sidebar avec logo, navigation et déconnexion."""
    
    with st.sidebar:
        # Logo institutionnel
        logo_path = Path(__file__).parent / "assets" / "logo.png"
        if logo_path.exists():
            st.image(str(logo_path), use_container_width=True)
        else:
            st.markdown("""
            <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #2E8B57, #3CB371); border-radius: 10px; margin-bottom: 20px;'>
                <h2 style='color: white; margin: 0;'>🏥 CARIS</h2>
                <p style='color: #E0E0E0; margin: 5px 0 0 0; font-size: 12px;'>Foundation International</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Message de bienvenue
        st.markdown(f"""
        <div style='background-color: #f0f8f0; padding: 10px; border-radius: 8px; border-left: 4px solid #2E8B57;'>
            <p style='margin: 0; color: #2E8B57;'>👤 Bienvenue, <strong>{name}</strong></p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Navigation
        st.markdown("### 📋 Navigation")
        
        menu_options = {
            "📊 Dashboard": "dashboard",
            "📄 Rapport HTML": "rapport",
            "📧 Alertes MAS": "alertes",
            "🤖 Assistant IA": "assistant"
        }
        
        # Utiliser session_state pour la navigation
        if "current_page" not in st.session_state:
            st.session_state.current_page = "dashboard"
        
        for label, page_key in menu_options.items():
            if st.button(label, key=f"nav_{page_key}", use_container_width=True):
                st.session_state.current_page = page_key
                st.rerun()
        
        st.markdown("---")
        
        # Informations système
        st.markdown("### ℹ️ Informations")
        st.caption("📅 Données mises à jour quotidiennement")
        st.caption("🔒 Session sécurisée")
        
        st.markdown("---")
        
        # Bouton de déconnexion
        authenticator.logout("🚪 Déconnexion", "sidebar")


# ============================================
# PAGES DE L'APPLICATION
# ============================================

def page_dashboard():
    """Page Dashboard principale avec KPIs et visualisations."""
    from pages.dashboard import render_dashboard
    render_dashboard()

def page_rapport():
    """Page d'intégration du rapport HTML Quarto."""
    from pages.rapport_html import render_rapport
    render_rapport()

def page_alertes():
    """Page de gestion des alertes MAS."""
    from pages.alertes import render_alertes
    render_alertes()

def page_assistant():
    """Page de l'assistant IA MEAL."""
    from pages.assistant_ia import render_assistant
    render_assistant()


# ============================================
# APPLICATION PRINCIPALE
# ============================================

def main():
    """Point d'entrée principal de l'application."""
    
    # Initialiser l'authentificateur
    authenticator, config = init_authenticator()
    
    # Afficher le formulaire de connexion
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
    
    # Vérifier l'état de l'authentification
    if st.session_state.get("authentication_status"):
        # Utilisateur connecté
        name = st.session_state.get("name", "Utilisateur")
        
        # Afficher la sidebar
        render_sidebar(authenticator, name)
        
        # Router vers la page appropriée
        current_page = st.session_state.get("current_page", "dashboard")
        
        if current_page == "dashboard":
            page_dashboard()
        elif current_page == "rapport":
            page_rapport()
        elif current_page == "alertes":
            page_alertes()
        elif current_page == "assistant":
            page_assistant()
        else:
            page_dashboard()
            
    elif st.session_state.get("authentication_status") is False:
        st.error("❌ Nom d'utilisateur ou mot de passe incorrect")
        
    elif st.session_state.get("authentication_status") is None:
        st.warning("👋 Veuillez entrer vos identifiants pour accéder au système MEAL")
        
        # Afficher des informations sur l'application
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div style='text-align: center; padding: 20px; background: #f8f9fa; border-radius: 10px;'>
                <h3>📊 Dashboard</h3>
                <p>KPIs en temps réel, visualisations interactives</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style='text-align: center; padding: 20px; background: #f8f9fa; border-radius: 10px;'>
                <h3>🤖 Assistant IA</h3>
                <p>Analyse MEAL assistée par Gemini 2.0</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div style='text-align: center; padding: 20px; background: #f8f9fa; border-radius: 10px;'>
                <h3>📧 Alertes</h3>
                <p>Notifications automatiques cas MAS</p>
            </div>
            """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
