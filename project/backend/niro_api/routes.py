"""HTTP routes for health, upload, analysis and report retrieval."""

from __future__ import annotations

import re
from pathlib import Path
from uuid import uuid4

from flask import Blueprint, current_app, jsonify, request
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from .dependency_parser import ManifestError, is_supported_manifest, parse_manifest


api = Blueprint("api", __name__)
UPLOAD_ID_PATTERN = re.compile(r"^[0-9a-f]{32}--[A-Za-z0-9_.@()-]+$")


@api.get("/health")
def health_check():
    cve_index = current_app.extensions["niro_cve_index"]
    analyzer = current_app.extensions["niro_analyzer"]
    return jsonify({
        "success": True,
        "message": "Niro AI API is ready.",
        "service": "niro-api",
        "version": "1.0.0",
        "dataset": {
            "available": cve_index.available,
            "records_indexed": cve_index.record_count,
        },
        "qwen_configured": analyzer.qwen_client.configured,
    })


@api.post("/upload")
def upload_file():
    try:
        upload = _receive_and_parse_file()
    except ManifestError as error:
        return _error(str(error), 400)

    return jsonify({
        "success": True,
        "message": f"{upload['filename']} was validated successfully.",
        "upload": {
            "id": upload["upload_id"],
            "name": upload["filename"],
            "size_bytes": upload["size_bytes"],
            "dependency_count": len(upload["dependencies"]),
            "dependencies": [item.to_dict() for item in upload["dependencies"][:50]],
            "preview_truncated": len(upload["dependencies"]) > 50,
        },
    }), 201


@api.post("/analyze")
def analyze_file():
    try:
        if "file" in request.files:
            upload = _receive_and_parse_file()
        else:
            upload_id = (request.get_json(silent=True) or {}).get("upload_id", "")
            upload = _load_existing_upload(upload_id)
    except ManifestError as error:
        return _error(str(error), 400)

    analyzer = current_app.extensions["niro_analyzer"]
    report = analyzer.create_report(upload["filename"], upload["dependencies"])
    current_app.extensions["niro_report_store"].save(report)

    return jsonify({
        "success": True,
        "message": "Dependency analysis completed.",
        "report": report,
    }), 201


@api.get("/report/<report_id>")
def get_report(report_id: str):
    report = current_app.extensions["niro_report_store"].get(report_id.lower())
    if report is None:
        return _error("Report not found.", 404)
    return jsonify({"success": True, "report": report})


def _receive_and_parse_file() -> dict:
    if "file" not in request.files:
        raise ManifestError("No file was included in the request.")
    uploaded_file: FileStorage = request.files["file"]
    original_filename = Path(uploaded_file.filename or "").name

    if not original_filename:
        raise ManifestError("No file was selected.")
    if not is_supported_manifest(original_filename):
        raise ManifestError(
            "Unsupported file. Upload package.json, package-lock.json, "
            "npm-shrinkwrap.json, yarn.lock or pnpm-lock.yaml."
        )

    safe_filename = secure_filename(original_filename)
    if not safe_filename:
        raise ManifestError("The file name is not valid.")

    upload_id = f"{uuid4().hex}--{safe_filename}"
    upload_folder = Path(current_app.config["UPLOAD_FOLDER"])
    save_path = upload_folder / upload_id
    uploaded_file.save(save_path)

    try:
        dependencies = parse_manifest(
            save_path,
            original_filename,
            current_app.config["MAX_DEPENDENCIES"],
        )
    except ManifestError:
        save_path.unlink(missing_ok=True)
        raise

    return {
        "upload_id": upload_id,
        "filename": original_filename,
        "size_bytes": save_path.stat().st_size,
        "dependencies": dependencies,
    }


def _load_existing_upload(upload_id: object) -> dict:
    if not isinstance(upload_id, str) or not UPLOAD_ID_PATTERN.fullmatch(upload_id):
        raise ManifestError("A valid upload_id or manifest file is required.")

    upload_folder = Path(current_app.config["UPLOAD_FOLDER"])
    path = upload_folder / upload_id
    if not path.is_file():
        raise ManifestError("The uploaded file was not found. Upload it again.")

    filename = upload_id.split("--", 1)[1]
    dependencies = parse_manifest(
        path,
        filename,
        current_app.config["MAX_DEPENDENCIES"],
    )
    return {
        "upload_id": upload_id,
        "filename": filename,
        "size_bytes": path.stat().st_size,
        "dependencies": dependencies,
    }


def _error(message: str, status: int):
    return jsonify({"success": False, "message": message}), status
