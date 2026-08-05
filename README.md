# Niro AI

## Dependency-Aware CTI Assistant for Future Zero-Day Risk Exposure Analysis

Niro AI is an AI-driven cybersecurity prototype developed for an MSc Cyber Security project. The system uses `package.json` and lock files to identify software dependencies, analyse public cyber threat intelligence, and estimate future zero-day risk exposure.

The project does **not** claim to confirm future zero-day attacks. Instead, it provides structured risk evidence, candidate zero-day indicators, confidence scores and recommended actions to support early security triage.

---

## Project Title

**Evaluating an AI-Driven Doc-to-LoRA Framework for Proactive Detection and Structured Analysis of Candidate Zero-Day Vulnerabilities from Public Cyber Threat Intelligence**

---

## Project Overview

Modern web applications depend heavily on open-source packages. In JavaScript and Node.js projects, dependencies are usually stored in files such as:

- `package.json`
- `package-lock.json`
- `yarn.lock`
- `pnpm-lock.yaml`

These files show which packages and versions are used by an application. A vulnerable or outdated dependency can create security risks for the whole system.

Niro AI uses these dependency files as input and combines them with public cyber threat intelligence sources such as CVE records, OSV, GitHub Security Advisories and CISA KEV. The system then uses an AI model to generate a structured vulnerability risk report.

---

## Important Disclaimer

Niro AI does **not** predict confirmed future zero-day attacks.

The system estimates **future zero-day risk exposure** using:

- Historical vulnerability behaviour
- Public CVE evidence
- Public CTI records
- Exploit history
- Patch status
- Package version information
- Dependency risk patterns

The output should be treated as an early-warning and decision-support report. Human analyst review is still required.

---

## Main Features

- Upload `package.json` or lock files
- Extract package names and versions
- Analyse dependency security risk
- Match packages with public vulnerability intelligence
- Use historical CVE data for risk pattern analysis
- Connect with Qwen3.5-9B model
- Support LoRA/Doc-to-LoRA-style model adaptation
- Generate structured vulnerability reports
- Estimate future zero-day risk exposure
- Display confidence score and recommendations

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
- Requests
- JSON processing
- Qwen model API connection

### AI / Model

- Qwen3.5-9B
- LoRA adapter
- Hugging Face Transformers
- PEFT
- Google Colab for training
- GitHub Codespaces for hosting and testing

### Data Sources

- CVE JSON records
- NVD-style vulnerability data
- OSV
- GitHub Security Advisories
- CISA Known Exploited Vulnerabilities
- Public CTI records

---

## Project Folder Structure

```text
zerorisk-ai/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── dependency_parser.py
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
│   │   ├── health_routes.py
│   │   ├── upload_routes.py
│   │   ├── analyze_routes.py
│   │   └── report_routes.py
│   │
│   ├── data/
│   │   ├── raw/
│   │   ├── processed/
│   │   ├── training/
│   │   └── sample_inputs/
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
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── assets/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── hooks/
│   │   ├── utils/
│   │   ├── styles/
│   │   ├── App.jsx
│   │   └── main.jsx
│   │
│   ├── package.json
│   ├── vite.config.js
│   └── README.md
│
├── docs/
├── evaluation/
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
Flask receives and validates the file
↓
Dependency parser extracts packages and versions
↓
CTI collector searches public vulnerability intelligence
↓
Retrieval baseline checks known vulnerability matches
↓
Qwen + LoRA model analyses vulnerability evidence
↓
Risk scoring module estimates future zero-day risk exposure
↓
Report generator creates structured output
↓
Frontend displays the final risk report
```

---

## Backend Setup

Go to the backend folder:

```bash
cd backend
```

Create a Python virtual environment:

```bash
python3 -m venv .venv
```

Activate the environment:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
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

## Environment Variables

Create a `.env` file inside the backend folder.

Example:

```env
FLASK_ENV=development
FLASK_DEBUG=True
QWEN_API_URL=http://127.0.0.1:8000/v1/chat/completions
MODEL_NAME=qwen3.5-9b
UPLOAD_FOLDER=uploads
REPORT_FOLDER=reports/generated
```

Do not push `.env` files to GitHub.

---

## Qwen Model Hosting

The Qwen model can be hosted locally inside GitHub Codespaces using a quantized GGUF model and `llama-cpp-python`.

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

Model training is performed in Google Colab because GitHub Codespaces is mainly used for development and prototype hosting.

Training process:

```text
Download 10 years of CVE JSON records
↓
Parse CVE records
↓
Extract CVE ID, description, affected product, CWE, CVSS and references
↓
Convert records into instruction-style JSONL examples
↓
Load Qwen3.5-9B in 4-bit
↓
Train LoRA adapter
↓
Save adapter files
↓
Upload adapter to Codespace or Hugging Face
```

The LoRA adapter is used to improve structured vulnerability evidence extraction.

---

## Example Report Output Fields

The final report may include:

- Package name
- Installed version
- Latest version
- Known vulnerabilities
- CVE / GHSA / OSV ID
- Severity
- CWE
- CVSS score
- Exploit evidence
- Patch status
- Candidate zero-day indicator
- Future zero-day risk level
- Confidence score
- Source evidence
- Recommended action

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

## MSc Report Description

This project was organised using a separated frontend and backend architecture. The frontend was developed using React with a component-based structure, while the backend was developed using a Flask API. Backend functionality was separated into modules for dependency parsing, CTI collection, preprocessing, model communication, risk scoring and report generation. This structure improved maintainability, readability and scalability of the prototype.

---

## Project Status

Current development status:

- [ ] Frontend React setup
- [ ] Flask backend setup
- [ ] package.json upload
- [ ] Dependency parser
- [ ] CVE dataset preparation
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

Niro AI is an academic prototype for estimating dependency-level future zero-day risk exposure using public CTI and AI-assisted analysis. It should not be treated as a commercial vulnerability scanner or a confirmed zero-day prediction system.
