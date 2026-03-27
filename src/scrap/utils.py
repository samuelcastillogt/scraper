from __future__ import annotations

from bs4 import BeautifulSoup, Tag
import requests
from urllib.parse import urljoin, urlparse
from typing import Iterable, List, Set


DEFAULT_HEADERS = {
    "User-Agent": "ScrapMaster3000/1.0 (+https://example.com)",
}


def fetch_html(session: requests.Session, url: str, timeout: float = 15.0) -> str:
    response = session.get(url, headers=DEFAULT_HEADERS, timeout=timeout)
    response.raise_for_status()
    return response.text


def strip_noise(soup: Tag) -> None:
    removable_tags = [
        "script",
        "style",
        "noscript",
        "iframe",
        "svg",
        "canvas",
        "header",
        "footer",
        "figcaption",
    ]
    for tag_name in removable_tags:
        for tag in soup.find_all(tag_name):
            tag.decompose()

    ad_signatures = [
        "adsbygoogle",
        "ad-slot",
        "advert",
        "ad-",
    ]
    for tag in soup.find_all(True):
        attrs = tag.attrs or {}
        classes = " ".join(attrs.get("class", []))
        id_attr = attrs.get("id", "")
        combined = f"{classes} {id_attr}".lower()
        if any(sig in combined for sig in ad_signatures):
            tag.decompose()


def extract_image_urls(soup: BeautifulSoup, base_url: str) -> List[str]:
    images: Set[str] = set()
    for img in soup.find_all("img"):
        src = img.get("src") or img.get("data-src")
        if not src:
            continue
        images.add(urljoin(base_url, src))
    return list(images)


def _clean_and_extract(root: Tag, base_url: str) -> tuple[str, str, List[str]]:
    strip_noise(root)

    # Mantener solo texto de enlaces (no necesitamos hrefs ni atributos)
    for anchor in root.find_all("a"):
        anchor.unwrap()

    image_urls = extract_image_urls(root, base_url)
    text_content = root.get_text(separator=" ", strip=True)
    cleaned_html = root.prettify()
    return cleaned_html, text_content, image_urls


def cleaned_html_and_text(html: str, base_url: str) -> tuple[str, str, List[str]]:
    soup = BeautifulSoup(html, "html.parser")
    root = soup.body or soup
    return _clean_and_extract(root, base_url)


def cleaned_html_and_text_from_node(node: Tag, base_url: str) -> tuple[str, str, List[str]]:
    return _clean_and_extract(node, base_url)


def extract_title(soup: BeautifulSoup) -> str:
    # Prefer h1 text
    h1 = soup.find("h1")
    if h1 and h1.get_text(strip=True):
        return h1.get_text(strip=True)
    if soup.title and soup.title.string:
        return soup.title.string.strip()
    return ""


def _host_allows(host: str, domain_filter: str | None, allow_subdomains: bool) -> bool:
    if not domain_filter:
        return True
    host = host.lower()
    domain_filter = domain_filter.lower()
    if host == domain_filter:
        return True
    if allow_subdomains and host.endswith("." + domain_filter):
        return True
    return False


def collect_links(
    soup: BeautifulSoup,
    base_url: str,
    domain_filter: str | None = None,
    allow_subdomains: bool = True,
    excluded_domains: Iterable[str] | None = None,
) -> List[str]:
    links: Set[str] = set()
    excluded = {d.lower() for d in excluded_domains or []}

    for anchor in soup.find_all("a"):
        href = anchor.get("href")
        if not href:
            continue
        full = urljoin(base_url, href)
        if full.startswith("mailto:") or full.startswith("javascript:"):
            continue

        parsed = urlparse(full)
        host = parsed.netloc.lower()
        if excluded and any(host == d or host.endswith("." + d) for d in excluded):
            continue
        if not _host_allows(host, domain_filter, allow_subdomains):
            continue

        cleaned = full.split("#")[0]
        links.add(cleaned)

    return list(links)
