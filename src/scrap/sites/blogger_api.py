from __future__ import annotations

from .blogger import BloggerScraper


class BloggerApiScraper(BloggerScraper):
    page_type = "blogger_api"
