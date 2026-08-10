"""Dependency-level evidence retrieval and conservative risk scoring."""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from uuid import uuid4

from .cve_index import CveIndex
from .dependency_parser import Dependency
from .qwen_client import QwenClient


SEVERITY_ORDER = {"UNKNOWN": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}


class AnalysisService:
    def __init__(self, cve_index: CveIndex, qwen_client: QwenClient):
        self.cve_index = cve_index
        self.qwen_client = qwen_client

    def create_report(self, filename: str, dependencies: list[Dependency]) -> dict:
        assessments = [self._assess(dependency) for dependency in dependencies]
        known_count = sum(len(item["known_vulnerabilities"]) for item in assessments)
        matched_count = sum(bool(item["known_vulnerabilities"]) for item in assessments)
        distribution = Counter(item["risk_level"] for item in assessments)
        overall_risk = _overall_risk(assessments)

        baseline_summary = {
            "dependency_count": len(dependencies),
            "dependencies_with_matches": matched_count,
            "known_vulnerability_count": known_count,
            "overall_risk_level": overall_risk,
            "risk_distribution": {
                key: distribution.get(key, 0)
                for key in ("High", "Medium", "Low", "Unknown")
            },
            "confidence": _report_confidence(assessments),
        }

        qwen_input = {
            "summary": {
                "dependency_count": baseline_summary["dependency_count"],
                "dependencies_with_matches": baseline_summary["dependencies_with_matches"],
                "known_vulnerability_count": baseline_summary["known_vulnerability_count"],
                "overall_risk_level": baseline_summary["overall_risk_level"],
            },
            "matched_dependencies": [
                {
                    "package": item["package"],
                    "risk_level": item["risk_level"],
                    "installed_version": item["installed_version"],
                    "known_vulnerabilities": [
                        {
                            "cve_id": vuln.get("cve_id"),
                            "severity": vuln.get("severity"),
                            "summary": vuln.get("summary"),
                        }
                        for vuln in item["known_vulnerabilities"][:2]
                    ],
                }
                for item in assessments if item["known_vulnerabilities"]
            ][:10],
        }
        ai_analysis, ai_warning = self.qwen_client.analyze(qwen_input)

        notes = [
            "Results are limited to exact package-name matches in the prepared public CVE dataset.",
            "No match is not proof that a dependency is safe or free of vulnerabilities.",
            "Future zero-day exposure is an estimate for triage, not a prediction.",
        ]
        if self.cve_index.load_error:
            notes.insert(0, self.cve_index.load_error)
        if ai_warning:
            notes.append(ai_warning)

        suggestions = self._generate_suggestions(assessments, baseline_summary)

        return {
            "report_id": str(uuid4()),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source_file": filename,
            "analysis_mode": "qwen-assisted" if ai_analysis else "local-retrieval-baseline",
            "summary": baseline_summary,
            "assessments": assessments,
            "ai_analysis": ai_analysis,
            "suggestions": suggestions,
            "coverage": {
                "dataset": self.cve_index.data_path.name,
                "records_indexed": self.cve_index.record_count,
                "dataset_available": self.cve_index.available,
            },
            "limitations": notes,
            "human_review_required": True,
        }

    def _assess(self, dependency: Dependency) -> dict:
        matches = self.cve_index.lookup(dependency.name)
        highest = max(
            (SEVERITY_ORDER.get(str(item.get("severity", "Unknown")).upper(), 0) for item in matches),
            default=0,
        )

        if not matches:
            risk_level = "Unknown"
            confidence = 0.2
            recommendation = "Verify this package with a current advisory source and keep it updated."
            candidate_indicator = "No evidence in the local dataset"
        elif highest >= SEVERITY_ORDER["HIGH"]:
            risk_level = "High"
            confidence = min(0.85, 0.6 + len(matches) * 0.04)
            recommendation = "Prioritise advisory review, confirm affected versions and apply the latest supported fix."
            candidate_indicator = "Unclear — public evidence requires analyst review"
        elif highest == SEVERITY_ORDER["MEDIUM"] or highest == 0:
            risk_level = "Medium"
            confidence = min(0.8, 0.55 + len(matches) * 0.04)
            recommendation = "Review the matched advisories and update to a supported, patched version."
            candidate_indicator = "Unclear — no confirmed zero-day evidence"
        else:
            risk_level = "Low"
            confidence = min(0.75, 0.5 + len(matches) * 0.04)
            recommendation = "Review the advisory and include the dependency in the normal update cycle."
            candidate_indicator = "No confirmed zero-day evidence"

        return {
            "package": dependency.name,
            "installed_version": dependency.version,
            "dependency_group": dependency.group,
            "risk_level": risk_level,
            "confidence": confidence,
            "candidate_zero_day_indicator": candidate_indicator,
            "known_vulnerabilities": matches,
            "recommendation": recommendation,
            "human_review_required": True,
        }

    def _generate_suggestions(self, assessments: list[dict], summary: dict) -> list[dict]:
        """Generate actionable remediation suggestions based on the analysis."""
        suggestions = []

        # High-risk packages that need immediate attention
        high_risk_packages = [a for a in assessments if a["risk_level"] == "High"]
        if high_risk_packages:
            suggestions.append({
                "priority": "critical",
                "title": "Review and patch high-risk dependencies",
                "description": f"Found {len(high_risk_packages)} package(s) with high-severity vulnerabilities. These should be prioritized for immediate review and patching.",
                "packages": [p["package"] for p in high_risk_packages[:5]],
                "action": "Review advisories and apply latest patches immediately"
            })

        # Medium-risk packages
        medium_risk_packages = [a for a in assessments if a["risk_level"] == "Medium"]
        if medium_risk_packages:
            suggestions.append({
                "priority": "high",
                "title": "Plan updates for medium-risk dependencies",
                "description": f"Found {len(medium_risk_packages)} package(s) with medium-severity vulnerabilities. Include these in your next maintenance cycle.",
                "packages": [p["package"] for p in medium_risk_packages[:5]],
                "action": "Schedule updates to patched versions"
            })

        # Dependencies with no local match
        unknown_packages = [a for a in assessments if a["risk_level"] == "Unknown"]
        if unknown_packages and len(unknown_packages) > summary["dependency_count"] * 0.3:
            suggestions.append({
                "priority": "medium",
                "title": "Verify dependencies with no local CVE data",
                "description": f"{len(unknown_packages)} dependencies have no matches in the local CVE dataset. This doesn't mean they're safe—verify using external advisory sources.",
                "action": "Cross-check packages against NVD, GitHub Security Advisories, or vendor security feeds"
            })

        # Overall risk assessment recommendations
        if summary["overall_risk_level"] == "High":
            suggestions.append({
                "priority": "critical",
                "title": "Urgent: Overall project risk is high",
                "description": "This project contains dependencies with confirmed high-severity vulnerabilities. Immediate action is required.",
                "action": "Establish a hotfix process and prioritize CVE patching"
            })
        elif summary["overall_risk_level"] == "Medium":
            suggestions.append({
                "priority": "high",
                "title": "Medium-risk exposure detected",
                "description": "Plan a comprehensive dependency update cycle to reduce medium-severity risks.",
                "action": "Schedule maintenance window for dependency updates"
            })

        # Low-risk or no matches - proactive recommendation
        if summary["overall_risk_level"] == "Low" or summary["overall_risk_level"] == "Unknown":
            suggestions.append({
                "priority": "low",
                "title": "Establish continuous monitoring",
                "description": "Even with low current risk, dependencies should be monitored for new vulnerabilities.",
                "action": "Set up automated dependency scanning and security alerts"
            })

        # Too many dependencies with matches might indicate outdated ecosystem
        if summary["dependencies_with_matches"] > summary["dependency_count"] * 0.4:
            suggestions.append({
                "priority": "high",
                "title": "Consider a major dependency refresh",
                "description": f"Over 40% of dependencies ({summary['dependencies_with_matches']}/{summary['dependency_count']}) have known vulnerabilities.",
                "action": "Evaluate newer versions or alternative packages"
            })

        return suggestions


def _overall_risk(assessments: list[dict]) -> str:
    levels = {item["risk_level"] for item in assessments}
    for level in ("High", "Medium", "Low"):
        if level in levels:
            return level
    return "Unknown"


def _report_confidence(assessments: list[dict]) -> float:
    matched = [item["confidence"] for item in assessments if item["known_vulnerabilities"]]
    return round(sum(matched) / len(matched), 2) if matched else 0.2
