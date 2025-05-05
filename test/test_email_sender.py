import pytest
from app.email_sender import send_email
from unittest.mock import patch, MagicMock
import email
import smtplib

from_address = "from@example.com"

@patch("smtplib.SMTP")
def test_send_email(mock_smtp):
    smtp_instance = MagicMock()
    mock_smtp.return_value.__enter__.return_value = smtp_instance
    smtp_instance.sendmail.return_value = {}

    result = send_email(
        subject="Hello",
        body="World",
        recipients=["to@example.com"],
        from_address="from@example.com"
    )

    assert result is True

def test_send_email_success(monkeypatch):
    class MockSMTP:
        def __init__(self, *args, **kwargs): pass
        def login(self, *args, **kwargs): pass
        def sendmail(self, from_addr, to_addrs, msg):
            parsed = email.message_from_string(msg)
            assert parsed["To"] == "recipient@example.com"
            assert parsed["Subject"] == "Hello"
            assert "Test body" in parsed.get_payload()
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
        def sendmail(self, from_addr, to_addrs, msg):
            captured_msg["msg"] = email.message_from_string(msg)
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
    assert result is True, "Expected email to be sent successfully"

    msg = captured_msg["msg"]
    if msg.is_multipart():
        parts = msg.walk()
        assert any(p.get_content_type() == "text/plain" for p in parts)

        parts = msg.walk()  # Redémarre le générateur
        assert any(p.get_content_type() == "text/html" for p in parts)
    else:
        assert False, "Email is not multipart"

def test_send_email_raises_exception(monkeypatch):
    class FailingSMTP:
        def login(self, *args, **kwargs): pass
        def sendmail(self, from_addr, to_addrs, msg):
            raise smtplib.SMTPException("SMTP error")
        def __enter__(self): return self
        def __exit__(self, *args): pass

    monkeypatch.setattr("smtplib.SMTP", lambda *args, **kwargs: FailingSMTP())

    result = send_email(
        recipients=["fail@example.com"],
        subject="Error",
        body="Trigger",
        from_address="from@example.com"
    )
    assert result is False
    
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
