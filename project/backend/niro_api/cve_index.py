"""Small local retrieval baseline built from prepared CVE training records."""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path


class CveIndex:
    def __init__(self, data_path: Path):
        self.data_path = data_path
        self._records_by_package: dict[str, list[dict]] = defaultdict(list)
        self._record_count = 0
        self._loaded = False
        self._load_error: str | None = None

    @property
    def record_count(self) -> int:
        self._ensure_loaded()
        return self._record_count

    @property
    def available(self) -> bool:
        self._ensure_loaded()
        return self._load_error is None and self._record_count > 0

    @property
    def load_error(self) -> str | None:
        self._ensure_loaded()
        return self._load_error

    def lookup(self, package_name: str) -> list[dict]:
        self._ensure_loaded()
        return list(self._records_by_package.get(_canonical_name(package_name), []))

    def _ensure_loaded(self) -> None:
        if self._loaded:
            return
        self._loaded = True

        if not self.data_path.is_file():
            self._load_error = "Prepared CVE dataset is not available."
            return

        try:
            with self.data_path.open("r", encoding="utf-8") as file:
                for line in file:
                    if not line.strip():
                        continue
                    self._index_line(json.loads(line))
        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            self._records_by_package.clear()
            self._record_count = 0
            self._load_error = "Prepared CVE dataset could not be read."

    def _index_line(self, payload: dict) -> None:
        raw_output = payload.get("output", {})
        output = json.loads(raw_output) if isinstance(raw_output, str) else raw_output
        if not isinstance(output, dict):
            return

        cve_id = output.get("cve_id")
        if not isinstance(cve_id, str):
            return

        input_text = payload.get("input", "")
        if not isinstance(input_text, str):
            input_text = ""

        package_names = _affected_names(output.get("affected", []))
        if not package_names:
            return

        record = {
            "cve_id": cve_id,
            "summary": output.get("summary") or "No summary available.",
            "severity": _first_match(input_text, r"['\"]baseSeverity['\"]:\s*['\"]([A-Za-z]+)") or "Unknown",
            "cvss_score": _float_match(input_text, r"['\"]baseScore['\"]:\s*([0-9.]+)"),
            "cwe": _first_match(input_text, r"['\"]cweId['\"]:\s*['\"](CWE-\d+)") or "Unknown",
            "patch_status": output.get("patch_status") or "Check advisory references",
            "exploit_evidence": output.get("exploit_evidence") or "Not confirmed from this record",
            "recommendation": output.get("recommendation") or "Review the public advisory and update when a fix is available.",
            "references": _references(input_text),
        }

        for name in package_names:
            records = self._records_by_package[_canonical_name(name)]
            if not any(item["cve_id"] == cve_id for item in records):
                records.append(record)
        self._record_count += 1


def _canonical_name(value: str) -> str:
    return re.sub(r"\s+", "-", value.strip().lower())


def _affected_names(affected: object) -> set[str]:
    if not isinstance(affected, list):
        return set()
    names: set[str] = set()
    for item in affected:
        if not isinstance(item, dict):
            continue
        for key in ("packageName", "product"):
            value = item.get(key)
            if isinstance(value, str) and value.strip():
                names.add(value.strip())
    return names


def _first_match(text: str, pattern: str) -> str | None:
    match = re.search(pattern, text, flags=re.IGNORECASE)
    return match.group(1) if match else None


def _float_match(text: str, pattern: str) -> float | None:
    value = _first_match(text, pattern)
    return float(value) if value is not None else None


def _references(text: str) -> list[str]:
    section = text.split("References:", 1)
    if len(section) != 2:
        return []
    return re.findall(r"https?://[^'\"\]\s]+", section[1])[:5]
