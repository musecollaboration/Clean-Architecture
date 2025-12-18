from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.config.settings import settings


engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,     # В dev режиме включаем логи SQL
    pool_pre_ping=True,      # Защита от разорванных соединений
    pool_size=5,             # Оптимальное значение для большинства приложений
    max_overflow=10,         # Максимум дополнительных соединений
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Важно для работы с detached объектами
    autoflush=False,         # Контроль над flush операциями
)
