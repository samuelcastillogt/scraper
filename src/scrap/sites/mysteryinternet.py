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


class MysteryInternetScraper(Scraper):
    page_type = "misteryinternet.com"

    def discover_urls(self, root_url: str, limit: int | None = None) -> List[str]:
        html = fetch_html(self.session, root_url)
        soup = BeautifulSoup(html, "lxml")
        domain = urlparse(root_url).netloc
        links = collect_links(
            soup,
            root_url,
            domain_filter=domain,
            allow_subdomains=True,
            excluded_domains=[
                "facebook.com",
                "twitter.com",
                "pinterest.com",
                "api.whatsapp.com",
                "wa.me",
                "linkedin.com",
            ],
        )
        post_links = [link for link in links if self._is_post(link)]
        return post_links[:limit] if limit else post_links

    def _is_post(self, url: str) -> bool:
        parsed = urlparse(url)
        path = parsed.path.lower()
        if path in {"", "/"}:
            return False
        excluded_keywords = [
            "category",
            "tag",
            "wp-",
            "sugerencias",
            "mapa-de-misterios",
            "todas-las-categorias",
        ]
        if any(keyword in path for keyword in excluded_keywords):
            return False
        # posts usual pattern: at least two path segments and contains a hyphen slug
        if path.count("/") < 2:
            return False
        if "-" not in path:
            return False
        return True

    def scrape(self, url: str) -> ScrapeRecord:
        html = fetch_html(self.session, url)
        soup = BeautifulSoup(html, "lxml")
        container = soup.find(class_="post_content")
        title = extract_title(soup)
        if container is None:
            cleaned_html, text_content, images = cleaned_html_and_text(html, url)
        else:
            cleaned_html, text_content, images = cleaned_html_and_text_from_node(container, url)
        return ScrapeRecord(
            url=url,
            page_type=self.page_type,
            title=title or url,
            cleaned_html=cleaned_html,
            text_content=text_content,
            image_urls=images,
        )
