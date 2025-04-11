import smtplib
import imaplib
import email
from email.message import EmailMessage
from email.header import decode_header
from jinja2 import Template
import os
from loguru import logger
from app.config import get_settings
from typing import Optional, List, Dict, Any

settings = get_settings()

class EmailService:
    def __init__(self):
        # Configuration SMTP
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER.get_secret_value()
        self.smtp_pass = settings.SMTP_PASS.get_secret_value()
        self.smtp_from = settings.SMTP_FROM
        
        # Configuration IMAP
        self.imap_server = settings.IMAP_SERVER
        self.imap_port = settings.IMAP_PORT
        self.imap_email = settings.IMAP_EMAIL
        self.imap_password = settings.IMAP_PASSWORD.get_secret_value()
        
        logger.info("✅ Service email initialisé")
    
    def send_email(self, to: str, subject: str, body: str, 
                  attachments: Optional[List[str]] = None, 
                  html: bool = False) -> bool:
        """Envoie un email avec gestion des erreurs et attachements"""
        try:
            msg = EmailMessage()
            msg["From"] = self.smtp_from
            msg["To"] = to
            msg["Subject"] = subject
            
            # Gestion du contenu HTML ou texte
            if html:
                msg.set_content("Version HTML requise")
                msg.add_alternative(body, subtype="html")
            else:
                msg.set_content(body)
            
            # Ajout des pièces jointes
            if attachments:
                for attachment_path in attachments:
                    self._add_attachment(msg, attachment_path)
            
            # Envoi du message
            with smtplib.SMTP_SSL(self.smtp_host, self.smtp_port) as smtp:
                smtp.login(self.smtp_user, self.smtp_pass)
                smtp.send_message(msg)
            
            logger.info(f"📧 Email envoyé à {to}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur envoi email: {e}")
            return False
    
    def _add_attachment(self, msg: EmailMessage, path: str) -> None:
        """Ajoute une pièce jointe au message"""
        try:
            with open(path, "rb") as f:
                file_data = f.read()
                filename = os.path.basename(path)
                
                # Déterminer le type MIME en fonction de l'extension
                maintype, subtype = self._get_mime_type(path)
                
                msg.add_attachment(
                    file_data,
                    maintype=maintype,
                    subtype=subtype,
                    filename=filename
                )
        except Exception as e:
            logger.error(f"❌ Erreur ajout pièce jointe {path}: {e}")
            raise
    
    def _get_mime_type(self, path: str) -> tuple:
        """Détermine le type MIME en fonction de l'extension du fichier"""
        ext = os.path.splitext(path)[1].lower()
        
        mime_types = {
            '.pdf': ('application', 'pdf'),
            '.jpg': ('image', 'jpeg'),
            '.jpeg': ('image', 'jpeg'),
            '.png': ('image', 'png'),
            '.txt': ('text', 'plain'),
            '.doc': ('application', 'msword'),
            '.docx': ('application', 'vnd.openxmlformats-officedocument.wordprocessingml.document'),
            '.xls': ('application', 'vnd.ms-excel'),
            '.xlsx': ('application', 'vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
        }
        
        return mime_types.get(ext, ('application', 'octet-stream'))
