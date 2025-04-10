from app.reminder import send_reminder
from app.models import Receipt
from datetime import datetime, timedelta

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
                created_at=datetime.utcnow() - timedelta(days=10)
            )]

    class FakeSession:
        def query(self, model): return FakeQuery()
        def close(self): pass

    monkeypatch.setattr("app.reminder.SessionLocal", lambda: FakeSession())
    monkeypatch.setattr("app.reminder.send_email", lambda *args, **kwargs: True)

    sent = send_reminder()
    assert sent == 1
