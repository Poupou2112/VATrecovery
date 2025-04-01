
from fastapi import FastAPI
from app import auth, receipts, email_sender

app = FastAPI()
app.include_router(auth.router)
