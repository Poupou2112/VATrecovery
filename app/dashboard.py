from fastapi import APIRouter

dashboard_router = APIRouter()

@dashboard_router.get("/dashboard")
def dashboard_root():
    return {"message": "Dashboard coming soon"}
