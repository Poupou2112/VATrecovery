# app/security.py
import re
import secrets
import string
import html
from typing import Optional, Dict, Any, Union
import os
from datetime import datetime, timedelta
from email_validator import validate_email as validate_email_format, EmailNotValidError
from jose import JWTError, jwt
from passlib.context import CryptContext

# Configuration
SECRET_KEY = os.getenv("SESSION_SECRET", "")
if not SECRET_KEY:
    raise ValueError("SESSION_SECRET must be set in environment variables")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Instance pour hachage des mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def sanitize_input(input_text: str) -> str:
    """
    Nettoie une chaîne de caractères des éventuelles attaques XSS.
    
    Args:
        input_text: Texte à nettoyer
        
    Returns:
        Le texte nettoyé
    """
    if not input_text:
        return ""
    # Échappement HTML pour prévenir les attaques XSS
    return html.escape(input_text)


def validate_email(email: str) -> bool:
    """
    Valide un format d'email.
    
    Args:
        email: L'email à valider
        
    Returns:
        True si l'email est valide, False sinon
    """
    try:
        validate_email_format(email)
        return True
    except EmailNotValidError:
        return False


def generate_password() -> str:
    """
    Génère un mot de passe aléatoire sécurisé.
    
    Returns:
        Un mot de passe aléatoire
    """
    alphabet = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(alphabet) for _ in range(16))
    return password


def get_password_hash(password: str) -> str:
    """
    Hache un mot de passe.
    
    Args:
        password: Le mot de passe en clair
        
    Returns:
        Le hash du mot de passe
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Vérifie un mot de passe par rapport à son hash.
    
    Args:
        plain_password: Mot de passe en clair
        hashed_password: Hash du mot de passe
        
    Returns:
        True si le mot de passe correspond au hash, False sinon
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Crée un token JWT d'accès.
    
    Args:
        data: Données à encoder dans le token
        expires_delta: Délai d'expiration du token
        
    Returns:
        Le token JWT encodé
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Décode un token JWT d'accès.
    
    Args:
        token: Le token JWT à décoder
        
    Returns:
        Les données décodées du token ou None si invalide
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def secure_filename(filename: str) -> str:
    """
    Nettoie un nom de fichier pour le rendre sûr.
    
    Args:
        filename: Le nom de fichier à nettoyer
        
    Returns:
        Le nom de fichier sécurisé
    """
    # Enlever les caractères dangereux
    filename = re.sub(r'[^\w\s.-]', '', filename)
    # Nettoyer les espaces et caractères superflus
    filename = filename.strip().replace(' ', '_')
    # Limiter la longueur
    if len(filename) > 255:
        filename = filename[:255]
    return filename
