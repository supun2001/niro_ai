import json
from pathlib import Path

import pytest

from niro_api.dependency_parser import ManifestError, parse_manifest


def test_parse_package_json(tmp_path: Path):
    manifest = tmp_path / "package.json"
    manifest.write_text(json.dumps({
        "dependencies": {"express": "^4.18.2"},
        "devDependencies": {"vite": "^6.0.0"},
    }), encoding="utf-8")

    dependencies = parse_manifest(manifest, "package.json")

    assert [(item.name, item.group) for item in dependencies] == [
        ("express", "production"),
        ("vite", "development"),
    ]


def test_rejects_empty_manifest(tmp_path: Path):
    manifest = tmp_path / "package.json"
    manifest.write_text("{}", encoding="utf-8")

    with pytest.raises(ManifestError, match="No dependencies"):
        parse_manifest(manifest, "package.json")


def test_parse_modern_package_lock(tmp_path: Path):
    manifest = tmp_path / "package-lock.json"
    manifest.write_text(json.dumps({
        "lockfileVersion": 3,
        "packages": {
            "": {"name": "demo", "version": "1.0.0"},
            "node_modules/express": {"version": "4.18.2"},
            "node_modules/@scope/tool": {"version": "2.1.0", "dev": True},
        },
    }), encoding="utf-8")

    dependencies = parse_manifest(manifest, "package-lock.json")

    assert [(item.name, item.version, item.group) for item in dependencies] == [
        ("@scope/tool", "2.1.0", "development"),
        ("express", "4.18.2", "production"),
    ]


def test_parse_yarn_lock(tmp_path: Path):
    manifest = tmp_path / "yarn.lock"
    manifest.write_text(
        'express@^4.18.0, express@~4.18.2:\n  version "4.18.3"\n'
        '"@scope/tool@^2.0.0":\n  version "2.1.0"\n',
        encoding="utf-8",
    )

    dependencies = parse_manifest(manifest, "yarn.lock")

    assert [(item.name, item.version) for item in dependencies] == [
        ("@scope/tool", "2.1.0"),
        ("express", "4.18.3"),
    ]


def test_parse_pnpm_lock(tmp_path: Path):
    manifest = tmp_path / "pnpm-lock.yaml"
    manifest.write_text(
        "lockfileVersion: '9.0'\n"
        "packages:\n"
        "  express@4.18.2:\n"
        "    resolution: {integrity: sha512-example}\n"
        "  '@scope/tool@2.1.0':\n"
        "    resolution: {integrity: sha512-example}\n",
        encoding="utf-8",
    )

    dependencies = parse_manifest(manifest, "pnpm-lock.yaml")

    assert [(item.name, item.version) for item in dependencies] == [
        ("@scope/tool", "2.1.0"),
        ("express", "4.18.2"),
    ]
