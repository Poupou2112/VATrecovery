
import smtplib
from email.message import EmailMessage
from typing import Union, List, Optional

DEFAULT_FROM_ADDRESS = "noreply@vatrecovery.com"

def send_email(
    recipients: Union[str, List[str]],
    subject: str,
    body: str,
    from_address: str = DEFAULT_FROM_ADDRESS,
    reply_to: Optional[str] = None,
    html: Optional[str] = None
) -> bool:
    """
    Envoie un email en texte brut et optionnellement en HTML.
    :param recipients: adresse unique ou liste d'adresses
    :param subject: objet du mail
    :param body: contenu en texte brut
    :param from_address: adresse d'expédition
    :param reply_to: adresse de reply-to (facultatif)
    :param html: contenu HTML (facultatif)
    :return: True si envoi réussi, sinon exception propagée
    """
    # Normalise la liste des destinataires
    if isinstance(recipients, str):
        to_addrs = [recipients]
    else:
        to_addrs = recipients

    # Construction du message
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = from_address
    msg["To"] = ", ".join(to_addrs)
    if reply_to:
        msg["Reply-To"] = reply_to

    # Contenu texte
    msg.set_content(body)

    # Contenu HTML en alternative
    if html:
        msg.add_alternative(html, subtype="html")

    # Envoi
    try:
        # Vous pouvez remplacer "localhost" / port si besoin
        with smtplib.SMTP("localhost") as server:
            server.sendmail(from_address, to_addrs, msg.as_string())
        return True
    except Exception:
        # On laisse l'exception (SMTPException, RuntimeError, etc.) remonter
        raise
