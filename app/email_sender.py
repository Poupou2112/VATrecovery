import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_email(subject, body, recipients, from_address="noreply@vatrecovery.com", html=None, reply_to=None):
    try:
        # Construire le message
        msg = MIMEMultipart("alternative" if html else "mixed")
        msg["Subject"] = subject
        msg["From"] = from_address
        msg["To"] = ", ".join(recipients)
        if reply_to:
            msg["Reply-To"] = reply_to

        # Ajouter les parties texte et HTML
        part1 = MIMEText(body, "plain")
        msg.attach(part1)
        if html:
            part2 = MIMEText(html, "html")
            msg.attach(part2)

        # Envoyer le mail
        with smtplib.SMTP("localhost") as server:
            server.sendmail(from_address, recipients, msg.as_string())

        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
