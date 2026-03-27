from __future__ import annotations

import abc
from typing import Dict, Iterable, List, Type

import requests

from .types import ScrapeRecord


class Scraper(abc.ABC):
    page_type: str

    def __init__(self, session: requests.Session | None = None) -> None:
        self.session = session or requests.Session()

    @abc.abstractmethod
    def discover_urls(self, root_url: str, limit: int | None = None) -> List[str]:
        """Return list of URLs to scrape for this site type."""

    @abc.abstractmethod
    def scrape(self, url: str) -> ScrapeRecord:
        """Fetch and clean content for the given URL."""


class ScraperRegistry:
    def __init__(self) -> None:
        self._registry: Dict[str, Type[Scraper]] = {}

    def register(self, scraper: Type[Scraper]) -> None:
        self._registry[scraper.page_type] = scraper

    def available(self) -> Iterable[str]:
        return self._registry.keys()

    def create(self, page_type: str, session: requests.Session | None = None) -> Scraper:
        scraper_cls = self._registry.get(page_type)
        if scraper_cls is None:
            raise ValueError(f"No scraper registered for page type '{page_type}'")
        return scraper_cls(session=session)
