"""Environment-backed configuration for the Flask application."""

import os
from pathlib import Path

from dotenv import load_dotenv


BACKEND_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BACKEND_DIR / ".env")


def _path_setting(name: str, default: str) -> Path:
    value = Path(os.getenv(name, default)).expanduser()
    return value if value.is_absolute() else (BACKEND_DIR / value).resolve()


def _boolean_setting(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _integer_setting(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default


class Config:
    DEBUG = _boolean_setting("FLASK_DEBUG", False)
    SECRET_KEY = os.getenv("SECRET_KEY", "niro-development-key")

    MAX_FILE_SIZE_MB = max(1, _integer_setting("MAX_FILE_SIZE_MB", 5))
    MAX_CONTENT_LENGTH = MAX_FILE_SIZE_MB * 1024 * 1024
    MAX_DEPENDENCIES = max(1, _integer_setting("MAX_DEPENDENCIES", 2500))

    UPLOAD_FOLDER = _path_setting("UPLOAD_FOLDER", "uploads")
    REPORT_FOLDER = _path_setting("REPORT_FOLDER", "reports/generated")
    CVE_DATA_PATH = _path_setting(
        "CVE_DATA_PATH",
        "../data/training/cve_instruction_train.jsonl",
    )

    CORS_ORIGINS = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://localhost:3000",
        ).split(",")
        if origin.strip()
    ]

    ENABLE_QWEN = _boolean_setting("ENABLE_QWEN", False)
    QWEN_API_URL = os.getenv(
        "QWEN_API_URL",
        "http://127.0.0.1:8000/v1/chat/completions",
    )
    MODEL_NAME = os.getenv("MODEL_NAME", "qwen2.5-0.5b-instruct")
    QWEN_TIMEOUT_SECONDS = max(5, _integer_setting("QWEN_TIMEOUT_SECONDS", 90))
