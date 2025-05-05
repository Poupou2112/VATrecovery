from email.message import EmailMessage
import pytest
from app.email_sender import send_email
from unittest.mock import patch, MagicMock
import email
import smtplib

from_address = "from@example.com"

def test_send_email(monkeypatch):
    class DummySMTP:
        def __init__(self, *args, **kwargs): pass
        def login(self, *args, **kwargs): pass
        def send_message(self, msg): self.msg = msg
        def quit(self): pass
        def __enter__(self): return self
        def __exit__(self, *args): pass

    dummy_smtp = DummySMTP()
    monkeypatch.setattr("smtplib.SMTP", lambda *args, **kwargs: dummy_smtp)

    recipients = ["test@example.com"]
    subject = "Hello"
    body = "World"
    from_address = "from@example.com"
    result = send_email(subject=subject, body=body, recipients=recipients, from_address=from_address)

    assert result is True

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

    monkeypatch.setattr("smtplib.SMTP", lambda *args, **kwargs: MockSMTP())

    result = send_email(
        recipients=["recipient@example.com"],
        subject="Hello",
        body="Test body",
        from_address="from@example.com"
    )
    assert result is True


def test_send_email_multiple_recipients(monkeypatch):
    mock_sendmail = MagicMock()
    smtp_mock = MagicMock()
    smtp_mock.sendmail = mock_sendmail
    monkeypatch.setattr("smtplib.SMTP", lambda *args, **kwargs: smtp_mock)

    recipients = ["a@example.com", "b@example.com"]
    result = send_email(
        recipients=recipients,
        subject="Multi",
        body="Body",
        from_address="from@example.com"
    )
    assert result is True

def test_send_email_content_structure(monkeypatch):
    captured_msg = {}

    class DummySMTP:
        def send_message(self, msg):
            captured_msg["msg"] = msg
        def __enter__(self): return self
        def __exit__(self, *args): pass

    monkeypatch.setattr("smtplib.SMTP", lambda *args, **kwargs: DummySMTP())

    subject = "Hello"
    body = "Text content"
    html = "<h1>HTML</h1>"

    result = send_email(
        subject=subject,
        body=body,
        html=html,
        recipients=["x@y.com"],
        from_address="from@example.com"
    )
    assert result is True

    msg = captured_msg["msg"]
    parts = msg.iter_parts()
    assert any(part.get_content_type() == "text/plain" for part in parts)
    # Important: il faut appeler iter_parts() **à nouveau** car c'est un générateur
    parts = msg.iter_parts()
    assert any(part.get_content_type() == "text/html" for part in parts)

def test_send_email_raises_exception(monkeypatch):
    class FailingSMTP:
        def __enter__(self): return self
        def __exit__(self, exc_type, exc_val, exc_tb): pass
        def sendmail(self, *args, **kwargs): raise smtplib.SMTPException("SMTP error")

    monkeypatch.setattr("smtplib.SMTP", lambda *args, **kwargs: FailingSMTP())

    with pytest.raises(smtplib.SMTPException):
        send_email(
            recipients=["fail@example.com"],
            subject="Error",
            body="Trigger",
            from_address="from@example.com"
        )

def test_send_email_contains_subject_and_body(monkeypatch):
    smtp_instance = MagicMock()
    monkeypatch.setattr("smtplib.SMTP", lambda *args, **kwargs: smtp_instance)

    subject = "Important"
    body = "Urgent content"
    result = send_email(
        recipients=["test@x.com"],
        subject=subject,
        body=body,
        from_address="from@example.com"
    )
    assert result is True

def test_send_email_mime_headers(monkeypatch):
    smtp_instance = MagicMock()
    monkeypatch.setattr("smtplib.SMTP", lambda *args, **kwargs: smtp_instance)

    reply = "someone@reply.com"
    result = send_email(
        recipients=["rcpt@domain.com"],
        subject="Subj",
        body="Body",
        from_address="from@example.com",
        reply_to=reply
    )
    assert result is True

def test_send_email_without_reply_to(monkeypatch):
    smtp_instance = MagicMock()
    monkeypatch.setattr("smtplib.SMTP", lambda *args, **kwargs: smtp_instance)

    result = send_email(
        recipients=["recipient@example.com"],
        subject="Hello",
        body="Test body",
        from_address="from@example.com"
    )
    assert result is True
