# Niro AI

## Dependency-Aware CTI Assistant for Future Zero-Day Risk Exposure Analysis

Niro AI is an AI-driven cybersecurity prototype developed for an MSc Cyber Security project. The system uses `package.json` and lock files to identify software dependencies, analyse public cyber threat intelligence, and estimate future zero-day risk exposure.

The project does **not** claim to confirm or predict exact future zero-day attacks. Instead, it provides structured risk evidence, candidate zero-day indicators, confidence scores and recommended actions to support early security triage and human analyst review.

---

## Project Title

**Evaluating an AI-Driven Doc-to-LoRA Framework for Proactive Detection and Structured Analysis of Candidate Zero-Day Vulnerabilities from Public Cyber Threat Intelligence**

---

## Project Overview

Modern JavaScript and Node.js applications depend heavily on open-source packages. These packages are usually managed through dependency files such as:

- `package.json`
- `package-lock.json`
- `yarn.lock`
- `pnpm-lock.yaml`

These files show which packages and versions are used inside a software project. A vulnerable, outdated or poorly maintained dependency can create security risks for the full application.

Niro AI uses these dependency files as the user input. The system extracts package names and versions, then combines this information with public vulnerability intelligence from the official CVE List repository. The extracted CVE data is parsed, cleaned and converted into instruction-style training data for Qwen3.5-9B LoRA-based analysis.

For the current implementation, the main public dataset used is:

```text
https://github.com/CVEProject/cvelistV5.git
```

---

## Important Disclaimer

Niro AI does **not** predict confirmed future zero-day attacks.

The system estimates **future zero-day risk exposure** using:

- Historical vulnerability behaviour
- Public CVE evidence
- Package version information
- Patch and advisory evidence
- Severity and weakness information
- Dependency risk patterns
- AI-assisted structured vulnerability analysis

The output should be treated as an early-warning and decision-support report. Human analyst review is still required.

---

## Main Features

- Upload `package.json` or lock files
- Extract package names and versions
- Parse public CVE JSON records from `CVEProject/cvelistV5`
- Convert CVE records into instruction-style JSONL training data
- Support Qwen3.5-9B model connection
- Support LoRA / Doc-to-LoRA-style model adaptation
- Analyse dependency-level vulnerability evidence
- Estimate future zero-day risk exposure
- Generate structured vulnerability risk reports
- Display confidence score and recommended actions

---

## Technology Stack

### Frontend

- React
- Vite
- JavaScript
- CSS / Tailwind CSS
- PrimeReact or custom UI components

### Backend

- Python
- Flask API
- Flask-CORS
- Requests
- JSON processing
- CVE data parsing
- Qwen model API connection

### AI / Model

- Qwen3.5-9B
- LoRA adapter
- Hugging Face Transformers
- PEFT
- BitsAndBytes
- GitHub Codespaces for development, data preparation and testing
- GPU environment required for full Qwen3.5-9B LoRA training if Codespaces has no GPU

### Main Data Source

- CVEProject/cvelistV5 official CVE JSON repository

---

## Updated Project Folder Structure

```text
niro-ai/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── dependency_parser.py
│   │   ├── cve_parser.py
│   │   ├── training_data_builder.py
│   │   ├── cti_collector.py
│   │   ├── cti_preprocessor.py
│   │   ├── retrieval_baseline.py
│   │   ├── qwen_client.py
│   │   ├── lora_analyzer.py
│   │   ├── risk_scoring.py
│   │   ├── report_generator.py
│   │   └── utils.py
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── health_routes.py
│   │   ├── upload_routes.py
│   │   ├── analyze_routes.py
│   │   └── report_routes.py
│   │
│   ├── scripts/
│   │   ├── 01_clone_cvelist.sh
│   │   ├── 01_parse_cves.py
│   │   ├── 02_make_training_data.py
│   │   ├── 03_check_gpu.py
│   │   ├── 04_train_qwen_lora.py
│   │   ├── 05_test_qwen.py
│   │   └── 06_test_api.py
│   │
│   ├── data/
│   │   ├── raw/
│   │   │   └── cvelistV5/
│   │   ├── processed/
│   │   │   └── cve_records.jsonl
│   │   ├── training/
│   │   │   └── cve_instruction_train.jsonl
│   │   └── sample_inputs/
│   │       ├── sample-package.json
│   │       └── sample-package-lock.json
│   │
│   ├── models/
│   │   ├── qwen_gguf/
│   │   └── lora_adapter/
│   │
│   ├── reports/
│   │   ├── generated/
│   │   └── samples/
│   │
│   ├── uploads/
│   │
│   ├── tests/
│   │   ├── test_dependency_parser.py
│   │   ├── test_cve_parser.py
│   │   ├── test_risk_scoring.py
│   │   └── test_api_routes.py
│   │
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md
│
├── frontend/
│   ├── public/
│   │   └── niro-logo.png
│   │
│   ├── src/
│   │   ├── assets/
│   │   │   ├── images/
│   │   │   └── icons/
│   │   │
│   │   ├── components/
│   │   │   ├── layout/
│   │   │   │   ├── Header.jsx
│   │   │   │   ├── Sidebar.jsx
│   │   │   │   └── Footer.jsx
│   │   │   │
│   │   │   ├── upload/
│   │   │   │   └── FileUploadBox.jsx
│   │   │   │
│   │   │   ├── dashboard/
│   │   │   │   ├── RiskCard.jsx
│   │   │   │   ├── VulnerabilityTable.jsx
│   │   │   │   ├── EvidencePanel.jsx
│   │   │   │   ├── RecommendationCard.jsx
│   │   │   │   └── ConfidenceScore.jsx
│   │   │   │
│   │   │   └── common/
│   │   │       ├── LoadingSpinner.jsx
│   │   │       ├── ErrorMessage.jsx
│   │   │       ├── PageTitle.jsx
│   │   │       └── StatusBadge.jsx
│   │   │
│   │   ├── pages/
│   │   │   ├── Home.jsx
│   │   │   ├── Upload.jsx
│   │   │   ├── Results.jsx
│   │   │   ├── Report.jsx
│   │   │   └── Methodology.jsx
│   │   │
│   │   ├── services/
│   │   │   └── api.js
│   │   │
│   │   ├── hooks/
│   │   │   └── useAnalysis.js
│   │   │
│   │   ├── utils/
│   │   │   ├── riskUtils.js
│   │   │   └── fileUtils.js
│   │   │
│   │   ├── data/
│   │   │   └── demoResult.js
│   │   │
│   │   ├── styles/
│   │   │   └── main.css
│   │   │
│   │   ├── App.jsx
│   │   └── main.jsx
│   │
│   ├── package.json
│   ├── vite.config.js
│   └── README.md
│
├── docs/
│   ├── system_architecture.md
│   ├── api_documentation.md
│   ├── dataset_description.md
│   └── user_manual.md
│
├── evaluation/
│   ├── test_cases.md
│   ├── baseline_results.json
│   ├── lora_results.json
│   └── evaluation_summary.md
│
├── .gitignore
├── README.md
└── docker-compose.yml
```

---

## System Workflow

```text
User uploads package.json or lock file
↓
React frontend sends file to Flask API
↓
Flask receives and validates the uploaded file
↓
Dependency parser extracts package names and versions
↓
CVE parser prepares records from CVEProject/cvelistV5
↓
Training data builder creates instruction-style JSONL examples
↓
Qwen3.5-9B + LoRA analysis extracts structured vulnerability evidence
↓
Retrieval baseline checks known vulnerability matches
↓
Risk scoring module estimates future zero-day risk exposure
↓
Report generator creates structured output
↓
React frontend displays the final report
```

---

## Backend Setup

Go to the backend folder:

```bash
cd backend
```

Create a Python virtual environment:

```bash
python -m venv .venv
```

Activate the environment:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Run the Flask API:

```bash
python app/main.py
```

The backend should run on:

```text
http://localhost:5000
```

---

## Backend Requirements

Example `backend/requirements.txt`:

```txt
flask
flask-cors
python-dotenv
requests
tqdm
datasets
transformers
accelerate
peft
bitsandbytes
torch
```

---

## Environment Variables

Create a `.env` file inside the `backend` folder.

Example:

```env
FLASK_ENV=development
FLASK_DEBUG=True
QWEN_API_URL=http://127.0.0.1:8000/v1/chat/completions
MODEL_NAME=qwen3.5-9b
UPLOAD_FOLDER=uploads
REPORT_FOLDER=reports/generated
CVE_DATA_PATH=data/processed/cve_records.jsonl
TRAINING_DATA_PATH=data/training/cve_instruction_train.jsonl
```

Do not push `.env` files to GitHub.

---

## CVE Dataset Setup in Codespaces

For the current implementation, the project uses only this public repository:

```text
https://github.com/CVEProject/cvelistV5.git
```

Clone the repository using sparse checkout because the repository is large:

```bash
cd backend

git clone --filter=blob:none --sparse https://github.com/CVEProject/cvelistV5.git data/raw/cvelistV5
cd data/raw/cvelistV5
```

Download only the selected CVE year folders:

```bash
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

Return to the backend folder:

```bash
cd ../../..
```

---

## CVE Parsing and Training Data Preparation

Run the CVE parser:

```bash
python scripts/01_parse_cves.py
```

This creates:

```text
data/processed/cve_records.jsonl
```

Create instruction-style training data:

```bash
python scripts/02_make_training_data.py
```

This creates:

```text
data/training/cve_instruction_train.jsonl
```

---

## GPU Check in Codespaces

Before training Qwen3.5-9B, check whether the Codespace has GPU support:

```bash
python scripts/03_check_gpu.py
```

Expected output if no GPU is available:

```text
CUDA available: False
No GPU found. Use Codespace for data preparation and prototype development.
```

If no GPU is available, do not train Qwen3.5-9B inside Codespaces. Use Codespaces for dataset preparation, backend, frontend and testing. Full LoRA training requires a GPU environment.

---

## Qwen Model Hosting

The Qwen model can be hosted locally using a quantized GGUF model and `llama-cpp-python`.

Example server command:

```bash
python -m llama_cpp.server \
  --model models/qwen_gguf/Qwen3.5-9B-Q4_K_M.gguf \
  --model_alias qwen3.5-9b \
  --host 0.0.0.0 \
  --port 8000 \
  --n_ctx 4096 \
  --n_threads $(nproc)
```

The Flask backend sends prompts to:

```text
http://127.0.0.1:8000/v1/chat/completions
```

---

## LoRA Training

Codespaces can be used to prepare the dataset and run the training script only if GPU support is available.

Training process:

```text
Clone CVEProject/cvelistV5
↓
Parse CVE JSON records
↓
Extract CVE ID, description, affected product, CWE, CVSS and references
↓
Convert records into instruction-style JSONL examples
↓
Check GPU availability
↓
Load Qwen3.5-9B in 4-bit
↓
Train LoRA adapter
↓
Save adapter files
↓
Use adapter for structured vulnerability evidence analysis
```

Run training only if GPU is available:

```bash
python scripts/04_train_qwen_lora.py
```

If the Codespace has no GPU, the training data can still be prepared in Codespaces and moved to another GPU environment for training.

---

## Example Backend Endpoints

```text
GET  /health
POST /upload
POST /analyze
GET  /report/<report_id>
```

---

## Example API Request

```json
{
  "prompt": "Analyse this dependency risk for express version 4.18.2 and return structured vulnerability evidence."
}
```

Example response:

```json
{
  "package": "express",
  "installed_version": "4.18.2",
  "risk_level": "Medium",
  "candidate_zero_day_indicator": "Unclear",
  "confidence": 0.72,
  "recommendation": "Update to the latest stable version and monitor public CTI sources."
}
```

---

## Frontend Setup

Go to the frontend folder:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Run the React app:

```bash
npm run dev
```

The frontend should run on:

```text
http://localhost:5173
```

---

## Frontend to Backend Connection

The frontend communicates with the Flask backend through `frontend/src/services/api.js`.

Example:

```javascript
const API_BASE_URL = "http://localhost:5000";

export async function analyzePackageFile(file) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/analyze`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error("Analysis failed");
  }

  return await response.json();
}
```

In Codespaces, replace `localhost` with the public Codespace port URL for Flask.

---

## Example Report Output Fields

The final report may include:

- Package name
- Installed version
- Known vulnerability evidence
- CVE ID
- CWE category
- CVSS score
- Severity
- Patch status
- Exploit evidence
- Candidate zero-day indicator
- Future zero-day risk exposure level
- Confidence score
- Source evidence
- Recommended action
- Human review note

---

## Risk Levels

```text
Low:
Limited vulnerability history and no strong public exploitation evidence.

Medium:
Some vulnerability history, outdated version use or unclear patch signals.

High:
Repeated vulnerability history, high severity issues, known exploitation evidence or weak patching behaviour.
```

---

## Safety and Ethics

This project uses public cybersecurity data only.

The project does not include:

- Malware execution
- Exploit development
- Real attack testing
- Private company data
- Personal data
- Credential collection
- Live exploitation

The system is designed for defensive security research, early risk triage and educational purposes.

---

## GitHub Notes

Do not push these files to GitHub:

- Qwen model files
- `.gguf` files
- `.safetensors` files
- LoRA adapter files
- Large CVE datasets
- `.env` files
- Generated reports with sensitive data
- Uploaded dependency files from real users

Use `.gitignore` to protect large and sensitive files.

---

## Suggested `.gitignore`

```gitignore
.venv/
__pycache__/
*.pyc

backend/data/raw/
backend/data/processed/
backend/data/training/
backend/uploads/
backend/reports/generated/
backend/models/

*.gguf
*.safetensors
*.bin
*.pt
*.pth

.env
node_modules/
dist/
build/
.DS_Store
```

---

## MSc Report Description

This project was organised using a separated frontend and backend architecture. The frontend was developed using React with a component-based structure, while the backend was developed using a Flask API. Backend functionality was separated into modules for dependency parsing, CVE data preparation, CTI processing, model communication, risk scoring and report generation. The public `CVEProject/cvelistV5` repository was used as the main CVE dataset for preparing structured vulnerability evidence and instruction-style training data.

GitHub Codespaces was used for development, CVE dataset preparation, backend testing, frontend testing and Qwen model integration. If GPU support is not available in Codespaces, full Qwen3.5-9B LoRA training should be completed in a GPU-supported environment using the same prepared training dataset.

---

## Project Status

Current development status:

- [ ] Frontend React setup
- [ ] Flask backend setup
- [ ] `package.json` upload
- [ ] Dependency parser
- [ ] Clone `CVEProject/cvelistV5`
- [ ] CVE parser
- [ ] Instruction-style training data builder
- [ ] GPU check in Codespaces
- [ ] Qwen model hosting
- [ ] LoRA training
- [ ] Risk scoring
- [ ] Report generation
- [ ] Testing and evaluation

---

## Author

**Supun Hasanka**

MSc Cyber Security  
University of the West of Scotland

---

## Final Note

Niro AI is an academic prototype for estimating dependency-level future zero-day risk exposure using public CVE data, dependency files and AI-assisted analysis. It should not be treated as a commercial vulnerability scanner or a confirmed zero-day prediction system.
