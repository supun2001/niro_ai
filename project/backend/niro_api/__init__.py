"""Niro AI API application factory."""

from pathlib import Path

from flask import Flask, jsonify
from flask_cors import CORS

from .analysis_service import AnalysisService
from .config import Config
from .cve_index import CveIndex
from .qwen_client import QwenClient
from .report_store import ReportStore
from .routes import api


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)

    upload_folder = Path(app.config["UPLOAD_FOLDER"])
    report_folder = Path(app.config["REPORT_FOLDER"])
    upload_folder.mkdir(parents=True, exist_ok=True)
    report_folder.mkdir(parents=True, exist_ok=True)

    cve_index = CveIndex(Path(app.config["CVE_DATA_PATH"]))
    qwen_client = QwenClient(
        enabled=app.config["ENABLE_QWEN"],
        api_url=app.config["QWEN_API_URL"],
        model_name=app.config["MODEL_NAME"],
        timeout_seconds=app.config["QWEN_TIMEOUT_SECONDS"],
    )

    app.extensions["niro_cve_index"] = cve_index
    app.extensions["niro_analyzer"] = AnalysisService(cve_index, qwen_client)
    app.extensions["niro_report_store"] = ReportStore(report_folder)

    CORS(
        app,
        resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}},
    )

    app.register_blueprint(api, url_prefix="/api")

    @app.errorhandler(413)
    def file_too_large(_error):
        size_mb = app.config["MAX_FILE_SIZE_MB"]
        return jsonify({
            "success": False,
            "message": f"The file cannot be larger than {size_mb} MB.",
        }), 413

    @app.errorhandler(404)
    def not_found(_error):
        return jsonify({"success": False, "message": "Endpoint not found."}), 404

    @app.errorhandler(500)
    def internal_error(_error):
        return jsonify({
            "success": False,
            "message": "The server could not complete the request.",
        }), 500

    return app
