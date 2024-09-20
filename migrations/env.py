from __future__ import with_statement
import sys
import os
from alembic import context
from sqlalchemy import engine_from_config, pool
from logging.config import fileConfig

# Add your project directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.database import DATABASE_URL
from src.models import Base

config = context.config

# Interpret the config file for Python logging.
fileConfig(config.config_file_name)

# Set up your target metadata
target_metadata = Base.metadata

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = DATABASE_URL
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
