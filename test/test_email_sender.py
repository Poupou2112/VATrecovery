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



def test_send_email_multiple_recipients():
    with patch("smtplib.SMTP") as mock_smtp:
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        send_email(
            to_email=["user1@example.com", "user2@example.com"],
            subject="Hello team",
            html="<p>Test</p>",
            from_email="sender@example.com"
        )

        mock_server.sendmail.assert_called_once()
        recipients = mock_server.sendmail.call_args[0][1]
        assert "user1@example.com" in recipients
        assert "user2@example.com" in recipients


def test_send_email_content_structure():
    with patch("smtplib.SMTP") as mock_smtp:
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        subject = "Subject line"
        html = "<h1>Important</h1>"
        send_email("to@example.com", subject, html, "from@example.com")

        msg = mock_server.sendmail.call_args[0][2]
        assert subject in msg
        assert html in msg
        assert "MIME-Version" in msg

def test_send_email_raises_exception():
    with patch("smtplib.SMTP", side_effect=RuntimeError("SMTP failed")):
        with pytest.raises(RuntimeError, match="SMTP failed"):
            send_email("to@example.com", "Subject", "<p>body</p>", "from@example.com")

    monkeypatch.setattr("smtplib.SMTP_SSL", lambda *args, **kwargs: MockSMTP())

    result = send_email(
        to="recipient@example.com",
        subject="Hello",
        body="Test body"
    )

    assert result is True
