import pytest
from app.email_sender import send_email
from unittest.mock import patch, MagicMock
import email


def test_send_email_success(monkeypatch):
    class MockSMTP:
        def __init__(self, *args, **kwargs): pass
        def sendmail(self, from_addr, to_addrs, msg): pass
        def __enter__(self): return self
        def __exit__(self, *args): pass

    monkeypatch.setattr("smtplib.SMTP", lambda *args, **kwargs: MockSMTP())

    result = send_email(
        recipients=["recipient@example.com"],
        subject="Hello",
        body="Test body",
        from_address="no-reply@vatrecovery.com"
    )

    assert result is True


def test_send_email_multiple_recipients(monkeypatch):
    smtp_mock = MagicMock()
    monkeypatch.setattr("smtplib.SMTP", lambda *args, **kwargs: smtp_mock)

    recipients = ["a@example.com", "b@example.com"]
    send_email(
        recipients=recipients,
        subject="Group mail",
        body="Hello team!",
        from_address="sender@example.com"
    )

    smtp_mock.sendmail.assert_called_once()
    args = smtp_mock.sendmail.call_args[0]
    assert set(recipients).issubset(set(args[1]))


def test_send_email_html_structure(monkeypatch):
    captured = {}

    class DummySMTP:
        def sendmail(self, from_addr, to_addrs, msg):
            captured["msg"] = email.message_from_string(msg)
        def __enter__(self): return self
        def __exit__(self, *args): pass

    monkeypatch.setattr("smtplib.SMTP", lambda *args, **kwargs: DummySMTP())

    result = send_email(
        recipients=["x@y.com"],
        subject="Test",
        body="Text version",
        html="<h1>HTML content</h1>",
        from_address="sender@example.com"
    )

    assert result is True
    msg = captured["msg"]
    parts = msg.walk()
    assert any(p.get_content_type() == "text/plain" for p in parts)
    parts = msg.walk()
    assert any(p.get_content_type() == "text/html" for p in parts)


def test_send_email_contains_subject_and_body(monkeypatch):
    captured = {}

    class DummySMTP:
        def sendmail(self, from_addr, to_addrs, msg):
            captured["msg"] = email.message_from_string(msg)
        def __enter__(self): return self
        def __exit__(self, *args): pass

    monkeypatch.setattr("smtplib.SMTP", lambda *args, **kwargs: DummySMTP())

    subject = "Important"
    body = "Urgent content"

    result = send_email(
        recipients=["to@example.com"],
        subject=subject,
        body=body,
        from_address="sender@example.com"
    )

    assert result is True
    msg = captured["msg"]
    assert subject in msg["Subject"]
    assert any(body in part.get_payload() for part in msg.walk() if part.get_content_type() == "text/plain")


def test_send_email_mime_headers(monkeypatch):
    captured = {}

    class DummySMTP:
        def sendmail(self, from_addr, to_addrs, msg):
            captured["msg"] = email.message_from_string(msg)
        def __enter__(self): return self
        def __exit__(self, *args): pass

    monkeypatch.setattr("smtplib.SMTP", lambda *args, **kwargs: DummySMTP())

    send_email(
        recipients=["x@y.com"],
        subject="Test subject",
        body="Email body",
        from_address="noreply@example.com",
        reply_to="support@example.com"
    )

    msg = captured["msg"]
    assert msg["From"] == "noreply@example.com"
    assert msg["Reply-To"] == "support@example.com"
    assert msg["Subject"] == "Test subject"
    assert "MIME-Version" in msg


def test_send_email_without_reply_to(monkeypatch):
    captured = {}

    class DummySMTP:
        def sendmail(self, from_addr, to_addrs, msg):
            captured["msg"] = email.message_from_string(msg)
        def __enter__(self): return self
        def __exit__(self, *args): pass

    monkeypatch.setattr("smtplib.SMTP", lambda *args, **kwargs: DummySMTP())

    send_email(
        recipients=["x@y.com"],
        subject="No Reply-To",
        body="No reply",
        from_address="noreply@example.com"
    )

    msg = captured["msg"]
    assert "Reply-To" not in msg


def test_send_email_raises_exception(monkeypatch):
    class FailingSMTP:
        def sendmail(self, from_addr, to_addrs, msg):
            raise RuntimeError("SMTP failed")
        def __enter__(self): return self
        def __exit__(self, *args): pass

    monkeypatch.setattr("smtplib.SMTP", lambda *args, **kwargs: FailingSMTP())

    with pytest.raises(RuntimeError, match="SMTP failed"):
        send_email(
            recipients=["fail@example.com"],
            subject="Fail",
            body="Trigger failure",
            from_address="noreply@example.com"
        )
