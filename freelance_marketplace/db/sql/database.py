from sqlalchemy.ext.asyncio import (AsyncSession,
                                    create_async_engine, async_sessionmaker)

from freelance_marketplace.models.sql.sql_roles import Base

DATABASE_URL = "postgresql+asyncpg://user:password@localhost:5432/mydatabase"
engine = create_async_engine(DATABASE_URL, echo=True, future=True)

AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_sql_db():
    async with AsyncSessionLocal() as session:
        yield session