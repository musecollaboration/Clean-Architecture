from loguru import logger
import sys

from app.config.settings import settings


def setup_logging() -> None:
    """Настройка глобального логгера Loguru."""
    logger.remove()  # Удаляем дефолтный handler

    if settings.DEBUG:
        # Dev-режим: красивый цветной вывод в stderr и логирование в файл
        logger.add(
            sys.stderr,
            level=settings.LOG_LEVEL,
            format=(
                "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
                "<level>{message}</level>"
            ),
            colorize=True,
        )
        logger.add(
            "logs/app.log",
            rotation="500 MB",
            retention="10 days",
            compression="zip",
            level=settings.LOG_LEVEL,
            encoding="utf-8"
        )
    else:
        # Prod-режим: структурированные JSON-логи (для Loki/ELK/Sentry) + логирование в файл
        logger.add(
            sys.stderr,
            level=settings.LOG_LEVEL,
            format="{time:YYYY-MM-DDTHH:mm:ssZ} | {level} | {name}:{function}:{line} | {message}",
            serialize=True,  # JSON-вывод
        )
        logger.add(
            "logs/app.log",
            rotation="500 MB",
            retention="10 days",
            compression="zip",
            level=settings.LOG_LEVEL,
            serialize=True,
            encoding="utf-8"
        )
