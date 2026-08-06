from pathlib import Path

from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.utils import secure_filename


app = Flask(__name__)

# Allow requests only from the Vue development server.
CORS(
    app,
    resources={
        r"/api/*": {
            "origins": "http://localhost:3000"
        }
    }
)

UPLOAD_FOLDER = Path("uploads")
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {"pdf", "txt", "json"}
MAX_FILE_SIZE = 5 * 1024 * 1024

app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_SIZE


def is_allowed_file(filename: str) -> bool:
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


@app.get("/api/health")
def health_check():
    return jsonify({
        "success": True,
        "message": "Flask API is running"
    }), 200


@app.post("/api/upload")
def upload_file():
    if "file" not in request.files:
        return jsonify({
            "success": False,
            "message": "No file was included in the request"
        }), 400

    uploaded_file = request.files["file"]

    if not uploaded_file.filename:
        return jsonify({
            "success": False,
            "message": "No file was selected"
        }), 400

    if not is_allowed_file(uploaded_file.filename):
        return jsonify({
            "success": False,
            "message": "Only PDF, TXT and JSON files are allowed"
        }), 400

    safe_filename = secure_filename(uploaded_file.filename)
    save_path = UPLOAD_FOLDER / safe_filename

    uploaded_file.save(save_path)

    return jsonify({
        "success": True,
        "message": "File uploaded successfully",
        "file": {
            "name": safe_filename,
            "path": str(save_path)
        }
    }), 201


@app.errorhandler(413)
def file_too_large(_error):
    return jsonify({
        "success": False,
        "message": "The file cannot be larger than 5 MB"
    }), 413


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )