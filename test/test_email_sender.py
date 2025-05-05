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

    subject = "Hello"
    body = "World"
    from_address, to_addresses, msg = send_email(
        to_addresses=["to@example.com"],
        subject=subject,
        body=body,
        from_address="from@example.com"
)

    assert from_address == "noreply@vatrecovery.com"
    assert to_addresses == to
    assert subject in message["Subject"]
    assert body in message.get_payload()[0].get_payload()

def test_send_email_html_structure(monkeypatch):
    class DummySMTP:
        def sendmail(self, from_addr, to_addrs, msg): pass
        def __enter__(self): return self
        def __exit__(self, *args): pass
    monkeypatch.setattr("smtplib.SMTP", lambda *args, **kwargs: DummySMTP())

    subject = "HTML Test"
    body = "Plain text"
    html = "<h1>HTML content</h1>"

    _, _, msg = send_email(subject=subject, body=body, to_addresses=["x@y.com"], html=html)

    parts = msg.get_payload()
    assert any(part.get_content_type() == "text/plain" for part in parts)
    assert any(part.get_content_type() == "text/html" for part in parts)

def test_send_email_success(monkeypatch):
    class MockSMTP:
        def __init__(self, *args, **kwargs): pass
        def sendmail(self, from_addr, to_addrs, msg): pass
        def __enter__(self): return self
        def __exit__(self, *args): pass

    monkeypatch.setattr("smtplib.SMTP", lambda *args, **kwargs: MockSMTP())

    subject = "Hello"
    body = "Test body"
    to = ["recipient@example.com"]

    subject = "Hello"
    body = "World"
    from_address, to_addresses, msg = send_email(
        to_addresses=["to@example.com"],
        subject=subject,
        body=body,
        from_address="from@example.com"
)

    assert from_address == "noreply@vatrecovery.com"
    assert to_addresses == to
    assert subject in message["Subject"]
    assert body in message.get_payload()[0].get_payload()

def test_send_email_multiple_recipients(monkeypatch):
    mock_sendmail = MagicMock()
    smtp_mock = MagicMock()
    smtp_mock.sendmail = mock_sendmail
    monkeypatch.setattr("smtplib.SMTP", lambda *args, **kwargs: smtp_mock)

    recipients = ["a@example.com", "b@example.com"]
    
    subject = "Hello"
    body = "World"
    from_address, to_addresses, msg = send_email(
        to_addresses=["to@example.com"],
        subject=subject,
        body=body,
        from_address="from@example.com"
)
    assert from_address == "noreply@vatrecovery.com"
    assert to_addresses == to
    assert subject in message["Subject"]
    assert body in message.get_payload()[0].get_payload()

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

    subject = "Hello"
    body = "World"
    from_address, to_addresses, msg = send_email(
        to_addresses=["to@example.com"],
        subject=subject,
        body=body,
        from_address="from@example.com"
)
    assert from_address == "noreply@vatrecovery.com"
    assert to_addresses == to
    assert subject in message["Subject"]
    assert body in message.get_payload()[0].get_payload()

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

    subject = "Hello"
    body = "World"
    from_address, to_addresses, msg = send_email(
        to_addresses=["to@example.com"],
        subject=subject,
        body=body,
        from_address="from@example.com"
)
    assert from_address == "noreply@vatrecovery.com"
    assert to_addresses == to
    assert subject in message["Subject"]
    assert body in message.get_payload()[0].get_payload()
    
def test_send_email_contains_subject_and_body(monkeypatch):
    smtp_instance = MagicMock()
    monkeypatch.setattr("smtplib.SMTP", lambda *args, **kwargs: smtp_instance)

    subject = "Important"
    body = "Urgent content"
    subject = "Hello"
    body = "World"
    from_address, to_addresses, msg = send_email(
        to_addresses=["to@example.com"],
        subject=subject,
        body=body,
        from_address="from@example.com"
)
    assert from_address == "noreply@vatrecovery.com"
    assert to_addresses == to
    assert subject in message["Subject"]
    assert body in message.get_payload()[0].get_payload()

def test_send_email_mime_headers(monkeypatch):
    smtp_instance = MagicMock()
    monkeypatch.setattr("smtplib.SMTP", lambda *args, **kwargs: smtp_instance)

    reply = "someone@reply.com"
    subject = "Hello"
    body = "World"
    from_address, to_addresses, msg = send_email(
        to_addresses=["to@example.com"],
        subject=subject,
        body=body,
        from_address="from@example.com"
)
    assert from_address == "noreply@vatrecovery.com"
    assert to_addresses == to
    assert subject in message["Subject"]
    assert body in message.get_payload()[0].get_payload()

def test_send_email_without_reply_to(monkeypatch):
    smtp_instance = MagicMock()
    monkeypatch.setattr("smtplib.SMTP", lambda *args, **kwargs: smtp_instance)

    subject = "Hello"
    body = "World"
    from_address, to_addresses, msg = send_email(
        to_addresses=["to@example.com"],
        subject=subject,
        body=body,
        from_address="from@example.com"
)
    assert from_address == "noreply@vatrecovery.com"
    assert to_addresses == to
    assert subject in message["Subject"]
    assert body in message.get_payload()[0].get_payload()
