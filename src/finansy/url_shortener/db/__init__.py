from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from ..config import config


_engine = None

AsyncSession = async_sessionmaker(expire_on_commit=False)


async def create_db():
    ensure_engine_initialized()
    from .models import BaseModel
    async with _engine.begin() as connection:
        await connection.run_sync(BaseModel.metadata.create_all)


def ensure_engine_initialized():
    global _engine
    if not _engine:
        _engine = create_async_engine(
            str(config.db.url),
            echo=config.db.echo,
        )


def ensure_session_factory_initialized():
    if not AsyncSession.kw['bind']:
        ensure_engine_initialized()
        AsyncSession.configure(bind=_engine)


def get_engine():
    return _engine