"""
Page Alertes - Détection MAS et envoi d'emails/WhatsApp
"""
import streamlit as st
import pandas as pd
from datetime import datetime

# Imports locaux
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.data_loader import (
    load_depistage, get_mas_cases,
    current_month_bounds, filter_by_date
)
from utils.kpi_calculator import get_mas_alert_data
from utils.email_service import (
    send_mas_alert, send_test_email, validate_email, get_smtp_config
)
from utils.whatsapp_service import (
    send_whatsapp_instant, format_mas_alert_whatsapp
)
from components.charts import create_mas_alert_chart, CARIS_COLORS


def render_alertes():
    """Affiche la page de gestion des alertes MAS."""
    
    st.title("📧 Alertes MAS")
    st.markdown("---")
    
    # Description
    st.markdown("""
    <div style='background-color: #fff3cd; padding: 15px; border-radius: 10px; border-left: 4px solid #ffc107; margin-bottom: 20px;'>
        <h4 style='margin: 0; color: #856404;'>⚠️ Système d'Alerte Proactive</h4>
        <p style='margin: 10px 0 0 0;'>
            Ce module détecte automatiquement les cas de <strong>Malnutrition Aiguë Sévère (MAS)</strong> 
            et permet d'envoyer des alertes email aux responsables MEAL pour une action immédiate.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Charger les données
    with st.spinner("Analyse des données en cours..."):
        df_depistage = load_depistage()
        
        # Filtrer sur le mois courant par défaut
        start, end = current_month_bounds()
        df_current = filter_by_date(df_depistage, 'date_de_depistage', start, end)
        
        # Obtenir les cas MAS
        df_mas = get_mas_cases(df_current)
        mas_data = get_mas_alert_data(df_current)
    
    # ============================================
    # SECTION DÉTECTION
    # ============================================
    st.markdown("### 🔍 Détection des Cas MAS")
    
    col_stat1, col_stat2, col_stat3 = st.columns(3)
    
    with col_stat1:
        if mas_data['has_mas']:
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #dc3545, #c82333); padding: 20px; border-radius: 15px; text-align: center; color: white;'>
                <h1 style='margin: 0; font-size: 48px;'>{mas_data['count']}</h1>
                <p style='margin: 5px 0 0 0;'>Cas MAS détectés</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style='background: linear-gradient(135deg, #28a745, #20c997); padding: 20px; border-radius: 15px; text-align: center; color: white;'>
                <h1 style='margin: 0; font-size: 48px;'>0</h1>
                <p style='margin: 5px 0 0 0;'>Aucun cas MAS</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col_stat2:
        st.markdown(f"""
        <div style='background: #f8f9fa; padding: 20px; border-radius: 15px; text-align: center; border: 2px solid #dee2e6;'>
            <h2 style='margin: 0; color: #495057;'>{len(mas_data.get('offices_affected', []))}</h2>
            <p style='margin: 5px 0 0 0; color: #6c757d;'>Bureaux concernés</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_stat3:
        st.markdown(f"""
        <div style='background: #f8f9fa; padding: 20px; border-radius: 15px; text-align: center; border: 2px solid #dee2e6;'>
            <h2 style='margin: 0; color: #495057;'>{start.strftime('%d/%m')} - {end.strftime('%d/%m')}</h2>
            <p style='margin: 5px 0 0 0; color: #6c757d;'>Période analysée</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ============================================
    # DÉTAIL DES CAS MAS
    # ============================================
    if mas_data['has_mas']:
        st.markdown("### 📋 Détail des Cas MAS")
        
        tab_chart, tab_table, tab_map = st.tabs(["📊 Graphique", "📋 Tableau", "🗺️ Par Bureau"])
        
        with tab_chart:
            fig_mas = create_mas_alert_chart(df_mas)
            st.plotly_chart(fig_mas, use_container_width=True)
        
        with tab_table:
            if not df_mas.empty:
                # Sélectionner les colonnes pertinentes
                display_cols = ['caseid', 'fullname', 'office', 'commune', 'date_de_depistage', 'muac']
                available_cols = [c for c in display_cols if c in df_mas.columns]
                
                if available_cols:
                    df_display = df_mas[available_cols].copy()
                    
                    # Formater la date
                    if 'date_de_depistage' in df_display.columns:
                        df_display['date_de_depistage'] = pd.to_datetime(df_display['date_de_depistage']).dt.strftime('%d/%m/%Y')
                    
                    st.dataframe(
                        df_display.style.applymap(
                            lambda x: 'background-color: #ffebee',
                            subset=['muac'] if 'muac' in df_display.columns else []
                        ),
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.dataframe(df_mas, use_container_width=True)
        
        with tab_map:
            st.markdown("##### Répartition par Bureau")
            for office, count in mas_data.get('by_office', {}).items():
                progress = min(count / max(mas_data.get('by_office', {}).values() or [1]), 1.0)
                st.markdown(f"**{office}**: {count} cas")
                st.progress(progress)
        
        st.markdown("---")
        
        # ============================================
        # SECTION ENVOI D'ALERTE
        # ============================================
        st.markdown("### 📤 Envoi d'Alerte Email")
        
        # Vérifier la configuration SMTP
        smtp_config = get_smtp_config()
        
        if not smtp_config['sender_email'] or not smtp_config['password']:
            st.error("""
            ⚠️ **Configuration SMTP manquante**
            
            Pour activer les alertes email, configurez les paramètres SMTP dans `.streamlit/secrets.toml`:
            
            ```toml
            [smtp]
            server = "smtp.gmail.com"
            port = 587
            sender_email = "votre.email@domain.com"
            password = "votre_mot_de_passe_app"
            receiver_emails = ["destinataire1@domain.com", "destinataire2@domain.com"]
            ```
            """)
        else:
            st.success("✅ Configuration SMTP détectée")
            
            # Prévisualisation
            with st.expander("👁️ Prévisualiser l'email", expanded=False):
                st.markdown(f"""
                **Objet:** 🚨 ALERTE MAS - {mas_data['count']} cas détecté(s) - {datetime.now().strftime('%d/%m/%Y')}
                
                **Contenu:**
                - Nombre de cas: {mas_data['count']}
                - Bureaux: {', '.join(mas_data['offices_affected'])}
                - Destinataires configurés: {', '.join(smtp_config.get('receiver_emails', []))}
                """)
            
            # Destinataires supplémentaires
            additional_emails = st.text_input(
                "📧 Destinataires supplémentaires (séparés par des virgules)",
                placeholder="email1@domain.com, email2@domain.com"
            )
            
            # Bouton d'envoi avec confirmation
            st.markdown("---")
            
            col_warning, col_button = st.columns([2, 1])
            
            with col_warning:
                st.warning("""
                ⚠️ **Validation requise**: Cliquez sur le bouton pour envoyer l'alerte.
                Cette action enverra un email aux responsables MEAL.
                """)
            
            with col_button:
                if st.button("🚀 ENVOYER L'ALERTE", type="primary", use_container_width=True):
                    # Parser les emails supplémentaires
                    extra_recipients = []
                    if additional_emails:
                        extra_recipients = [e.strip() for e in additional_emails.split(',') if validate_email(e.strip())]
                    
                    with st.spinner("Envoi en cours..."):
                        result = send_mas_alert(mas_data, extra_recipients)
                    
                    if result['success']:
                        st.success(f"✅ {result['message']}")
                        st.balloons()
                        
                        # Logger l'envoi
                        st.session_state['last_alert_sent'] = {
                            'timestamp': datetime.now().isoformat(),
                            'recipients': result['sent_to'],
                            'mas_count': mas_data['count'],
                            'type': 'email'
                        }
                    else:
                        st.error(f"❌ Échec de l'envoi: {result['error']}")
        
        # ============================================
        # SECTION ALERTE WHATSAPP
        # ============================================
        st.markdown("---")
        st.markdown("### 📱 Alerte WhatsApp Automatique")
        
        st.markdown("""
        <div style='background-color: #d4edda; padding: 15px; border-radius: 10px; border-left: 4px solid #25D366; margin-bottom: 20px;'>
            <h4 style='margin: 0; color: #155724;'>📱 Envoi WhatsApp Automatisé</h4>
            <p style='margin: 10px 0 0 0;'>
                <strong>Option 1:</strong> Cliquez pour ouvrir WhatsApp Web avec message pré-rempli<br>
                <strong>Option 2:</strong> Envoi 100% automatique via PyWhatKit (nécessite WhatsApp Web connecté)
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Configuration WhatsApp
        wa_phone = st.text_input(
            "📞 Numéro WhatsApp du destinataire (avec indicatif pays)",
            value="50947368767",
            help="Ex: 50937123456 pour Haïti (509), sans + ni espaces"
        )
        
        # Préparer le message
        cas_critiques_text = ""
        if not df_mas.empty:
            for i, row in df_mas.head(5).iterrows():
                nom = row.get('fullname', 'N/A')
                bureau = row.get('office', 'N/A')
                cas_critiques_text += f"• {nom} - {bureau}\n"
        
        wa_message = f"""🚨 *ALERTE NUTRITION - MAS DÉTECTÉS*

📅 Date: {datetime.now().strftime('%d/%m/%Y')}
⚠️ Total cas MAS: *{mas_data['count']}*

👶 *Cas prioritaires:*
{cas_critiques_text}
📋 *Action requise:*
Connectez-vous à l'application MEAL pour les détails.

🏥 CARIS Foundation International"""
        
        # Prévisualisation
        with st.expander("👁️ Prévisualiser le message"):
            st.code(wa_message, language=None)
        
        # Options d'envoi
        st.markdown("#### Choisissez votre méthode d'envoi:")
        
        col_opt1, col_opt2 = st.columns(2)
        
        with col_opt1:
            st.markdown("##### 🖱️ Option 1: Manuel")
            if wa_phone:
                import urllib.parse
                clean_phone = wa_phone.replace("+", "").replace(" ", "").replace("-", "")
                encoded_message = urllib.parse.quote(wa_message)
                wa_link = f"https://wa.me/{clean_phone}?text={encoded_message}"
                
                st.markdown(f"""
                <a href="{wa_link}" target="_blank" style="
                    display: inline-block;
                    width: 100%;
                    padding: 12px 20px;
                    background: linear-gradient(135deg, #25D366, #128C7E);
                    color: white;
                    text-align: center;
                    text-decoration: none;
                    border-radius: 10px;
                    font-weight: bold;
                ">
                    📱 Ouvrir WhatsApp
                </a>
                <p style='font-size: 0.85em; color: #666; margin-top: 8px;'>
                    Ouvre WhatsApp Web, vous cliquez sur Envoyer
                </p>
                """, unsafe_allow_html=True)
        
        with col_opt2:
            st.markdown("##### 🤖 Option 2: Automatique")
            
            # Protection contre double envoi
            if 'wa_sending' not in st.session_state:
                st.session_state.wa_sending = False
            
            send_disabled = st.session_state.wa_sending
            
            if st.button("🚀 ENVOYER AUTOMATIQUEMENT", type="primary", use_container_width=True, disabled=send_disabled):
                if not wa_phone:
                    st.error("⚠️ Entrez un numéro WhatsApp")
                elif not st.session_state.wa_sending:
                    st.session_state.wa_sending = True
                    
                    with st.spinner("📱 Ouverture de WhatsApp Web et envoi..."):
                        success, result_msg = send_whatsapp_instant(wa_phone, wa_message)
                    
                    st.session_state.wa_sending = False
                    
                    if success:
                        st.success(f"✅ {result_msg}")
                        st.balloons()
                        
                        st.session_state['last_alert_sent'] = {
                            'timestamp': datetime.now().isoformat(),
                            'recipients': [f"WhatsApp: {wa_phone}"],
                            'mas_count': mas_data['count'],
                            'type': 'whatsapp_auto'
                        }
                    else:
                        st.error(f"❌ {result_msg}")
                        if "PyWhatKit" in result_msg:
                            st.info("💡 Installez PyWhatKit: `pip install pywhatkit`")
                        elif "connecté" in result_msg:
                            st.info("💡 Ouvrez web.whatsapp.com et scannez le QR code d'abord")
            
            st.markdown("""
            <p style='font-size: 0.85em; color: #666; margin-top: 8px;'>
                Ouvre, tape et envoie automatiquement
            </p>
            """, unsafe_allow_html=True)
        
        # Note importante
        st.info("""
        💡 **Pour l'envoi automatique (Option 2):**
        1. Installez PyWhatKit: `pip install pywhatkit`
        2. Ouvrez **web.whatsapp.com** dans votre navigateur et scannez le QR code
        3. L'app ouvrira WhatsApp Web, tapera le message et l'enverra automatiquement!
        """)
    
    else:
        st.success("""
        ✅ **Aucun cas MAS détecté** pour la période analysée.
        
        Le programme nutrition fonctionne dans des paramètres normaux.
        Continuez à surveiller les indicateurs sur le Dashboard.
        """)
    
    # ============================================
    # SECTION TEST
    # ============================================
    st.markdown("---")
    st.markdown("### 🧪 Test de Configuration")
    
    with st.expander("📧 Tester l'envoi d'email"):
        test_email = st.text_input("Email de test", placeholder="votre.email@domain.com")
        
        if st.button("📨 Envoyer un email de test"):
            if test_email and validate_email(test_email):
                with st.spinner("Envoi du test..."):
                    result = send_test_email(test_email)
                
                if result['success']:
                    st.success(f"✅ {result['message']}")
                else:
                    st.error(f"❌ {result['error']}")
            else:
                st.error("Veuillez entrer une adresse email valide.")
    
    with st.expander("📱 Tester WhatsApp"):
        test_wa_phone = st.text_input(
            "Numéro WhatsApp test",
            placeholder="50937123456",
            key="test_wa_phone"
        )
        
        if test_wa_phone:
            import urllib.parse
            clean_phone = test_wa_phone.replace("+", "").replace(" ", "").replace("-", "")
            test_msg = "🧪 Test MEAL - Si vous voyez ce message, WhatsApp fonctionne ! ✅"
            encoded_msg = urllib.parse.quote(test_msg)
            test_link = f"https://wa.me/{clean_phone}?text={encoded_msg}"
            
            st.markdown(f"""
            <a href="{test_link}" target="_blank" style="
                display: inline-block;
                padding: 10px 20px;
                background: #25D366;
                color: white;
                text-decoration: none;
                border-radius: 8px;
                font-weight: bold;
            ">📱 Tester WhatsApp</a>
            """, unsafe_allow_html=True)
    
    # Historique des alertes
    if 'last_alert_sent' in st.session_state:
        st.markdown("---")
        st.markdown("### 📜 Dernière Alerte Envoyée")
        last_alert = st.session_state['last_alert_sent']
        st.info(f"""
        - **Date**: {last_alert['timestamp']}
        - **Destinataires**: {', '.join(last_alert['recipients'])}
        - **Cas MAS signalés**: {last_alert['mas_count']}
        """)
