FROM python:3.11-slim

# Créer un utilisateur non-root
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Définir les variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Copier et installer les dépendances d'abord pour utiliser le cache Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code avec les permissions correctes
COPY --chown=appuser:appuser . .

# Créer les répertoires nécessaires avec les bonnes permissions
RUN mkdir -p /app/logs /app/uploads \
    && chown -R appuser:appuser /app

# Basculer vers l'utilisateur non-root
USER appuser

# Port d'exposition
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Commande de démarrage
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
