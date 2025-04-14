FROM python:3.9-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers nécessaires
COPY requirements.txt .
COPY app/ app/
COPY run.sh .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Donner les droits d'exécution au script
RUN chmod +x run.sh

# Définir le point d'entrée
ENTRYPOINT ["./run.sh"]
