import pytest
from app.email_sender import send_email
from unittest.mock import patch, MagicMock
import email
import smtplib

@patch("smtplib.SMTP")
def test_send_email(mock_smtp):
    smtp_instance = MagicMock()
    mock_smtp.return_value.__enter__.return_value = smtp_instance
    smtp_instance.sendmail.return_value = {}

    result = send_email(
        recipients=["to@example.com"],
        subject="Test Subject",
        body="Test Body",
        from_address="from@example.com"
    )

    assert result is True
    smtp_instance.sendmail.assert_called_once()

def test_send_email_success(monkeypatch):
    captured = {}

    class MockSMTP:
        def sendmail(self, from_addr, to_addrs, msg):
            captured["msg"] = email.message_from_string(msg)
        def __enter__(self): return self
        def __exit__(self, *args): pass

    monkeypatch.setattr("smtplib.SMTP", lambda *a, **kw: MockSMTP())

    result = send_email(
        recipients=["someone@example.com"],
        subject="Subject Line",
        body="Email body",
        from_address="sender@example.com"
    )

    assert result is True
    msg = captured["msg"]
    assert msg["Subject"] == "Subject Line"
    assert "Email body" in msg.get_payload()

def test_send_email_html_structure(monkeypatch):
    captured = {}

    class DummySMTP:
        def sendmail(self, from_addr, to_addrs, msg):
            captured["msg"] = email.message_from_string(msg)
        def __enter__(self): return self
        def __exit__(self, *args): pass

    monkeypatch.setattr("smtplib.SMTP", lambda *a, **kw: DummySMTP())

    result = send_email(
        recipients=["html@test.com"],
        subject="HTML Subject",
        body="Plain text",
        html="<p>HTML content</p>",
        from_address="test@vatrecovery.com"
    )

    assert result is True
    msg = captured["msg"]
    assert msg.is_multipart()
    parts = list(msg.walk())
    assert any(p.get_content_type() == "text/plain" for p in parts)
    assert any(p.get_content_type() == "text/html" for p in parts)

def test_send_email_multiple_recipients(monkeypatch):
    called = {}

    class DummySMTP:
        def sendmail(self, from_addr, to_addrs, msg):
            called["to"] = to_addrs
            called["msg"] = msg
        def __enter__(self): return self
        def __exit__(self, *args): pass

    monkeypatch.setattr("smtplib.SMTP", lambda *a, **kw: DummySMTP())

    recipients = ["a@a.com", "b@b.com"]
    result = send_email(
        recipients=recipients,
        subject="Multi",
        body="Multiple Recipients",
        from_address="sender@example.com"
    )

    assert result is True
    assert called["to"] == recipients

def test_send_email_raises_exception(monkeypatch):
    class FailingSMTP:
        def sendmail(self, from_addr, to_addrs, msg):
            raise smtplib.SMTPException("SMTP error")
        def __enter__(self): return self
        def __exit__(self, *args): pass

    monkeypatch.setattr("smtplib.SMTP", lambda *a, **kw: FailingSMTP())

    result = send_email(
        recipients=["fail@example.com"],
        subject="Should fail",
        body="This should fail",
        from_address="sender@example.com"
    )

    assert result is False

def test_send_email_reply_to(monkeypatch):
    captured = {}

    class DummySMTP:
        def sendmail(self, from_addr, to_addrs, msg):
            captured["msg"] = email.message_from_string(msg)
        def __enter__(self): return self
        def __exit__(self, *args): pass

    monkeypatch.setattr("smtplib.SMTP", lambda *a, **kw: DummySMTP())

    result = send_email(
        recipients=["test@x.com"],
        subject="Reply-To Test",
        body="Reply body",
        from_address="sender@example.com",
        reply_to="reply@vatrecovery.com"
    )

    assert result is True
    assert captured["msg"]["Reply-To"] == "reply@vatrecovery.com"
