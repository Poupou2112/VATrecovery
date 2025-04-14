from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from app.auth import get_current_user
from app.database import get_db
from app.models import Receipt
from sqlalchemy.orm import Session
from typing import Optional
from jinja2 import Template
import os

dashboard_router = APIRouter()


@dashboard_router.get("/dashboard", response_class=HTMLResponse)
def get_dashboard(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # Récupérer les reçus filtrés par client_id
    receipts = db.query(Receipt).filter(Receipt.client_id == current_user.client_id).all()

    # Exemple simple de rendu HTML
    html_template = """
    <html>
        <head><title>Dashboard</title></head>
        <body>
            <h1>Bienvenue sur le Dashboard, {{ user_email }}</h1>
            <p>Vous avez {{ receipts|length }} reçus enregistrés.</p>
            <ul>
                {% for receipt in receipts %}
                    <li>ID {{ receipt.id }} - TTC: {{ receipt.price_ttc }} €</li>
                {% endfor %}
            </ul>
        </body>
    </html>
    """
    template = Template(html_template)
    content = template.render(user_email=current_user.email, receipts=receipts)

    return HTMLResponse(content=content)
