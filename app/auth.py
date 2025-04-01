
from fastapi import APIRouter
from fastapi.responses import RedirectResponse
import requests
import os

router = APIRouter()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

@router.get("/login")
def login():
    url = f"https://example.com/oauth/authorize?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope=read"
    return RedirectResponse(url)

@router.get("/callback")
def callback(code: str):
    token_url = "https://example.com/oauth/token"
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    r = requests.post(token_url, data=data)
    tokens = r.json()
    return tokens
