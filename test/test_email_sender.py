from email.message import EmailMessage
import pytest
from app.email_sender import send_email

def test_send_email_success(monkeypatch):
    class MockSMTP:
        def __init__(self, *args, **kwargs): pass
        def login(self, *args, **kwargs): pass
        def send_message(self, msg):
            assert isinstance(msg, EmailMessage)
            assert msg["To"] == "recipient@example.com"
            assert msg["Subject"] == "Hello"
            assert msg.get_content().strip() == "Test body"
        def quit(self): pass
        def __enter__(self): return self
        def __exit__(self, *args): pass

    monkeypatch.setattr("smtplib.SMTP_SSL", lambda *args, **kwargs: MockSMTP())

    result = send_email(
        to="recipient@example.com",
        subject="Hello",
        body="Test body"
    )

    assert result is True
