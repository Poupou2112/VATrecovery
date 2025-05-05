from email.message import EmailMessage
import pytest
from app.email_sender import send_email
from unittest.mock import patch, MagicMock
import email

def test_send_email(monkeypatch):
    mock_sendmail = MagicMock()
    mock_smtp = MagicMock()
    mock_smtp.sendmail = mock_sendmail
    monkeypatch.setattr("smtplib.SMTP", lambda *args, **kwargs: mock_smtp)

    subject = "Test Subject"
    body = "Test Body"
    to = ["recipient@example.com"]

    from_address, to_addresses, msg = send_email(subject, body, to)

    assert from_address == "noreply@vatrecovery.com"
    assert to_addresses == to
    assert subject in msg["Subject"]
    assert body in msg.get_payload(0).get_payload()
    mock_sendmail.assert_called_once()

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


def test_send_email_multiple_recipients(monkeypatch):
    mock_sendmail = MagicMock()
    monkeypatch.setattr("smtplib.SMTP", lambda *args, **kwargs: MagicMock(sendmail=mock_sendmail))

    recipients = ["a@example.com", "b@example.com"]
    _, to_addresses, msg = send_email("Multi", "Body", recipients)

    assert to_addresses == recipients
    assert "To" in msg

def test_send_email_content_structure(monkeypatch):
    monkeypatch.setattr("smtplib.SMTP", lambda *args, **kwargs: MagicMock(sendmail=MagicMock()))

    subject = "Hello"
    body = "Text content"
    html = "<h1>HTML</h1>"
    _, _, msg = send_email(subject, body, ["x@y.com"], html=html)

    parts = msg.get_payload()
    assert any(part.get_content_type() == "text/plain" for part in parts)
    assert any(part.get_content_type() == "text/html" for part in parts)


def test_send_email_raises_exception(monkeypatch):
    class FailingSMTP:
        def __enter__(self): return self
        def __exit__(self, exc_type, exc_val, exc_tb): pass
        def sendmail(self, *args, **kwargs): raise smtplib.SMTPException("SMTP error")

    monkeypatch.setattr("smtplib.SMTP", lambda *args, **kwargs: FailingSMTP())

    with pytest.raises(smtplib.SMTPException):
        send_email("Error", "Trigger", ["fail@example.com"])

def test_send_email_contains_subject_and_body(monkeypatch):
    monkeypatch.setattr("smtplib.SMTP", lambda *args, **kwargs: MagicMock(sendmail=MagicMock()))

    subject = "Important"
    body = "Urgent content"
    _, _, msg = send_email(subject, body, ["test@x.com"])

    assert subject == msg["Subject"]
    assert body in msg.get_payload(0).get_payload()

def test_send_email_mime_headers(monkeypatch):
    monkeypatch.setattr("smtplib.SMTP", lambda *args, **kwargs: MagicMock(sendmail=MagicMock()))

    reply = "someone@reply.com"
    _, _, msg = send_email("Subj", "Body", ["rcpt@domain.com"], reply_to=reply)

    assert msg["Reply-To"] == reply

def test_send_email_without_reply_to():
    from app.email_sender import send_email

    with patch("smtplib.SMTP") as mock_smtp:
        smtp_instance = MagicMock()
        mock_smtp.return_value.__enter__.return_value = smtp_instance

        send_email("test@example.com", "Hello", "<p>Content</p>", "no-reply@example.com")

        mime_message = smtp_instance.sendmail.call_args[0][2]
        assert "Reply-To:" not in mime_message

    monkeypatch.setattr("smtplib.SMTP_SSL", lambda *args, **kwargs: MockSMTP())

    result = send_email(
        to="recipient@example.com",
        subject="Hello",
        body="Test body"
    )

    assert result is True
