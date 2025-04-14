import logging
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from datetime import timedelta
from app import models, schemas
from app.database import get_db
from app.security import verify_password, create_access_token
from app.config import get_settings
from app.dependencies import get_current_user
from typing import List
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

# Configuration du logging
logger = logging.getLogger(__name__)

# Récupération des paramètres
settings = get_settings()

# Configuration du hachage de mot de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuration de l'authentification OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# Rate limiter pour prévenir les attaques par force brute
throttler = Throttler(rate_limit=5, time_window=60)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifie si le mot de passe en clair correspond au hash stocké."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Génère un hash sécurisé pour le mot de passe."""
    return pwd_context.hash(password)

def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """Authentifie un utilisateur par son nom d'utilisateur et mot de passe."""
    user = db.query(User).filter(User.email == username).first()
    if not user or not verify_password(password, user.password_hash):
        return None
    return user

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Crée un token JWT pour l'authentification."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    
    try:
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.SECRET_KEY.get_secret_value(), 
            algorithm=settings.JWT_ALGORITHM
        )
        return encoded_jwt
    except Exception as e:
        logger.error(f"Erreur lors de la création du token: {str(e)}")
        raise

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Récupère l'utilisateur courant à partir du token JWT."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Identifiants invalides",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY.get_secret_value(), 
            algorithms=[settings.JWT_ALGORITHM]
        )
        username: str = payload.get("sub")
        
        if username is None:
            raise credentials_exception
            
        user = db.query(User).filter(User.email == username).first()
        
        if user is None:
            raise credentials_exception
            
        return user
    except JWTError as e:
        logger.warning(f"Erreur JWT lors de l'authentification: {str(e)}")
        raise credentials_exception
    except Exception as e:
        logger.error(f"Erreur lors de l'authentification: {str(e)}")
        raise credentials_exception

# Création du router d'authentification
auth_router = APIRouter(prefix="/auth", tags=["authentication"])

@auth_router.post("/token", response_model=Token)
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    """
    Endpoint pour l'authentification et l'obtention d'un token JWT.
    Utilise un rate limiter pour prévenir les attaques par force brute.
    """
    # Appliquer le rate limiting
    client_ip = request.client.host
    await throttler.check(client_ip)
    
    start_time = time.time()
    
    # Authentifier l'utilisateur
    user = authenticate_user(db, form_data.username, form_data.password)
    
    if not user:
        # Ajout d'un délai fixe pour prévenir les attaques temporelles
        time.sleep(0.5)
        logger.warning(f"Tentative de connexion échouée pour {form_data.username} depuis {client_ip}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nom d'utilisateur ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Créer le token d'accès
    access_token = create_access_token(data={"sub": user.email})
    
    # Journaliser la connexion réussie
    logger.info(f"Connexion réussie pour {user.email} depuis {client_ip}")
    
    return {"access_token": access_token, "token_type": "bearer"}

@auth_router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    Endpoint pour l'enregistrement d'un nouvel utilisateur.
    """
    # Vérifier si l'utilisateur existe déjà
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Un utilisateur avec cette adresse email existe déjà"
        )
    
    # Créer le nouvel utilisateur
    hashed_password = get_password_hash(user.password)
    new_user = User(
        email=user.email,
        password_hash=hashed_password,
        full_name=user.full_name,
        company_name=user.company_name
    )
    
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        logger.info(f"Nouvel utilisateur enregistré: {user.email}")
        
        return UserResponse(
            id=new_user.id,
            email=new_user.email,
            full_name=new_user.full_name,
            company_name=new_user.company_name
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Erreur lors de l'enregistrement de l'utilisateur: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la création de l'utilisateur"
        )
