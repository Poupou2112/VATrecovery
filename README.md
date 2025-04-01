
# API TVA - Récupération automatisée

Ce projet permet :
- De se connecter à une API tierce via OAuth2
- De télécharger des reçus
- D’envoyer automatiquement un e-mail de demande de facture

## Installation

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Créez un fichier `.env` en copiant `.env.example`.

## Lancement

```bash
uvicorn app.main:app --reload
```

Accédez à `http://localhost:8000/login` pour démarrer l'authentification OAuth.
