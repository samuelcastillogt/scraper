from __future__ import annotations

from pathlib import Path
from typing import Iterable

from openpyxl import Workbook

from .types import ScrapeRecord


class ExcelExporter:
    def __init__(self, output_path: str | Path = "scrap_output.xlsx") -> None:
        self.output_path = Path(output_path)

    def export(self, records: Iterable[ScrapeRecord]) -> Path:
        wb = Workbook()
        ws = wb.active
        ws.title = "scrapes"

        headers = ["url", "page_type", "title", "cleaned_html", "text_content", "image_urls", "fetched_at"]
        ws.append(headers)

        for record in records:
            row = record.as_row()
            ws.append([row[h] for h in headers])

        wb.save(self.output_path)
        return self.output_path


class TextExporter:
    def __init__(self, output_path: str | Path = "scrap_output.txt") -> None:
        self.output_path = Path(output_path)

    def export(self, records: Iterable[ScrapeRecord]) -> Path:
        lines = []
        for record in records:
            title = record.title or record.url
            lines.append(f"Titulo: {title}")
            lines.append("HTML limpio:")
            lines.append(record.cleaned_html)
            lines.append("-" * 80)

        self.output_path.write_text("\n".join(lines), encoding="utf-8")
        return self.output_path
