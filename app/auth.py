from fastapi import Header, HTTPException, Depends, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session
from app.models import User
from app.init_db import get_db
from datetime import datetime, timedelta
import secrets
import os
from loguru import logger
from typing import Optional

# Configuration des sécurités
security_bearer = HTTPBearer()
security_basic = HTTPBasic()

# Nombre max de tentatives de connexion
MAX_LOGIN_ATTEMPTS = 5
# Temps de blocage en minutes
LOCKOUT_MINUTES = 15

# Cache des tentatives de connexion (IP -> {count, timestamp})
login_attempts = {}

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security_bearer),
    db: Session = Depends(get_db)
) -> User:
    """
    Authentifie un utilisateur via token API Bearer
    
    Args:
        credentials: Les credentials fournis via le header Authorization
        db: Session de base de données
        
    Returns:
        User: L'utilisateur authentifié
        
    Raises:
        HTTPException: Si l'authentification échoue
    """
    try:
        api_token = credentials.credentials
        user = db.query(User).filter_by(api_token=api_token).first()
        
        if not user:
            logger.warning(f"Tentative d'accès avec token invalide: {api_token[:10]}...")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token d'API invalide",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Vérifier si le token est expiré (si implémenté)
        # if user.token_expires_at and user.token_expires_at < datetime.utcnow():
        #     raise HTTPException(status_code=401, detail="Token expiré")
            
        return user
    except Exception as e:
        logger.error(f"Erreur d'authentification: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Erreur d'authentification",
            headers={"WWW-Authenticate": "Bearer"},
        )

def verify_admin_credentials(
    credentials: HTTPBasicCredentials = Depends(security_basic),
    request_ip: Optional[str] = Header(None, alias="X-Forwarded-For")
) -> str:
    """
    Authentifie un administrateur via Basic Auth pour le dashboard
    
    Args:
        credentials: Les credentials HTTP Basic
        request_ip: L'IP du client pour limiter les tentatives
        
    Returns:
        str: Le nom d'utilisateur authentifié
        
    Raises:
        HTTPException: Si l'authentification échoue
    """
    # Protection contre brute force avec rate limiting par IP
    ip = request_ip or "unknown"
    
    if ip in login_attempts:
        if login_attempts[ip]["count"] >= MAX_LOGIN_ATTEMPTS:
            # Vérifier si le temps de blocage est écoulé
            elapsed = datetime.utcnow() - login_attempts[ip]["timestamp"]
            if elapsed < timedelta(minutes=LOCKOUT_MINUTES):
                remaining = LOCKOUT_MINUTES - int(elapsed.total_seconds() / 60)
                logger.warning(f"Compte bloqué pour IP {ip} - Tentatives restantes: {remaining}min")
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Trop de tentatives. Réessayez dans {remaining} minutes."
                )
            else:
                # Réinitialiser le compteur après la période de blocage
                login_attempts[ip] = {"count": 0, "timestamp": datetime.utcnow()}
    else:
        login_attempts[ip] = {"count": 0, "timestamp": datetime.utcnow()}

    # Récupération des credentials depuis variables d'environnement
    admin_user = os.environ.get("DASHBOARD_USER")
    admin_pass = os.environ.get("DASHBOARD_PASS")
    
    if not admin_user or not admin_pass:
        logger.error("Credentials d'admin non configurées dans les variables d'environnement")
        raise HTTPException(status_code=500, detail="Erreur de configuration serveur")
    
    # Comparaison sécurisée des credentials
    is_valid_user = secrets.compare_digest(credentials.username, admin_user)
    is_valid_pass = secrets.compare_digest(credentials.password, admin_pass)
    
    if not (is_valid_user and is_valid_pass):
        # Incrémenter le compteur de tentatives
        login_attempts[ip]["count"] += 1
        login_attempts[ip]["timestamp"] = datetime.utcnow()
        
        logger.warning(f"Tentative d'authentification échouée depuis {ip} - Tentative {login_attempts[ip]['count']}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Accès refusé",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    # Réinitialiser le compteur après connexion réussie
    login_attempts[ip] = {"count": 0, "timestamp": datetime.utcnow()}
    
    return credentials.username
