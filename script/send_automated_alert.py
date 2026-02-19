import os
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import date, datetime, timedelta
from pathlib import Path

# Tentative de chargement du fichier .env (pour le local)
try:
    from dotenv import load_dotenv
    # On cible explicitement votre dossier variables
    env_path = Path('.') / 'variables' / 'dot.env'
    load_dotenv(dotenv_path=env_path)
    print(f"ℹ️  Fichier .env chargé depuis : {env_path}")
except ImportError:
    print("ℹ️  python-dotenv non installé, utilisation des variables d'environnement système.")

# ==============================================================================
# LOGIQUE DE CALCUL DES DATES (Semaine Précédente)
# ==============================================================================
def previous_week_bounds(ref: date):
    current_monday = ref - timedelta(days=ref.weekday())
    prev_monday = current_monday - timedelta(days=7)
    prev_sunday = prev_monday + timedelta(days=6)
    return prev_monday, prev_sunday

def get_formatted_period():
    today = date.today()
    start_date, end_date = previous_week_bounds(today)
    months = {
        1: "janvier", 2: "février", 3: "mars", 4: "avril", 5: "mai", 6: "juin",
        7: "juillet", 8: "août", 9: "septembre", 10: "octobre", 11: "novembre", 12: "décembre"
    }
    return f"{start_date.day:02d} {months[start_date.month]} au {end_date.day:02d} {months[end_date.month]} {end_date.year}"

# ==============================================================================
# DESIGN DE L'EMAIL (Friendly)
# ==============================================================================
def create_html_body(period):
    urls = {
        "PTME": "https://caris-meal-app.pages.dev/tracking-ptme",
        "OEV": "https://caris-meal-app.pages.dev/tracking-oev",
        "MUSO": "https://caris-meal-app.pages.dev/tracking-muso",
        "JARDINAGE": "https://caris-meal-app.pages.dev/tracking-gardening",
        "NUTRITION": "https://caris-meal-app.pages.dev/tracking-nutrition"
    }
    primary_color = "#2E8B57"
    bg_color = "#f4f7f6"

    return f"""
    <!DOCTYPE html>
    <html>
    <body style="font-family: 'Segoe UI', Tahoma, sans-serif; background-color: {bg_color}; padding: 20px; color: #333;">
        <div style="background-color: #ffffff; padding: 30px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); max-width: 600px; margin: auto; border: 1px solid #eee;">
            <div style="text-align: center; border-bottom: 2px solid {primary_color}; padding-bottom: 15px; margin-bottom: 20px;">
                <h2 style="color: {primary_color}; margin: 0;">📊 Mise à jour des Rapports</h2>
                <p style="font-size: 14px; color: #666; margin: 5px 0 0 0;">Système MEAL - CARIS Foundation</p>
            </div>
            <p>Bonsoir Mme Elektra,<br>Bonsoir Dr. Charles,<br>Bonjour à tous,</p>
            <p>Nous avons le plaisir de vous informer que les rapports pour la période du <strong>{period}</strong> ont été mis à jour et sont désormais disponibles sur le dashboard.</p>
            <div style="background-color: #f9f9f9; padding: 20px; border-radius: 6px; text-align: center;">
                <a href="{urls['PTME']}" style="display: inline-block; padding: 10px 18px; margin: 4px; background-color: {primary_color}; color: #ffffff; text-decoration: none; border-radius: 5px; font-weight: bold; font-size: 13px;">📍 PTME</a>
                <a href="{urls['OEV']}" style="display: inline-block; padding: 10px 18px; margin: 4px; background-color: {primary_color}; color: #ffffff; text-decoration: none; border-radius: 5px; font-weight: bold; font-size: 13px;">📍 OEV</a>
                <a href="{urls['MUSO']}" style="display: inline-block; padding: 10px 18px; margin: 4px; background-color: {primary_color}; color: #ffffff; text-decoration: none; border-radius: 5px; font-weight: bold; font-size: 13px;">📍 MUSO</a><br>
                <a href="{urls['JARDINAGE']}" style="display: inline-block; padding: 10px 18px; margin: 4px; background-color: {primary_color}; color: #ffffff; text-decoration: none; border-radius: 5px; font-weight: bold; font-size: 13px;">📍 JARDINAGE</a>
                <a href="{urls['NUTRITION']}" style="display: inline-block; padding: 10px 18px; margin: 4px; background-color: {primary_color}; color: #ffffff; text-decoration: none; border-radius: 5px; font-weight: bold; font-size: 13px;">📍 NUTRITION</a>
            </div>
            <p style="margin-top: 25px;">Cordialement,</p>
            <div style="margin-top: 40px; padding-top: 15px; border-top: 1px solid #eee; text-align: center; font-size: 11px; color: #999;">
                <p>Ceci est une notification automatique générée par le pipeline CARIS.<br>© 2026 CARIS Foundation International</p>
            </div>
        </div>
    </body>
    </html>
    """

def send_update_notification():
    period = get_formatted_period()
    
    # Récupération des variables (chargées depuis variables/dot.env ou GitHub env)
    sender = os.getenv("SMTP_SENDER")
    password = os.getenv("SMTP_PASSWORD")
    to_emails = os.getenv("SMTP_RECEIVERS", "")
    cc_emails = os.getenv("SMTP_CC", "")
    
    if not sender or not password:
        print("❌ Erreur : Identifiants SMTP manquants dans le fichier .env ou l'environnement.")
        return

    to_list = [e.strip() for e in to_emails.split(",") if e.strip()]
    cc_list = [e.strip() for e in cc_emails.split(",") if e.strip()]

    msg = MIMEMultipart('alternative')
    msg['Subject'] = f"✨ Mise à jour Rapports Dashboard | {period}"
    msg['From'] = f"MEAL CARIS <{sender}>"
    msg['To'] = ", ".join(to_list)
    if cc_list:
        msg['Cc'] = ", ".join(cc_list)

    msg.attach(MIMEText(create_html_body(period), 'html'))

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls(context=context)
            server.login(sender, password)
            server.sendmail(sender, to_list + cc_list, msg.as_string())
        print(f"✅ Notification envoyée avec succès pour : {period}")
    except Exception as e:
        print(f"❌ Erreur SMTP : {e}")

if __name__ == "__main__":
    send_update_notification()