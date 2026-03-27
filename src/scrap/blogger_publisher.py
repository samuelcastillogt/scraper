from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Iterable, List

import requests

from .types import ScrapeRecord


@dataclass
class BloggerPublishedPost:
    id: str
    url: str
    title: str


class BloggerPublisher:
    base_url = "https://www.googleapis.com/blogger/v3"

    def __init__(self, access_token: str, session: requests.Session | None = None) -> None:
        if not access_token:
            raise ValueError("Missing Blogger access token")
        self.access_token = access_token
        self.session = session or requests.Session()

    def publish_records(self, blog_id: str, records: Iterable[ScrapeRecord]) -> List[BloggerPublishedPost]:
        published: List[BloggerPublishedPost] = []
        for record in records:
            published.append(self.publish_post(blog_id=blog_id, title=record.title or record.url, html_content=record.cleaned_html))
        return published

    def publish_post(self, blog_id: str, title: str, html_content: str) -> BloggerPublishedPost:
        url = f"{self.base_url}/blogs/{blog_id}/posts/"
        response = self.session.post(
            url,
            headers={
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
            },
            json={
                "kind": "blogger#post",
                "title": title,
                "content": html_content,
            },
            timeout=30,
        )

        if response.status_code >= 400:
            detail = response.text
            raise RuntimeError(f"Blogger publish failed: {response.status_code} {detail}")

        payload = response.json()
        return BloggerPublishedPost(
            id=str(payload.get("id", "")),
            url=str(payload.get("url", "")),
            title=str(payload.get("title", title)),
        )


def resolve_blogger_access_token(session: requests.Session | None = None) -> str:
    direct_token = os.getenv("BLOGGER_ACCESS_TOKEN", "").strip()
    if direct_token:
        return direct_token

    client_id = os.getenv("GOOGLE_CLIENT_ID", "").strip()
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET", "").strip()
    refresh_token = os.getenv("BLOGGER_REFRESH_TOKEN", "").strip()
    if not (client_id and client_secret and refresh_token):
        return ""

    request_session = session or requests.Session()
    response = request_session.post(
        "https://oauth2.googleapis.com/token",
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        },
        timeout=30,
    )
    if response.status_code >= 400:
        raise RuntimeError(f"Failed to refresh Blogger access token: {response.status_code} {response.text}")

    payload = response.json()
    return str(payload.get("access_token", "")).strip()
