# VATrecovery

[![Tests](https://github.com/Poupou2112/VATrecovery/actions/workflows/ci.yml/badge.svg)](https://github.com/Poupou2112/VATrecovery/actions)
[![Coverage](https://codecov.io/gh/Poupou2112/VATrecovery/branch/main/graph/badge.svg)](https://codecov.io/gh/Poupou2112/VATrecovery)
[![Docker](https://github.com/Poupou2112/VATrecovery/actions/workflows/docker.yml/badge.svg)](https://github.com/Poupou2112/VATrecovery/actions)

> Application de récupération automatique de TVA sur notes de frais.

## 🚀 Fonctionnalités

- OCR intelligent sur reçus (Google Vision)
- Envoi automatisé d’e-mails
- Synchronisation via Gmail IMAP
- API sécurisée avec tokens
- Dashboard web filtré par client

## 🧪 Lancer les tests

```bash
pytest --cov=app --cov-report=term-missing
