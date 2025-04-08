#!/bin/bash

# Va dans le dossier du script (donc racine du projet)
cd "$(dirname "$0")"

# Active l'environnement virtuel
source venv/bin/activate

# Lancement du script principal
echo "🚀 Lancement de Reclaimy..."
python3 -m app.main
