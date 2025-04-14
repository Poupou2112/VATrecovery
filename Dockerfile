FROM python:3.11-slim AS builder

# Configuration de l'environnement de base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Installation des dépendances système pour la construction
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Copie et installation des dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Étape de production (multi-stage build)
FROM python:3.11-slim

# Métadonnées
LABEL maintainer="contact@example.com" \
      name="VATrecovery" \
      version="1.0.0"

# Configuration de l'environnement
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Installation des dépendances minimales pour l'exécution
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Copie des packages installés depuis l'étape de build
COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Création d'un utilisateur non-root
RUN groupadd -r appuser && useradd -r -g appuser -d /app appuser \
    && chown -R appuser:appuser /app

# Copie du code de l'application
COPY --chown=appuser:appuser . .

# Permissions d'exécution pour le script de démarrage
RUN chmod +x run.sh

# Passage à l'utilisateur non-root
USER appuser

# Exposition du port de l'application
EXPOSE 8000

# Point d'entrée
CMD ["./run.sh"]
