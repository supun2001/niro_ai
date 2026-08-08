"""Optional client for an OpenAI-compatible local Qwen server."""

from __future__ import annotations

import json
import re

import requests


class QwenClient:
    def __init__(self, enabled: bool, api_url: str, model_name: str, timeout_seconds: int):
        self.enabled = enabled
        self.api_url = api_url
        self.model_name = model_name
        self.timeout_seconds = timeout_seconds

    @property
    def configured(self) -> bool:
        return self.enabled and bool(self.api_url)

    def analyze(self, evidence: dict) -> tuple[dict | None, str | None]:
        if not self.configured:
            return None, None

        prompt = (
            "Review this public dependency vulnerability evidence. Return one valid JSON "
            "object with keys summary, candidate_zero_day_indicator, future_risk, "
            "confidence, recommendation and human_review_required. Do not claim a "
            "confirmed zero-day without explicit evidence.\n\n"
            + json.dumps(evidence, ensure_ascii=False)
        )

        try:
            response = requests.post(
                self.api_url,
                json={
                    "model": self.model_name,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2,
                },
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            return _parse_json_object(content), None
        except (requests.RequestException, KeyError, IndexError, TypeError, ValueError):
            return None, "Qwen enrichment was unavailable; the local retrieval baseline was used."


def _parse_json_object(content: str) -> dict:
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", content.strip(), flags=re.IGNORECASE)
    parsed = json.loads(cleaned)
    if not isinstance(parsed, dict):
        raise ValueError("The model response was not a JSON object.")
    return parsed
