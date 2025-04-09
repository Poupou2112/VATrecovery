from app.reminder import send_reminder
from app.models import Receipt
from datetime import datetime

def test_send_reminder_mock(monkeypatch):
    # Simule la base de données avec un ticket à relancer
    class FakeSession:
        def query(self, model):
            class Filter:
                def filter(self, *args, **kwargs):
                    return [Receipt(
                        id=1,
                        file="test.jpg",
                        email_sent=True,
                        invoice_received=False,
                        email_sent_to="contact@test.com",
                        created_at=datetime.now()
                    )]
            return Filter()
        def close(self): pass

    monkeypatch.setattr("app.reminder.SessionLocal", lambda: FakeSession())

    sent_count = send_reminder()
    assert isinstance(sent_count, int)
