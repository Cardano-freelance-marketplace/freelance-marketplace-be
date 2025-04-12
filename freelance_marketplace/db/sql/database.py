from sqlalchemy.ext.asyncio import (AsyncSession,
                                    create_async_engine, async_sessionmaker)
from sqlalchemy.ext.declarative import declarative_base
from freelance_marketplace.core.config import settings
Base = declarative_base()

DATABASE_URL = settings.sql.connection_string
engine = create_async_engine(DATABASE_URL, echo=True, future=True)

AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

async def init_db():
    async with engine.begin() as conn:
        print(Base.metadata.tables)
        await conn.run_sync(Base.metadata.create_all)

async def get_sql_db():
    async with AsyncSessionLocal() as session:
        yield session
