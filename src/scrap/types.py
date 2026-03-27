from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List


@dataclass
class ScrapeRecord:
    url: str
    page_type: str
    title: str
    cleaned_html: str
    text_content: str
    image_urls: List[str] = field(default_factory=list)
    fetched_at: datetime = field(default_factory=datetime.utcnow)

    def as_row(self) -> Dict[str, str]:
        return {
            "url": self.url,
            "page_type": self.page_type,
            "title": self.title,
            "cleaned_html": self.cleaned_html,
            "text_content": self.text_content,
            "image_urls": ",".join(self.image_urls),
            "fetched_at": self.fetched_at.isoformat(),
        }
