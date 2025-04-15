from app.reminder import send_reminder
from app.models import Receipt, User
from datetime import datetime, timedelta
from app.init_db import SessionLocal
db = SessionLocal()
Base.metadata.create_all(bind=engine)

def test_send_reminder_mock(monkeypatch):
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
    monkeypatch.setattr("app.reminder.send_email", lambda *args, **kwargs: True)

    sent = send_reminder(db)
    assert sent == 1
