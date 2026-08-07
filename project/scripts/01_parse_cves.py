import json
from pathlib import Path
from tqdm import tqdm

ROOT_DIR = Path("data/raw/cvelistV5/cves")
OUTPUT_FILE = Path("data/processed/cve_records.jsonl")

def safe_text(value):
    if value is None:
        return ""
    return str(value).replace("\n", " ").strip()

def get_english_description(descriptions):
    if not descriptions:
        return ""

    for item in descriptions:
        if item.get("lang") == "en":
            return safe_text(item.get("value"))

    return safe_text(descriptions[0].get("value"))

def parse_record(path):
    try:
        with open(path, "r", encoding="utf-8") as file:
            record = json.load(file)
    except Exception:
        return []
    # Support files that contain either a single record (dict) or a list of records
    records = record if isinstance(record, list) else [record]

    parsed_entries = []

    for rec in records:
        if not isinstance(rec, dict):
            continue

        metadata = rec.get("cveMetadata", {})
        containers = rec.get("containers", {})
        cna = containers.get("cna", {})

        cve_id = metadata.get("cveId")
        state = metadata.get("state")

        if not cve_id or state != "PUBLISHED":
            continue

        descriptions = cna.get("descriptions", [])
        affected = cna.get("affected", [])
        problem_types = cna.get("problemTypes", [])
        metrics = cna.get("metrics", [])
        references = cna.get("references", [])

        parsed_entries.append({
            "cve_id": cve_id,
            "date_published": metadata.get("datePublished"),
            "date_updated": metadata.get("dateUpdated"),
            "title": safe_text(cna.get("title")),
            "description": get_english_description(descriptions),
            "affected": affected,
            "problem_types": problem_types,
            "metrics": metrics,
            "references": [ref.get("url") for ref in references if ref.get("url")]
        })

    return parsed_entries

def main():
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    json_files = list(ROOT_DIR.rglob("*.json"))
    print(f"Found {len(json_files)} CVE JSON files")

    saved = 0

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        for path in tqdm(json_files):
            parsed_list = parse_record(path)

            for parsed in parsed_list:
                if parsed and parsed.get("description"):
                    out.write(json.dumps(parsed, ensure_ascii=False) + "\n")
                    saved += 1

    print(f"Saved {saved} CVE records to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()