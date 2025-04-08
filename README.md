# VATrecovery
![CI](https://github.com/Poupou2112/VATrecovery/actions/workflows/ci.yml/badge.svg)

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
