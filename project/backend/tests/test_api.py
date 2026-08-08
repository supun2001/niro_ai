import io
import json
from pathlib import Path

import pytest

from niro_api import create_app


@pytest.fixture()
def client(tmp_path: Path):
    dataset = tmp_path / "cves.jsonl"
    dataset.write_text(json.dumps({
        "input": (
            "CVE ID: CVE-2024-0001\n"
            "Metrics: [{'cvssV3_1': {'baseScore': 8.1, 'baseSeverity': 'HIGH'}}]\n"
            "Problem Types: [{'descriptions': [{'cweId': 'CWE-79'}]}]\n"
            "References: ['https://example.com/advisory']"
        ),
        "output": json.dumps({
            "cve_id": "CVE-2024-0001",
            "summary": "Example vulnerability",
            "affected": [{"packageName": "express", "product": "express"}],
            "patch_status": "Check advisory references",
            "exploit_evidence": "Not confirmed",
        }),
    }) + "\n", encoding="utf-8")

    app = create_app({
        "TESTING": True,
        "UPLOAD_FOLDER": tmp_path / "uploads",
        "REPORT_FOLDER": tmp_path / "reports",
        "CVE_DATA_PATH": dataset,
        "ENABLE_QWEN": False,
    })
    return app.test_client()


def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.get_json()["dataset"]["records_indexed"] == 1


def test_analyze_manifest_and_retrieve_report(client):
    response = client.post(
        "/api/analyze",
        data={
            "file": (
                io.BytesIO(json.dumps({"dependencies": {"express": "4.18.2"}}).encode()),
                "package.json",
            )
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 201
    payload = response.get_json()
    report = payload["report"]
    assert report["summary"]["known_vulnerability_count"] == 1
    assert report["summary"]["overall_risk_level"] == "High"

    fetched = client.get(f"/api/report/{report['report_id']}")
    assert fetched.status_code == 200
    assert fetched.get_json()["report"]["report_id"] == report["report_id"]


def test_rejects_unrelated_json(client):
    response = client.post(
        "/api/analyze",
        data={"file": (io.BytesIO(b"{}"), "report.json")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 400
