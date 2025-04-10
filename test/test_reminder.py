from app.reminder import send_reminder
from app.models import Receipt, User
from datetime import datetime, timedelta

def test_send_reminder_mock(monkeypatch):
    class FakeQuery:
        def filter(self, *args, **kwargs): return self
        def filter_by(self, *args, **kwargs): return self
        def all(self):  # Pour la récupération des reçus à relancer
            return [Receipt(
                id=1,
                file="test.jpg",
                email_sent=True,
                invoice_received=False,
                email_sent_to="contact@test.com",
                created_at=datetime.utcnow() - timedelta(days=10),
                client_id="reclaimy"
            )]
        def first(self):  # Pour récupérer l'utilisateur
            return User(api_token="token", client_id="reclaimy")

    class FakeSession:
        def query(self, model): return FakeQuery()
        def close(self): pass

    monkeypatch.setattr("app.reminder.SessionLocal", lambda: FakeSession())
    monkeypatch.setattr("app.reminder.send_email", lambda *args, **kwargs: True)

    sent = send_reminder()
    assert sent == 1
