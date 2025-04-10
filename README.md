# VATrecovery

[![CI](https://github.com/Poupou2112/VATrecovery/actions/workflows/ci.yml/badge.svg)](https://github.com/Poupou2112/VATrecovery/actions)
[![Docker](https://github.com/Poupou2112/VATrecovery/actions/workflows/docker.yml/badge.svg)](https://github.com/Poupou2112/VATrecovery/actions)
[![codecov](https://codecov.io/gh/Poupou2112/VATrecovery/branch/main/graph/badge.svg?token=f2c2215f-7200-4e3d-999c-f9fe0f6e4c8f)](https://codecov.io/gh/Poupou2112/VATrecovery)

> Application de récupération automatique de TVA sur notes de frais.

---

## 🚀 Fonctionnalités

- 📄 OCR intelligent sur reçus (Google Vision)
- 📧 Envoi automatisé d’e-mails
- 🔁 Synchronisation avec Gmail IMAP
- 🔐 API sécurisée par token
- 📊 Dashboard web filtré par client

---

## 🧪 Lancer les tests

```bash
pytest --cov=app --cov-report=term-missing --cov-report=xml
