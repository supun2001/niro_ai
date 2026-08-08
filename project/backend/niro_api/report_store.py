"""Persistence for generated JSON reports."""

import json
import re
from pathlib import Path


REPORT_ID_PATTERN = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$")


class ReportStore:
    def __init__(self, folder: Path):
        self.folder = folder

    def save(self, report: dict) -> None:
        report_id = report["report_id"]
        destination = self.folder / f"{report_id}.json"
        temporary = self.folder / f".{report_id}.tmp"
        temporary.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        temporary.replace(destination)

    def get(self, report_id: str) -> dict | None:
        if not REPORT_ID_PATTERN.fullmatch(report_id):
            return None
        path = self.folder / f"{report_id}.json"
        if not path.is_file():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None
