import pytest
from app.reminder import send_reminder
from app.database import Base
from app.database import engine
from app.models import Receipt, User
from datetime import datetime, timedelta
from app.init_db import SessionLocal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base
from unittest.mock import AsyncMock, patch
from app.reminder import send_reminders

engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

@pytest.mark.asyncio
@patch("app.reminder.Receipt.get_pending_receipts", return_value=[])
@patch("app.reminder.send_email_reminder")
async def test_send_reminders_no_pending_receipts(mock_send_email, mock_get_receipts):
    await send_reminders()
    
    # Vérifie que la fonction de récupération a bien été appelée
    mock_get_receipts.assert_called_once()
    
    # Vérifie qu'aucun e-mail n'est envoyé si la liste est vide
    mock_send_email.assert_not_called()
async def test_send_reminder_with_receipt(monkeypatch):
    class DummyReceipt:
        email_sent_to = "dummy@test.com"
        file = "dummy.pdf"
        user = type("User", (), {"client_id": "123"})
        id = 1

    async def mock_send_email_async(*args, **kwargs):
        return True

    monkeypatch.setattr(reminder, "get_pending_receipts", lambda db: [DummyReceipt()])
    monkeypatch.setattr(reminder, "send_email_async", mock_send_email_async)

    await reminder.send_reminder(db=MagicMock())

def test_send_reminder_mock(client, db):
    class FakeQuery:
        def filter(self, *args, **kwargs):
            return self
        def all(self):
            return [Receipt(
                id=1,
                file="test.jpg",
                email_sent=True,
                invoice_received=False,
                email_sent_to="contact@test.com",
                created_at=datetime.utcnow() - timedelta(days=10),
                client_id=123,
                date="01/04/2025",
                price_ttc=28.45
            )]
        def filter_by(self, **kwargs):
            return self
        def first(self):
            return User(client_id=123, email="user@example.com")

    class FakeSession:
        def query(self, model): return FakeQuery()
        def close(self): pass

    monkeypatch.setattr("app.reminder.SessionLocal", lambda: FakeSession())
    async def fake_send_email(*args, **kwargs): return True
    monkeypatch.setattr("app.reminder.send_email", fake_send_email)

    sent = send_reminder(db)
    assert sent == 1
