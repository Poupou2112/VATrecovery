import pytest
from app.email_sender import send_email
from unittest.mock import patch, MagicMock
from email import message_from_string
import smtplib


@patch("smtplib.SMTP")
def test_send_email_success(mock_smtp):
    smtp_instance = MagicMock()
    mock_smtp.return_value.__enter__.return_value = smtp_instance

    result = send_email(
        subject="Hello",
        body="Email body",
        recipients=["recipient@example.com"]
    )

    assert result is True
    smtp_instance.sendmail.assert_called_once()


def test_send_email_html_structure(monkeypatch):
    captured = {}

    class DummySMTP:
        def sendmail(self, from_addr, to_addrs, msg):
            captured["msg"] = message_from_string(msg)
        def __enter__(self): return self
        def __exit__(self, *args): pass

    monkeypatch.setattr("smtplib.SMTP", lambda *a, **k: DummySMTP())

    send_email(
        subject="HTML Test",
        body="Plain text",
        html="<h1>HTML</h1>",
        recipients=["test@example.com"]
    )

    msg = captured["msg"]
    assert msg.is_multipart()
    parts = list(msg.walk())
    assert any(p.get_content_type() == "text/plain" for p in parts)
    assert any(p.get_content_type() == "text/html" for p in parts)


def test_send_email_multiple_recipients(monkeypatch):
    smtp_mock = MagicMock()
    monkeypatch.setattr("smtplib.SMTP", lambda *a, **k: smtp_mock)

    recipients = ["a@example.com", "b@example.com"]
    result = send_email(
        subject="Hello",
        body="Body",
        recipients=recipients
    )

    assert result is True
    smtp_mock.sendmail.assert_called_once()


def test_send_email_reply_to(monkeypatch):
    captured = {}

    class DummySMTP:
        def sendmail(self, from_addr, to_addrs, msg):
            captured["msg"] = message_from_string(msg)
        def __enter__(self): return self
        def __exit__(self, *args): pass

    monkeypatch.setattr("smtplib.SMTP", lambda *a, **k: DummySMTP())

    send_email(
        subject="Reply Test",
        body="Body",
        recipients=["test@example.com"],
        reply_to="reply@domain.com"
    )

    assert "Reply-To" in captured["msg"]
    assert captured["msg"]["Reply-To"] == "reply@domain.com"


def test_send_email_raises_exception(monkeypatch):
    class FailingSMTP:
        def sendmail(self, *a, **k):
            raise smtplib.SMTPException("Failed")
        def __enter__(self): return self
        def __exit__(self, *args): pass

    monkeypatch.setattr("smtplib.SMTP", lambda *a, **k: FailingSMTP())

    result = send_email(
        subject="Error",
        body="Should fail",
        recipients=["fail@example.com"]
    )

    assert result is False
