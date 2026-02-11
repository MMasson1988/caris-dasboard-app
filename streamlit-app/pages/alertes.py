import streamlit as st
import pandas as pd
from datetime import datetime
import json
from pathlib import Path
from utils.data_loader import load_enrolled
from utils.email_service import send_mas_alert, get_smtp_config
from utils.whatsapp_service import send_whatsapp_instant, format_mas_alert_whatsapp

def save_alert_log(user, channel, recipient, count_mas):
    """Enregistre l'activité d'alerte dans un fichier local."""
    log_file = Path("outputs/NUTRITION/alert_logs.json")
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    new_log = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user": user,
        "channel": channel,
        "recipient": recipient,
        "mas_count": count_mas,
        "office": st.session_state.get("filter_office", "N/A")
    }
    
    logs = []
    if log_file.exists():
        with open(log_file, "r") as f:
            logs = json.load(f)
    
    logs.insert(0, new_log) # Ajouter au début pour voir le plus récent
    with open(log_file, "w") as f:
        json.dump(logs[:50], f, indent=4) # Garder les 50 derniers

def render_alertes():
    """Affiche la page de gestion des alertes MAS avec historique des logs."""
    
    st.markdown('<h1 style="color:white;">📧 Centre d\'Alertes MAS</h1>', unsafe_allow_html=True)
    st.markdown("---")

    # 1. FILTRAGE DES DONNÉES
    df = load_enrolled()
    if st.session_state.filter_office != "Tous les Bureaux":
        df = df[df['office'] == st.session_state.filter_office]
    
    df = df[df['commune'].isin(st.session_state.filter_commune)]
    
    if len(st.session_state.filter_date_range) == 2:
        start, end = st.session_state.filter_date_range
        df = df[(df['date_enrollement'].dt.date >= start) & (df['date_enrollement'].dt.date <= end)]

    df_mas = df[df['manutrition_type'] == 'MAS'] [cite: 1]
    count_mas = len(df_mas) [cite: 1]

    # 2. AFFICHAGE DES CARTES (Style NextAdmin)
    col_status, col_info = st.columns([1, 2])
    with col_status:
        color = "#ef4444" if count_mas > 0 else "#10b981"
        st.markdown(f"""
            <div class="kpi-card-v2" style="border-left: 5px solid {color};">
                <div class="kpi-title">Alerte Critique</div>
                <div class="kpi-value-v2" style="color:{color};">{count_mas} CAS</div>
                <div class="trend-{'down' if count_mas > 0 else 'up'}">Action {'requise' if count_mas > 0 else 'normale'}</div>
            </div>
        """, unsafe_allow_html=True)

    with col_info:
        st.info(f"**Zone :** {st.session_state.filter_office} | **Période :** {st.session_state.filter_date_range[0]} au {st.session_state.filter_date_range[1]}")

    if count_mas > 0:
        st.markdown("### 📤 Canaux de Diffusion")
        tab_email, tab_wa, tab_logs = st.tabs(["📧 Email", "📱 WhatsApp", "📜 Historique des envois"])

        with tab_email:
            config = get_smtp_config()
            if st.button("🚀 Diffuser l'alerte Email", type="primary", use_container_width=True):
                res = send_mas_alert({'has_mas': True, 'count': count_mas, 'by_office': df_mas.groupby('office').size().to_dict(), 'offices_affected': df_mas['office'].unique().tolist()})
                if res['success']:
                    save_alert_log(st.session_state.name, "Email", "Manager MEAL", count_mas)
                    st.success("✅ Email envoyé et enregistré.")

        with tab_wa:
            phone = st.text_input("Point focal WhatsApp", value="50947368767") [cite: 1, 2]
            msg_wa = format_mas_alert_whatsapp(count_mas, df_mas[['name', 'office', 'age_range']].rename(columns={'name': 'nom', 'office': 'bureau', 'age_range': 'age'}).to_dict('records'), datetime.now().strftime('%d/%m/%Y')) [cite: 2]
            if st.button("🚀 Envoyer via WhatsApp Web", use_container_width=True):
                success, info = send_whatsapp_instant(phone, msg_wa)
                if success:
                    save_alert_log(st.session_state.name, "WhatsApp", phone, count_mas)
                    st.success(info)

        with tab_logs:
            st.markdown("#### 📜 50 dernières alertes envoyées")
            log_file = Path("outputs/NUTRITION/alert_logs.json")
            if log_file.exists():
                with open(log_file, "r") as f:
                    st.table(json.load(f))
            else:
                st.write("Aucun historique pour le moment.")
    else:
        st.success("Aucune alerte à diffuser pour cette sélection.")