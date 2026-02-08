"""
Service d'envoi d'emails pour alertes MAS
Utilise SMTP avec authentification via Streamlit Secrets
"""
import smtplib
import ssl
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Dict, Optional
import streamlit as st
from datetime import datetime


def get_smtp_config() -> Dict[str, str]:
    """
    Récupère la configuration SMTP depuis Streamlit Secrets.
    
    Returns:
        Dictionnaire avec les paramètres SMTP
    """
    try:
        return {
            "server": st.secrets["smtp"]["server"],
            "port": int(st.secrets["smtp"]["port"]),
            "sender_email": st.secrets["smtp"]["sender_email"],
            "password": st.secrets["smtp"]["password"],
            "receiver_emails": st.secrets["smtp"].get("receiver_emails", [])
        }
    except KeyError as e:
        st.error(f"⚠️ Configuration SMTP manquante dans secrets.toml: {e}")
        # Configuration par défaut pour développement
        return {
            "server": "smtp.gmail.com",
            "port": 587,
            "sender_email": "",
            "password": "",
            "receiver_emails": []
        }


def create_mas_alert_email(mas_data: Dict, 
                            recipient_name: str = "MEAL Manager") -> MIMEMultipart:
    """
    Crée un email d'alerte formaté pour les cas MAS.
    
    Args:
        mas_data: Données des cas MAS (depuis get_mas_alert_data)
        recipient_name: Nom du destinataire
    
    Returns:
        Message email formaté
    """
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f"🚨 ALERTE MAS - {mas_data['count']} cas détecté(s) - {datetime.now().strftime('%d/%m/%Y')}"
    
    # Version texte simple
    text_content = f"""
ALERTE NUTRITION - CAS MAS DÉTECTÉS

Bonjour {recipient_name},

Le système MEAL a détecté {mas_data['count']} nouveau(x) cas de Malnutrition Aiguë Sévère (MAS).

Bureaux concernés: {', '.join(mas_data['offices_affected'])}

Répartition par bureau:
"""
    for office, count in mas_data.get('by_office', {}).items():
        text_content += f"  - {office}: {count} cas\n"
    
    text_content += """
ACTION REQUISE: Veuillez vérifier les cas et initier le suivi approprié.

Connectez-vous au dashboard MEAL pour plus de détails.

---
Message généré automatiquement par le système MEAL CARIS
"""
    
    # Version HTML
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .header {{ background: linear-gradient(135deg, #dc3545, #c82333); color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ padding: 20px; background: #f8f9fa; }}
        .alert-box {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 15px 0; border-radius: 4px; }}
        .stats-table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
        .stats-table th {{ background: #2E8B57; color: white; padding: 10px; text-align: left; }}
        .stats-table td {{ padding: 10px; border-bottom: 1px solid #ddd; }}
        .stats-table tr:hover {{ background: #f5f5f5; }}
        .footer {{ background: #2E8B57; color: white; padding: 15px; text-align: center; font-size: 12px; border-radius: 0 0 10px 10px; }}
        .btn {{ display: inline-block; padding: 10px 20px; background: #2E8B57; color: white; text-decoration: none; border-radius: 5px; margin-top: 15px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🚨 ALERTE NUTRITION</h1>
        <h2>Cas MAS Détectés</h2>
    </div>
    
    <div class="content">
        <p>Bonjour <strong>{recipient_name}</strong>,</p>
        
        <div class="alert-box">
            <strong>⚠️ Le système MEAL a détecté {mas_data['count']} nouveau(x) cas de Malnutrition Aiguë Sévère (MAS).</strong>
        </div>
        
        <h3>📊 Répartition par Bureau</h3>
        <table class="stats-table">
            <thead>
                <tr>
                    <th>Bureau</th>
                    <th>Nombre de cas</th>
                </tr>
            </thead>
            <tbody>
"""
    
    for office, count in mas_data.get('by_office', {}).items():
        html_content += f"""
                <tr>
                    <td>{office}</td>
                    <td><strong>{count}</strong></td>
                </tr>
"""
    
    html_content += f"""
            </tbody>
        </table>
        
        <h3>📋 Action Requise</h3>
        <p>Veuillez vérifier les cas identifiés et initier le protocole de prise en charge MAS approprié.</p>
        
        <p><em>Date de détection: {datetime.now().strftime('%d/%m/%Y à %H:%M')}</em></p>
    </div>
    
    <div class="footer">
        <p>Message généré automatiquement par le système MEAL</p>
        <p>CARIS Foundation International</p>
    </div>
</body>
</html>
"""
    
    # Attacher les deux versions
    part1 = MIMEText(text_content, 'plain', 'utf-8')
    part2 = MIMEText(html_content, 'html', 'utf-8')
    
    msg.attach(part1)
    msg.attach(part2)
    
    return msg


def send_mas_alert(mas_data: Dict,
                   additional_recipients: List[str] = None) -> Dict[str, any]:
    """
    Envoie une alerte email pour les cas MAS détectés.
    
    Args:
        mas_data: Données des cas MAS
        additional_recipients: Emails supplémentaires
    
    Returns:
        Dictionnaire avec statut d'envoi
    """
    config = get_smtp_config()
    
    if not config['sender_email'] or not config['password']:
        return {
            "success": False,
            "error": "Configuration SMTP incomplète. Vérifiez secrets.toml",
            "sent_to": []
        }
    
    if not mas_data.get('has_mas', False):
        return {
            "success": False,
            "error": "Aucun cas MAS à signaler",
            "sent_to": []
        }
    
    # Préparer la liste des destinataires
    recipients = list(config.get('receiver_emails', []))
    if additional_recipients:
        recipients.extend(additional_recipients)
    
    if not recipients:
        return {
            "success": False,
            "error": "Aucun destinataire configuré",
            "sent_to": []
        }
    
    # Créer le message
    msg = create_mas_alert_email(mas_data)
    msg['From'] = config['sender_email']
    msg['To'] = ', '.join(recipients)
    
    # Envoyer
    try:
        context = ssl.create_default_context()
        
        with smtplib.SMTP(config['server'], config['port']) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(config['sender_email'], config['password'])
            server.sendmail(config['sender_email'], recipients, msg.as_string())
        
        return {
            "success": True,
            "message": f"Alerte envoyée à {len(recipients)} destinataire(s)",
            "sent_to": recipients,
            "timestamp": datetime.now().isoformat()
        }
        
    except smtplib.SMTPAuthenticationError:
        return {
            "success": False,
            "error": "Échec d'authentification SMTP. Vérifiez les identifiants.",
            "sent_to": []
        }
    except smtplib.SMTPException as e:
        return {
            "success": False,
            "error": f"Erreur SMTP: {str(e)}",
            "sent_to": []
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Erreur inattendue: {str(e)}",
            "sent_to": []
        }


def send_test_email(recipient: str) -> Dict[str, any]:
    """
    Envoie un email de test pour vérifier la configuration.
    
    Args:
        recipient: Adresse email de test
    
    Returns:
        Dictionnaire avec statut d'envoi
    """
    config = get_smtp_config()
    
    if not config['sender_email'] or not config['password']:
        return {
            "success": False,
            "error": "Configuration SMTP incomplète"
        }
    
    msg = EmailMessage()
    msg['Subject'] = "🧪 Test MEAL Alert System - CARIS"
    msg['From'] = config['sender_email']
    msg['To'] = recipient
    msg.set_content(f"""
Bonjour,

Ceci est un message de test du système d'alertes MEAL.

Si vous recevez ce message, la configuration SMTP est correcte.

Date: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

---
CARIS Foundation International
""")
    
    try:
        context = ssl.create_default_context()
        
        with smtplib.SMTP(config['server'], config['port']) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(config['sender_email'], config['password'])
            server.send_message(msg)
        
        return {
            "success": True,
            "message": f"Email de test envoyé à {recipient}"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def validate_email(email: str) -> bool:
    """Valide le format d'une adresse email."""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None
