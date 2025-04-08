from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys

# ➕ Ajout du chemin de l'app pour les imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from app.models import Base  # 📦 tes modèles SQLAlchemy
from app.init_db import DATABASE_URL  # 🔌 ta connexion

# Config Alembic
config = context.config

# 🔧 Injecte l'URL de la base
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# Logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline():
    """Run migrations sans DB (génère SQL)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations avec DB."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

# Auto-switch online/offline
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
