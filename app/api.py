from fastapi import APIRouter

from app.auth import get_current_user  # si besoin de dépendance globale

# Si tu as des sous-modules (ex: auth_routes, receipts, etc.)
# from app.routes.auth_routes import router as auth_router
# from app.routes.receipts import router as receipts_router

api_router = APIRouter()

# Ajoute ici les sous-routers si existants
# api_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
# api_router.include_router(receipts_router, prefix="/receipts", tags=["Receipts"])
