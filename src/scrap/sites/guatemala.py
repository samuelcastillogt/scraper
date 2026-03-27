from __future__ import annotations

from urllib.parse import urlparse
from typing import List

from bs4 import BeautifulSoup

from ..base import Scraper
from ..types import ScrapeRecord
from ..utils import (
    cleaned_html_and_text,
    cleaned_html_and_text_from_node,
    collect_links,
    extract_title,
    fetch_html,
)


class GuatemalaScraper(Scraper):
    page_type = "guatemala.com"

    def discover_urls(self, root_url: str, limit: int | None = None) -> List[str]:
        html = fetch_html(self.session, root_url)
        soup = BeautifulSoup(html, "lxml")
        domain = urlparse(root_url).netloc
        links = collect_links(soup, root_url, domain_filter=domain)
        return links[:limit] if limit else links

    def scrape(self, url: str) -> ScrapeRecord:
        html = fetch_html(self.session, url)
        soup = BeautifulSoup(html, "lxml")
        container = soup.select_one(".single_content.read-more")
        title = extract_title(soup)
        if container is None:
            cleaned_html, text_content, images = cleaned_html_and_text(html, url)
        else:
            for widget in container.select(".widget_articulo"):
                widget.decompose()
            cleaned_html, text_content, images = cleaned_html_and_text_from_node(container, url)
        return ScrapeRecord(
            url=url,
            page_type=self.page_type,
            title=title or url,
            cleaned_html=cleaned_html,
            text_content=text_content,
            image_urls=images,
        )
