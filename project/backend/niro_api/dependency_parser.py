"""Dependency manifest validation and parsing."""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path


SUPPORTED_FILENAMES = {
    "package.json",
    "package-lock.json",
    "npm-shrinkwrap.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "pnpm-lock.yml",
}


class ManifestError(ValueError):
    """Raised when a dependency file cannot be validated or parsed."""


@dataclass(frozen=True)
class Dependency:
    name: str
    version: str
    group: str = "dependency"

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


def is_supported_manifest(filename: str) -> bool:
    return Path(filename).name.lower() in SUPPORTED_FILENAMES


def parse_manifest(path: Path, original_filename: str, limit: int = 2500) -> list[Dependency]:
    filename = Path(original_filename).name.lower()

    if filename == "package.json":
        dependencies = _parse_package_json(path)
    elif filename in {"package-lock.json", "npm-shrinkwrap.json"}:
        dependencies = _parse_package_lock(path)
    elif filename == "yarn.lock":
        dependencies = _parse_yarn_lock(path)
    elif filename in {"pnpm-lock.yaml", "pnpm-lock.yml"}:
        dependencies = _parse_pnpm_lock(path)
    else:
        raise ManifestError(
            "Unsupported file. Upload package.json, package-lock.json, "
            "npm-shrinkwrap.json, yarn.lock or pnpm-lock.yaml."
        )

    dependencies = _deduplicate(dependencies)
    if not dependencies:
        raise ManifestError("No dependencies were found in the uploaded file.")
    if len(dependencies) > limit:
        raise ManifestError(
            f"The manifest contains {len(dependencies)} dependencies; the limit is {limit}."
        )
    return dependencies


def _load_json(path: Path) -> dict:
    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except UnicodeDecodeError as error:
        raise ManifestError("The uploaded file must use UTF-8 text encoding.") from error
    except json.JSONDecodeError as error:
        raise ManifestError(f"Invalid JSON near line {error.lineno}, column {error.colno}.") from error

    if not isinstance(data, dict):
        raise ManifestError("The JSON manifest must contain an object at its root.")
    return data


def _parse_package_json(path: Path) -> list[Dependency]:
    data = _load_json(path)
    dependencies: list[Dependency] = []
    groups = {
        "dependencies": "production",
        "devDependencies": "development",
        "peerDependencies": "peer",
        "optionalDependencies": "optional",
    }

    for key, group in groups.items():
        values = data.get(key, {})
        if values is None:
            continue
        if not isinstance(values, dict):
            raise ManifestError(f"The '{key}' field must be a JSON object.")
        for name, version in values.items():
            if isinstance(name, str) and isinstance(version, str):
                dependencies.append(Dependency(name=name, version=version, group=group))
    return dependencies


def _parse_package_lock(path: Path) -> list[Dependency]:
    data = _load_json(path)
    dependencies: list[Dependency] = []
    packages = data.get("packages")

    if isinstance(packages, dict):
        for package_path, details in packages.items():
            if not package_path or not isinstance(details, dict):
                continue
            name = details.get("name") or _name_from_node_modules_path(package_path)
            version = details.get("version")
            if isinstance(name, str) and isinstance(version, str):
                group = "development" if details.get("dev") else "production"
                dependencies.append(Dependency(name=name, version=version, group=group))
    else:
        _walk_legacy_lock(data.get("dependencies", {}), dependencies)

    return dependencies


def _walk_legacy_lock(values: object, dependencies: list[Dependency]) -> None:
    if not isinstance(values, dict):
        return
    for name, details in values.items():
        if not isinstance(name, str) or not isinstance(details, dict):
            continue
        version = details.get("version")
        if isinstance(version, str):
            dependencies.append(Dependency(name=name, version=version))
        _walk_legacy_lock(details.get("dependencies"), dependencies)


def _name_from_node_modules_path(package_path: str) -> str:
    marker = "node_modules/"
    return package_path.rsplit(marker, 1)[-1] if marker in package_path else package_path


def _parse_yarn_lock(path: Path) -> list[Dependency]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError as error:
        raise ManifestError("The uploaded file must use UTF-8 text encoding.") from error

    dependencies: list[Dependency] = []
    selectors: list[str] = []
    for line in lines:
        if line and not line.startswith((" ", "#")) and line.rstrip().endswith(":"):
            selectors = [item.strip().strip('"\'') for item in line[:-1].split(",")]
            continue

        version_match = re.match(r'^\s{2}version\s+["\']?([^"\'\s]+)', line)
        if version_match and selectors:
            version = version_match.group(1)
            for selector in selectors:
                name = _package_name_from_yarn_selector(selector)
                if name:
                    dependencies.append(Dependency(name=name, version=version))
            selectors = []
    return dependencies


def _package_name_from_yarn_selector(selector: str) -> str:
    selector = selector.removeprefix("npm:")
    if selector.startswith("@"):
        slash = selector.find("/")
        separator = selector.find("@", slash + 1)
        return selector[:separator] if slash > 0 and separator > slash else ""
    return selector.rsplit("@", 1)[0] if "@" in selector else selector


def _parse_pnpm_lock(path: Path) -> list[Dependency]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError as error:
        raise ManifestError("The uploaded file must use UTF-8 text encoding.") from error

    dependencies: list[Dependency] = []
    in_packages = False
    for line in lines:
        if line and not line.startswith(" "):
            in_packages = line.strip() in {"packages:", "snapshots:"}
            continue
        if not in_packages:
            continue

        match = re.match(r"^\s{2}['\"]?/?(.+?)['\"]?:\s*$", line)
        if not match:
            continue
        parsed = _split_pnpm_package_key(match.group(1))
        if parsed:
            dependencies.append(Dependency(name=parsed[0], version=parsed[1]))
    return dependencies


def _split_pnpm_package_key(value: str) -> tuple[str, str] | None:
    value = value.split("(", 1)[0]
    if value.startswith("@"):
        slash = value.find("/")
        separator = max(value.rfind("@"), value.rfind("/"))
        if slash <= 0 or separator <= slash:
            return None
    else:
        separator = max(value.rfind("@"), value.rfind("/"))
        if separator <= 0:
            return None
    name = value[:separator]
    version = value[separator + 1:]
    return (name, version) if name and version else None


def _deduplicate(dependencies: list[Dependency]) -> list[Dependency]:
    unique: dict[tuple[str, str], Dependency] = {}
    for dependency in dependencies:
        name = dependency.name.strip()
        version = dependency.version.strip()
        if name and version:
            key = (name.lower(), version)
            unique.setdefault(key, Dependency(name=name, version=version, group=dependency.group))
    return sorted(unique.values(), key=lambda item: item.name.lower())
