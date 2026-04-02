from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from .models import Base

engine = create_async_engine('sqlite+aiosqlite:///mybase.db')

# Фабрика сессий
async_session = async_sessionmaker(engine, expire_on_commit=False)

# Функция для создания таблиц (при старте)
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)