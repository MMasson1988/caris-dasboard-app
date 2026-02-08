"""
Service WhatsApp automatisé via PyWhatKit
PyWhatKit automatise WhatsApp Web - ouvre le navigateur, tape et envoie le message automatiquement.

Prérequis:
- pip install pywhatkit
- WhatsApp Web doit être connecté dans votre navigateur par défaut
"""
import urllib.parse
from typing import Tuple
from datetime import datetime


def send_whatsapp_instant(phone_number: str, message: str) -> Tuple[bool, str]:
    """
    Envoie un message WhatsApp instantanément via PyWhatKit.
    
    Args:
        phone_number: Numéro avec indicatif pays (ex: 50947368767)
        message: Message à envoyer
    
    Returns:
        Tuple (succès: bool, message: str)
    """
    try:
        import pywhatkit as kit
        
        # Nettoyer le numéro
        clean_phone = phone_number.replace(" ", "").replace("-", "")
        if not clean_phone.startswith("+"):
            clean_phone = "+" + clean_phone
        
        # Envoyer instantanément (ouvre WhatsApp Web et envoie)
        # wait_time=15 : attend 15 secondes que WhatsApp Web charge
        # tab_close=True : ferme l'onglet après envoi
        kit.sendwhatmsg_instantly(
            phone_no=clean_phone,
            message=message,
            wait_time=15,
            tab_close=True
        )
        
        return True, "Message WhatsApp envoyé avec succès!"
        
    except ImportError:
        return False, "PyWhatKit n'est pas installé. Exécutez: pip install pywhatkit"
    except Exception as e:
        error_msg = str(e)
        if "not connected" in error_msg.lower():
            return False, "WhatsApp Web n'est pas connecté. Scannez le QR code d'abord."
        return False, f"Erreur: {error_msg}"


def send_whatsapp_scheduled(
    phone_number: str, 
    message: str, 
    hour: int, 
    minute: int
) -> Tuple[bool, str]:
    """
    Programme l'envoi d'un message WhatsApp à une heure précise.
    
    Args:
        phone_number: Numéro avec indicatif pays
        message: Message à envoyer
        hour: Heure (0-23)
        minute: Minute (0-59)
    
    Returns:
        Tuple (succès: bool, message: str)
    """
    try:
        import pywhatkit as kit
        
        clean_phone = phone_number.replace(" ", "").replace("-", "")
        if not clean_phone.startswith("+"):
            clean_phone = "+" + clean_phone
        
        kit.sendwhatmsg(
            phone_no=clean_phone,
            message=message,
            time_hour=hour,
            time_min=minute,
            tab_close=True
        )
        
        return True, f"Message programmé pour {hour:02d}:{minute:02d}"
        
    except ImportError:
        return False, "PyWhatKit n'est pas installé. Exécutez: pip install pywhatkit"
    except Exception as e:
        return False, f"Erreur: {str(e)}"


def format_mas_alert_whatsapp(
    total_mas: int,
    cas_critiques: list,
    date_rapport: str
) -> str:
    """
    Formate une alerte MAS pour WhatsApp.
    """
    message = f"""🚨 *ALERTE NUTRITION - MAS DÉTECTÉS*

📅 Date: {date_rapport}
⚠️ Total cas MAS: *{total_mas}*

"""
    
    if cas_critiques:
        message += "👶 *Cas prioritaires:*\n"
        for i, cas in enumerate(cas_critiques[:5], 1):
            nom = cas.get('nom', 'N/A')
            age = cas.get('age', 'N/A')
            bureau = cas.get('bureau', 'N/A')
            message += f"{i}. {nom} ({age}) - {bureau}\n"
    
    message += """
📋 *Action requise:*
Connectez-vous à l'application MEAL pour voir les détails.

🏥 CARIS Foundation International
"""
    
    return message
