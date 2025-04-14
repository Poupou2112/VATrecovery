from fastapi import FastAPI, Request, Header, HTTPException, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.openapi.docs import get_redoc_html
from sqlalchemy.orm import Session
from app.auth import auth_router
from app.api import api_router
from app.init_db import init_db, get_db
from app.models import User, Receipt
from app.receipts import get_receipts_by_client

import os

app = FastAPI(title="VATrecovery")

# Initialize the database
init_db()

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Auth routes
app.include_router(auth_router)
app.include_router(api_router, prefix="/api")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Render the index page"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/redoc", include_in_schema=False)
async def redoc_docs():
    """Render the ReDoc documentation"""
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title="VATrecovery - ReDoc"
    )


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request, 
    x_api_token: str = Header(default=None),
    db: Session = Depends(get_db)
):
    """Render the dashboard page with user receipts if authenticated"""
    if not x_api_token:
        raise HTTPException(status_code=401, detail="Token required")

    user = User.get_by_token(db, x_api_token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")

    receipts = get_receipts_by_client(db, user.client_id)
    return templates.TemplateResponse(
        "dashboard.html", 
        {"request": request, "receipts": receipts, "user": user}
    )
