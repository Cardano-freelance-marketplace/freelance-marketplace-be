from logging.config import fileConfig
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context
from freelance_marketplace.core.config import settings
from freelance_marketplace.db.sql.database import Base

# Alembic Config
config = context.config

# Configure logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata for autogenerate
target_metadata = Base.metadata

# Async Database Engine
connectable = create_async_engine(
    settings.sql.connection_string,
    echo=True,  # Set to False in production
    future=True
)

async def run_migrations():
    """Run migrations in an async-safe way."""
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

def do_run_migrations(connection):
    """Configure and run migrations."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        literal_binds=False,
        compare_type=True,  # Detect column type changes
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations())
