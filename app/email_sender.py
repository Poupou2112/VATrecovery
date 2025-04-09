# test/test_email_sender.py

import pytest
from app.email_sender import send_email

def test_send_email_mock(monkeypatch):
    class MockSMTP:
        def __init__(self, *args, **kwargs):
            self.sent_message = None

        def login(self, *args, **kwargs):
            pass

        def send_message(self, msg):
            self.sent_message = msg

        def quit(self):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

    mock_smtp = MockSMTP()
    monkeypatch.setattr("smtplib.SMTP_SSL", lambda *args, **kwargs: mock_smtp)

    result = send_email(
        to="test@example.com",
        subject="Test Subject",
        body="This is a test email body.",
        attachment_path=None
    )

    assert result is True
    assert mock_smtp.sent_message is not None
    assert mock_smtp.sent_message["To"] == "test@example.com"
    assert mock_smtp.sent_message["Subject"] == "Test Subject"
