from __future__ import annotations

import json
from pathlib import Path
from typing import List

import click
import requests

from dotenv import load_dotenv

from .base import ScraperRegistry
from .exporters import ExcelExporter, TextExporter
from .sites.blogger import BloggerScraper
from .sites.guatemala import GuatemalaScraper
from .sites.mysteryinternet import MysteryInternetScraper
from .sites.blogger_api import BloggerApiScraper

load_dotenv()


registry = ScraperRegistry()
registry.register(BloggerScraper)
registry.register(GuatemalaScraper)
registry.register(MysteryInternetScraper)
registry.register(BloggerApiScraper)


def build_session() -> requests.Session:
    session = requests.Session()
    session.headers.update({"Accept-Language": "es-ES,es;q=0.9,en;q=0.8"})
    return session


@click.group()
def cli() -> None:
    """Scrap Master 3000 CLI."""


@cli.command(name="sites")
def list_sites() -> None:
    """List available site types."""
    click.echo("Tipos disponibles:")
    for site in registry.available():
        click.echo(f"- {site}")


@cli.command()
@click.option("--site", "site_type", required=True, help="Tipo de pagina (ej. blogger, guatemala.com)")
@click.option("--root-url", required=True, help="URL inicial para descubrir o procesar")
@click.option("--limit", type=int, default=None, help="Limite de URLs a procesar")
@click.option("--format", "output_format", type=click.Choice(["txt", "xlsx"], case_sensitive=False), default="txt", help="Formato de salida")
@click.option("--output", type=click.Path(), default=None, help="Ruta del archivo de salida")
@click.option("--json-output", type=click.Path(), default=None, help="Ruta para volcar JSON con registros")
@click.option("--single", is_flag=True, default=False, help="Procesar solo la URL indicada (sin descubrimiento)")
def run(site_type: str, root_url: str, limit: int | None, output_format: str, output: str | None, json_output: str | None, single: bool) -> None:
    """Descubrir y extraer contenido."""
    if site_type not in registry.available():
        raise click.BadParameter(f"Tipo no soportado: {site_type}. Usa 'sites' para ver opciones.")

    session = build_session()
    scraper = registry.create(site_type, session=session)

    if single:
        urls = [root_url]
        click.echo(f"Procesando solo: {root_url}")
    else:
        click.echo(f"Descubriendo URLs en {root_url}...")
        urls = scraper.discover_urls(root_url, limit=limit)
        click.echo(f"Se encontraron {len(urls)} URLs")

    records = []
    for idx, url in enumerate(urls, start=1):
        click.echo(f"[{idx}/{len(urls)}] Extrayendo {url}")
        try:
            records.append(scraper.scrape(url))
        except Exception as exc:  # pragma: no cover - simple CLI feedback
            click.echo(f"   Error: {exc}")

    exporter = (
        TextExporter(output_path=output or "scrap_output.txt")
        if output_format.lower() == "txt"
        else ExcelExporter(output_path=output or "scrap_output.xlsx")
    )
    path = exporter.export(records)
    click.echo(f"Archivo {output_format} generado en {path}")

    if json_output:
        payload = [r.as_row() for r in records]
        Path(json_output).write_text(json.dumps(payload, ensure_ascii=False, indent=2))
        click.echo(f"JSON guardado en {json_output}")


if __name__ == "__main__":
    cli()
