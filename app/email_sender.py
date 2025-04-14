import smtplib
import imaplib
import email
from email.message import EmailMessage
from email.header import decode_header
from jinja2 import Template
import os
from loguru import logger
from app.config import get_settings
from typing import Optional, List, Dict, Any, Tuple

settings = get_settings()

class EmailService:
    def __init__(self):
        """Initialize email service with settings from configuration"""
        # SMTP Configuration
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER.get_secret_value()
        self.smtp_pass = settings.SMTP_PASS.get_secret_value()
        self.smtp_from = settings.SMTP_FROM
        
        # IMAP Configuration
        self.imap_server = settings.IMAP_SERVER
        self.imap_port = settings.IMAP_PORT
        self.imap_email = settings.IMAP_EMAIL
        self.imap_password = settings.IMAP_PASSWORD.get_secret_value()
        
        logger.info("✅ Email service initialized")
    
    def send_email(self, to: str, subject: str, body: str, 
                  attachments: Optional[List[str]] = None, 
                  html: bool = False) -> bool:
        """
        Send an email with error handling and attachments
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body content
            attachments: List of file paths to attach
            html: Whether body contains HTML content
            
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            msg = EmailMessage()
            msg["From"] = self.smtp_from
            msg["To"] = to
            msg["Subject"] = subject
            
            # Handle HTML or text content
            if html:
                msg.set_content("HTML version required")
                msg.add_alternative(body, subtype="html")
            else:
                msg.set_content(body)
            
            # Add attachments if provided
            if attachments:
                for attachment_path in attachments:
                    self._add_attachment(msg, attachment_path)
            
            # Send message
            with smtplib.SMTP_SSL(self.smtp_host, self.smtp_port, timeout=10) as smtp:
                smtp.login(self.smtp_user, self.smtp_pass)
                smtp.send_message(msg)
            
            logger.info(f"📧 Email sent to {to}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error sending email: {e}")
            return False
    
    def _add_attachment(self, msg: EmailMessage, path: str) -> None:
        """
        Add an attachment to the email message
        
        Args:
            msg: Email message object
            path: Path to the file to attach
            
        Raises:
            Exception: If file cannot be read or attached
        """
        if not os.path.exists(path):
            logger.error(f"Attachment file not found: {path}")
            raise FileNotFoundError(f"Attachment file not found: {path}")
            
        try:
            with open(path, "rb") as f:
                file_data = f.read()
                filename = os.path.basename(path)
                
                # Determine MIME type based on extension
                maintype, subtype = self._get_mime_type(path)
                
                msg.add_attachment(
                    file_data,
                    maintype=maintype,
                    subtype=subtype,
                    filename=filename
                )
                
                logger.debug(f"Added attachment: {filename} ({maintype}/{subtype})")
        except Exception as e:
            logger.error(f"❌ Error adding attachment {path}: {e}")
            raise
    
    def _get_mime_type(self, path: str) -> Tuple[str, str]:
        """
        Determine MIME type based on file extension
        
        Args:
            path: Path to the file
            
        Returns:
            Tuple of (maintype, subtype) for the file
        """
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
        
    def render_template(self, template_path: str, context: Dict[str, Any]) -> str:
        """
        Render a Jinja2 template with given context
        
        Args:
            template_path: Path to the template file
            context: Dictionary of variables for the template
            
        Returns:
            Rendered template as string
        """
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
                
            template = Template(template_content)
            return template.render(**context)
        except Exception as e:
            logger.error(f"❌ Error rendering template {template_path}: {e}")
            raise

def send_email(to: str, subject: str, body: str, 
              attachments: Optional[List[str]] = None, 
              html: bool = False) -> bool:
    """
    Convenience function to send an email without creating an EmailService instance
    
    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body content
        attachments: List of file paths to attach
        html: Whether body contains HTML content
        
    Returns:
        True if email sent successfully, False otherwise
    """
    service = EmailService()
    return service.send_email(to=to, subject=subject, body=body, 
                             attachments=attachments, html=html)
