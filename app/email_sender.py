import smtplib
from email.message import EmailMessage
from typing import Union, List, Optional

DEFAULT_FROM_ADDRESS = "noreply@vatrecovery.com"

def send_email(
    to_addresses: Union[str, List[str]],
    subject: str,
    body: str,
    from_address: str = DEFAULT_FROM_ADDRESS,
    html: Optional[str] = None,
    reply_to: Optional[str] = None,
) -> bool:
    """
    Envoie un email via SMTP en mode texte ou multipart (texte + HTML).
    - to_addresses : une adresse ou une liste d’adresses
    - subject      : objet du message
    - body         : texte brut
    - html         : contenu HTML optionnel
    - reply_to     : adresse de réponse optionnelle
    """
    # Normalisation en liste
    if isinstance(to_addresses, str):
        to_list = [to_addresses]
    else:
        to_list = to_addresses

    # Construction du message
    msg = EmailMessage()
    msg["From"] = from_address
    msg["To"] = ", ".join(to_list)
    msg["Subject"] = subject
    if reply_to:
        msg["Reply-To"] = reply_to

    if html:
        # multipart alternative : texte + HTML
        msg.set_content(body)
        msg.add_alternative(html, subtype="html")
    else:
        msg.set_content(body)

    # Envoi SMTP
    smtp = smtplib.SMTP()  # les tests patchent smtplib.SMTP
    with smtp:
        smtp.sendmail(from_address, to_list, msg.as_string())

    return True
