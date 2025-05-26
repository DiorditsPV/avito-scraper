"""
Avito Subscriber - инструмент для скрейпинга объявлений с Avito
"""

__version__ = "0.1.0"

# Экспортируем основные классы и функции
from .scraper.scraper import AvitoScraper, scrape

__all__ = [
    "AvitoScraper",
    "scrape",
]
