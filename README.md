# VATrecovery
![CI](https://github.com/Poupou2112/VATrecovery/actions/workflows/ci.yml/badge.svg)
[![codecov](https://codecov.io/gh/Poupou2112/VATrecovery/branch/main/graph/badge.svg)](https://codecov.io/gh/Poupou2112/VATrecovery)
![Docker](https://github.com/Poupou2112/VATrecovery/actions/workflows/docker.yml/badge.svg)

## ✅ Checklist de validation VATrecovery

| Étape                                    | Statut |
|-----------------------------------------|--------|
| 🔁 Tests unitaires passent (`pytest`)     | ☑️     |
| 📊 Couverture de code > 60% (`codecov`)  | ☑️     |
| 🐳 Docker image build et run OK         | ☑️     |
| 🛠️ Alembic migrations sans erreur       | ☑️     |
| 🌍 Accès `http://localhost:8000/`        | ☑️     |
| 📘 Swagger UI (`/docs`) fonctionne       | ☑️     |
| 📕 Redoc (`/redoc`) fonctionne           | ☑️     |
| 🔐 Dashboard `/dashboard` accessible     | ☑️     |
| 🔑 Auth API avec `X-API-Token`           | ☑️     |
| 🧾 Endpoint `/api/receipts` OK           | ☑️     |
| 📤 Envoi email `/api/send_invoice` OK   | ☑️     |
| 🧠 OCR fonctionne (Google Vision API)    | ☑️     |
| 📬 Réception IMAP de factures OK         | ☑️     |
| 📦 Code formaté avec `black`             | ☑️     |

---

📌 _Coche chaque case à mesure que tu testes les fonctionnalités. Une fois tout validé, ton app est prête à être utilisée ou déployée en production !_


**VATrecovery** est une application de récupération automatique de TVA sur notes de frais.  
Elle permet de :
- Scanner les reçus (OCR via Google Vision)
- Envoyer des emails pour demander les factures
- Suivre l’état des relances
- Synchroniser les factures reçues via Gmail IMAP
- Consulter l’activité via un dashboard web
- Exposer une API REST sécurisée

---

## 🔧 Technologies

- **FastAPI** (API + serveur web)
- **SQLAlchemy** (ORM)
- **Google Cloud Vision** (OCR)
- **SMTP / IMAP** (email)
- **Loguru** (logs)
- **Docker** (déploiement)

---

## 🚀 Lancer le projet

### 1. Cloner le repo

```bash
git clone https://github.com/ton-user/VATrecovery.git
cd VATrecovery
