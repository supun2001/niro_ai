import json
from pathlib import Path
from tqdm import tqdm

INPUT_FILE = Path("data/processed/cve_records.jsonl")
OUTPUT_FILE = Path("data/training/cve_instruction_train.jsonl")

MAX_RECORDS = 3000


def build_input(record):
    return f"""
CVE ID: {record.get("cve_id")}
Published Date: {record.get("date_published")}
Updated Date: {record.get("date_updated")}
Title: {record.get("title")}
Description: {record.get("description")}
Affected: {record.get("affected")}
Problem Types: {record.get("problem_types")}
Metrics: {record.get("metrics")}
References: {record.get("references")[:5]}
""".strip()


def build_output(record):
    return {
        "cve_id": record.get("cve_id"),
        "summary": record.get("description"),
        "affected": record.get("affected"),
        "severity": "Extract from CVSS metrics if available",
        "patch_status": "Check advisory references",
        "exploit_evidence": "Not confirmed from CVE record alone",
        "candidate_zero_day_indicator": "No",
        "future_zero_day_risk_exposure": "Unknown from CVE record alone",
        "recommendation": "Review affected versions, check vendor advisory, and update if a fixed version is available.",
        "human_review_required": True
    }


def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"{INPUT_FILE} not found. Run scripts/01_parse_cves.py first."
        )

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    count = 0

    with open(INPUT_FILE, "r", encoding="utf-8") as file, open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        for line in tqdm(file):
            if count >= MAX_RECORDS:
                break

            record = json.loads(line)

            example = {
                "instruction": (
                    "Extract structured vulnerability evidence from this CVE record. "
                    "Return valid JSON only. Do not claim a confirmed zero-day unless the evidence clearly supports it."
                ),
                "input": build_input(record),
                "output": json.dumps(build_output(record), ensure_ascii=False)
            }

            out.write(json.dumps(example, ensure_ascii=False) + "\n")
            count += 1

    print(f"Saved {count} training examples to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()