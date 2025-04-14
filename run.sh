#!/bin/bash

# Activer l'environnement virtuel si nécessaire
# source venv/bin/activate

# Lancer l'application
uvicorn app.main:app --host 0.0.0.0 --port 8000
