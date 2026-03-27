from __future__ import annotations

import tempfile
from pathlib import Path
from typing import List

from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_file

from scrap.base import ScraperRegistry
from scrap.exporters import TextExporter
from scrap.cli import build_session
from scrap.sites.blogger import BloggerScraper
from scrap.sites.blogger_api import BloggerApiScraper
from scrap.sites.guatemala import GuatemalaScraper
from scrap.sites.mysteryinternet import MysteryInternetScraper

load_dotenv()


def build_registry() -> ScraperRegistry:
    registry = ScraperRegistry()
    registry.register(BloggerScraper)
    registry.register(BloggerApiScraper)
    registry.register(GuatemalaScraper)
    registry.register(MysteryInternetScraper)
    return registry


app = Flask(__name__)


@app.after_request
def add_cors_headers(resp):
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return resp


@app.get("/")
def root():
    return jsonify({"status": "ok", "message": "Scrap Master 3000 API"})


@app.route("/api/scrape", methods=["POST", "OPTIONS"])
def scrape_endpoint():
    if request.method == "OPTIONS":
        return ("", 204)
    data = request.get_json(force=True, silent=True) or {}
    url = data.get("url")
    site = data.get("site")
    limit = data.get("limit")
    if not url or not site:
        return jsonify({"error": "Missing 'url' or 'site'"}), 400

    registry = build_registry()
    if site not in registry.available():
        return jsonify({"error": f"Unsupported site '{site}'"}), 400

    session = build_session()
    scraper = registry.create(site, session=session)

    urls: List[str]
    if data.get("single", True):
        urls = [url]
    else:
        urls = scraper.discover_urls(url, limit=limit)

    records = []
    for target in urls:
        records.append(scraper.scrape(target))

    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
        exporter = TextExporter(output_path=tmp.name)
        exporter.export(records)
        path = Path(tmp.name)

    return send_file(path, mimetype="text/plain", as_attachment=True, download_name="scrap_output.txt")


if __name__ == "__main__":
    app.run(port=8000, debug=False)
