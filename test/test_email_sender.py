from app.email_sender import send_email

def test_send_email_mock(monkeypatch):
    class MockSMTP:
        def __init__(self, *args, **kwargs): pass
        def login(self, *args, **kwargs): pass
        def send_message(self, msg): self.sent = msg
        def quit(self): pass
        def __enter__(self): return self
        def __exit__(self, *args): pass

    # Mock de smtplib.SMTP_SSL pour éviter tout envoi réel
    monkeypatch.setattr("smtplib.SMTP_SSL", lambda *args, **kwargs: MockSMTP())

    result = send_email(
        to="test@example.com",
        subject="Test",
        body="This is a test email.",
        attachment_path=None  # Aucun fichier en pièce jointe
    )
    assert result is True
