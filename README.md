# Niro AI

Dependency-aware cyber threat intelligence (CTI) analysis for Node.js projects.

**Research title:** *Evaluating an AI-Driven Doc-to-LoRA Framework for Proactive Detection and Structured Analysis of Candidate Zero-Day Vulnerabilities from Public Cyber Threat Intelligence*

Niro AI accepts a `package.json` or lock file, extracts its dependencies, retrieves exact package-name matches from the prepared public CVE dataset, applies conservative risk rules, and returns a structured report for human review. An OpenAI-compatible Qwen server can optionally enrich the baseline report.

> Niro AI is an academic defensive-security prototype. It does not prove that a package is safe, confirm an active exploit, or predict a future zero-day. Every report requires analyst review.

## What is implemented

- Vue 3 + TypeScript analysis dashboard
- Drag-and-drop npm, Yarn and pnpm manifest upload
- Flask application factory and versioned JSON API
- Manifest validation with a 5 MB default limit
- Parsers for `package.json`, `package-lock.json`, `npm-shrinkwrap.json`, `yarn.lock` and `pnpm-lock.yaml`
- Local retrieval baseline using the prepared CVE instruction dataset
- Dependency-level risk, confidence, CVE evidence and recommendations
- Optional OpenAI-compatible Qwen enrichment
- Persistent JSON reports and report retrieval by ID
- Frontend JSON export
- Backend parser and API tests

## Architecture

```text
Browser (Vue, port 5173)
        |
        | /api through the Vite development proxy
        v
Flask API (port 5000)
        |
        +-- manifest validation and dependency parsing
        +-- local prepared-CVE retrieval baseline
        +-- conservative risk scoring
        +-- optional Qwen enrichment
        `-- generated JSON report storage
```

The current web application uses **Vue 3**, not React. The optional model adapter in `adapters/` was trained against Qwen2.5-0.5B-Instruct; it is not loaded into the web API unless a compatible model server is configured.

## Project layout

```text
project/
├── backend/
│   ├── niro_api/
│   │   ├── __init__.py             # Flask application factory
│   │   ├── analysis_service.py     # scoring and report creation
│   │   ├── config.py               # environment configuration
│   │   ├── cve_index.py            # local CVE retrieval index
│   │   ├── dependency_parser.py    # manifest parsers
│   │   ├── qwen_client.py          # optional model API client
│   │   ├── report_store.py         # generated report persistence
│   │   └── routes.py               # HTTP endpoints
│   ├── tests/
│   ├── app.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/components/
│   ├── src/services/
│   ├── src/App.vue
│   ├── package.json
│   └── .env.example
├── data/
│   ├── sample_inputs/
│   └── training/
├── scripts/                        # CVE preparation and LoRA experiments
├── adapters/                       # experimental LoRA adapter metadata
├── requirements-ml.txt
└── README.md
```

## Prerequisites

- Python 3.11 or newer for the API (Python 3.11 or 3.12 is recommended for ML work)
- Node.js `22.18+` or `24.12+`
- npm 10 or newer
- Two terminal windows for local development

The application baseline works without a GPU and without a running Qwen model.

## Qwen Model Download
```bash 
cd /workspaces/niro_ai/project
source .venv/bin/activate
```
1. Create a new folder called `model`
```bash 
mkdir -p models/qwen_gguf
```
2. Install Hugging Face CLI and login

```bash 
pip install -U huggingface_hub
hf auth login
```

3. Download the Qwen 3.5-9B GGUF Model

```bash
hf download bartowski/Qwen_Qwen3.5-9B-GGUF \
  --include "Qwen_Qwen3.5-9B-Q4_K_M.gguf" \
  --local-dir models/qwen_gguf
```

4. Install the llama-cpp server

```bash 
sudo apt-get update
sudo apt-get install -y build-essential cmake

CMAKE_ARGS="-DGGML_NATIVE=on" pip install "llama-cpp-python[server]"
```

5. Run Qwen model server

```bash 
python -m llama_cpp.server \
  --model models/qwen_gguf/Qwen_Qwen3.5-9B-Q4_K_M.gguf \
  --model_alias qwen3.5-9b \
  --host 0.0.0.0 \
  --port 8000 \
  --n_ctx 4096 \
  --n_threads $(nproc)
```


## CVE data and model experiments

Install the optional ML dependencies in a separate virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-ml.txt
```

The scripts currently expect these paths relative to the `project` directory:

```bash
mkdir -p data/raw
mkdir -p data/processed
mkdir -p data/training
mkdir -p data/sample_inputs
mkdir -p scripts
mkdir -p adapters
mkdir -p outputs
mkdir -p models
```
Download CVE GitHub dataset (you can use any data set, that must be include in the `data/raw` directory)
```bash
rm -rf data/raw/cvelistV5

git clone --filter=blob:none --sparse https://github.com/CVEProject/cvelistV5.git data/raw/cvelistV5

cd data/raw/cvelistV5

git sparse-checkout init --cone

git sparse-checkout set \
  cves/2017 \
  cves/2018 \
  cves/2019 \
  cves/2020 \
  cves/2021 \
  cves/2022 \
  cves/2023 \
  cves/2024 \
  cves/2025 \
  cves/2026
```

Prepare data:

```bash
python scripts/01_parse_cves.py
python scripts/02_make_training_data.py
```

Run the small experimental training script only in an environment with enough memory:

Train the model with 1000 records (Change the number what ever want)
```bash
MAX_RECORDS=1000 python scripts/03_train_qwen_codespace_lora.py
```
```bash
python scripts/03_train_qwen_cpu_lora.py
python scripts/04_test_lora_adapter.py
```

The current script uses `Qwen/Qwen2.5-0.5B-Instruct` by default and can be changed through `MODEL_ID` during training. Model downloads require internet access. Do not commit base-model weights or private input data.

## Testing and build commands

### Backend

```bash
cd backend
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
pytest -q
```

### Frontend

```bash
cd frontend
npm run type-check
npm run build
```

Preview the production frontend build:

```bash
npm run preview
```

The production frontend still needs `/api` to be reverse-proxied to Flask, or `VITE_API_BASE_URL` must be set to the deployed API URL before building.

## Troubleshooting

### The dashboard says “API offline”

- Confirm Flask is running at `http://127.0.0.1:5000`.
- Open `http://127.0.0.1:5000/api/health` directly.
- Confirm Vite is running on port 5173 and its `/api` proxy was not changed.

### Upload returns “Unsupported file”

Rename/export the manifest using one of the supported exact names. General `.json`, PDF and text documents are intentionally rejected because this workflow analyses dependencies, not arbitrary CTI documents.

### All dependencies show `Unknown`

The prepared dataset is small and retrieval requires an exact package-name match. This result is expected for many manifests and does not imply safety. Check `dataset.records_indexed` in `/api/health`, then verify packages with current public advisory services.

### Qwen output is missing

Confirm `ENABLE_QWEN=true`, restart Flask, verify the model endpoint accepts OpenAI chat-completions requests, and make sure the `MODEL_NAME` alias exists on that server.

## Safety and research limitations

- Uses public defensive-security evidence only
- Does not execute packages, malware or uploaded manifest content
- Does not develop or test exploits
- Does not collect credentials or personal data
- Does not confirm vulnerability applicability by semantic version yet
- Does not claim that a zero-day exists
- Requires a human analyst to validate evidence, versions, patches and source freshness


## Quick start

The application lives in the repository's `project/` directory. From the repository root, enter it first:

```bash
cd project
```

Skip that command if your terminal is already in `project/`. Run the remaining commands from this directory unless a section says otherwise.

### 1. Start the backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
cp .env.example .env
python app.py
```

On Windows PowerShell, activate the environment with:

```powershell
.venv\Scripts\Activate.ps1
```

The API starts at `http://127.0.0.1:5000`. Confirm it is ready:

```bash
curl http://127.0.0.1:5000/api/health
```

### 2. Start the frontend

Open a second terminal:

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Open `http://localhost:5173`.

The default `VITE_API_BASE_URL=/api` uses Vite's development proxy, which forwards requests to `http://127.0.0.1:5000`. You do not need to put a backend hostname in frontend code.

### 3. Try the sample manifest

Upload `data/sample_inputs/sample-package.json` in the dashboard. A result with no local match means only that the limited prepared dataset has no exact package-name match; it is not a clean bill of health.

## Backend configuration

Copy `backend/.env.example` to `backend/.env`. Available settings:

| Variable | Default | Purpose |
| --- | --- | --- |
| `FLASK_DEBUG` | `true` in the example | Enables Flask development debugging |
| `SECRET_KEY` | development value | Replace outside local development |
| `CORS_ORIGINS` | localhost ports | Comma-separated allowed browser origins |
| `UPLOAD_FOLDER` | `uploads` | Stored manifest folder, relative to `backend/` |
| `REPORT_FOLDER` | `reports/generated` | Generated report folder |
| `CVE_DATA_PATH` | `../data/training/cve_instruction_train.jsonl` | Prepared local evidence dataset |
| `MAX_FILE_SIZE_MB` | `5` | Maximum upload size |
| `MAX_DEPENDENCIES` | `2500` | Maximum dependencies in one manifest |
| `ENABLE_QWEN` | `false` | Enables optional model enrichment |
| `QWEN_API_URL` | local port 8000 | OpenAI-compatible chat-completions endpoint |
| `MODEL_NAME` | `qwen2.5-0.5b-instruct` | Model alias sent to the server |
| `QWEN_TIMEOUT_SECONDS` | `90` | Model request timeout |

Do not commit `.env`, uploaded manifests, or generated reports. These paths are ignored by `.gitignore`.

## Frontend configuration

Copy `frontend/.env.example` to `frontend/.env`:

```env
VITE_API_BASE_URL=/api
```

For a separately hosted backend, set an absolute API prefix instead:

```env
VITE_API_BASE_URL=https://api.example.org/api
```

Add the deployed frontend origin to `CORS_ORIGINS` on the backend.

## API reference

All errors use this shape:

```json
{
  "success": false,
  "message": "A human-readable explanation."
}
```

### `GET /api/health`

Reports API, dataset and optional model status.

```bash
curl http://127.0.0.1:5000/api/health
```

### `POST /api/upload`

Validates, stores and parses a manifest without running analysis.

```bash
curl -X POST http://127.0.0.1:5000/api/upload \
  -F "file=@data/sample_inputs/sample-package.json;filename=package.json"
```

The response includes an `upload.id`, dependency count and a maximum 50-item preview. The ID can be supplied to `/api/analyze`:

```bash
curl -X POST http://127.0.0.1:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"upload_id":"UPLOAD_ID_FROM_THE_PREVIOUS_RESPONSE"}'
```

### `POST /api/analyze`

Uploads and analyses a manifest in one request. This is what the Vue application uses.

```bash
curl -X POST http://127.0.0.1:5000/api/analyze \
  -F "file=@data/sample_inputs/sample-package.json;filename=package.json"
```

The response contains:

- report ID and UTC generation time
- overall risk and confidence
- dependency and local CVE-match counts
- one assessment per dependency
- public CVE evidence where an exact match exists
- dataset coverage and limitations
- optional model output under `ai_analysis`
- `human_review_required: true`

### `GET /api/report/<report_id>`

Retrieves a generated report:

```bash
curl http://127.0.0.1:5000/api/report/REPORT_ID
```

Reports are stored as JSON under `backend/reports/generated/`.

The frontend can open a saved report directly with `http://localhost:5173/?report=REPORT_ID`.

## Supported manifest files

| File | Parser behaviour |
| --- | --- |
| `package.json` | Reads production, development, peer and optional dependencies |
| `package-lock.json` | Reads modern `packages` and legacy recursive dependency structures |
| `npm-shrinkwrap.json` | Uses the npm lockfile parser |
| `yarn.lock` | Reads Yarn selectors and resolved versions |
| `pnpm-lock.yaml` / `.yml` | Reads package and snapshot keys without executing YAML |

Only the exact file names above are accepted. Uploaded content is treated as data and is never executed.

## How risk analysis works

1. The backend extracts package names and version declarations from the manifest.
2. `cve_index.py` loads the prepared instruction JSONL file once and creates a package-name index.
3. Each dependency is matched by an exact, normalised package name. Version applicability is **not yet evaluated**.
4. Public severity evidence drives a conservative Low, Medium or High level. Dependencies without a local match receive `Unknown`, not `Low`.
5. The API includes limitations and always requires human review.
6. If Qwen is enabled and reachable, its structured interpretation is attached separately; the deterministic baseline is retained.

This local dataset is an experimental subset and is not a replacement for live OSV, NVD, GitHub Advisory Database or CISA KEV checks.

## Optional Qwen integration

The Flask API expects an OpenAI-compatible endpoint at `QWEN_API_URL`. Start your compatible model server separately, then change `backend/.env`:

```env
ENABLE_QWEN=true
QWEN_API_URL=http://127.0.0.1:8000/v1/chat/completions
MODEL_NAME=qwen2.5-0.5b-instruct
```

Restart Flask after changing the environment. If the model server fails or returns invalid JSON, analysis continues with the baseline and adds a warning to the report.

The adapter under `adapters/qwen_codespace_cve_lora_adapter/` is a PEFT LoRA adapter, not a standalone model. Load it with the same base model as the training script before exposing it through a compatible inference server. `scripts/04_test_lora_adapter.py` shows the direct Transformers/PEFT loading sequence.

## Author

Supun Hasanka<br>
MSc Cyber Security, University of the West of Scotland
