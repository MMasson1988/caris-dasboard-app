import os
import smtplib
import ssl
from email.message import EmailMessage

email_sender = "mmasson@carisfoundationintl.org"
email_password = "Mirlande-88"
email_receiver = "mmasson@carisfoundationintl.org"

msg = EmailMessage()
msg["From"] = email_sender
msg["To"] = email_receiver
msg["Subject"] = "Message Automatique Python"
msg.set_content("Bonjour,\n\nCeci est un message automatique envoyé avec Python.\n\nCordialement,\nVotre Script")

context = ssl.create_default_context()

with smtplib.SMTP("smtp.gmail.com", 587) as server:
    server.ehlo()
    server.starttls(context=context)
    server.ehlo()
    server.login(email_sender, email_password)
    server.send_message(msg)
print("Email envoyé avec succès !")
