#!/bin/bash
set -euo pipefail

# Configuration selon l'environnement
if [ "${ENV:-development}" = "production" ]; then
    echo "Démarrage de VATrecovery en mode production..."
    # En production, pas de --reload
    exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
else
    echo "Démarrage de VATrecovery en mode développement..."
    # En dev, utiliser --reload
    exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
fi
