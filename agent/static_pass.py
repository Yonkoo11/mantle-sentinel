"""Static analysis pass using Slither. Returns normalized findings with line numbers.
This is the ground-truth layer — it runs locally, no API key needed, and anchors the verdict
so the LLM pass can't hallucinate the whole report."""
import json
import subprocess
import tempfile
import os
from typing import List, Dict

# Slither impact -> our severity vocabulary
_IMPACT = {"High": "high", "Medium": "medium", "Low": "low", "Informational": "informational", "Optimization": "informational"}


def run_slither(source_path: str) -> List[Dict]:
    """Run Slither on a single .sol file, return a list of findings.
    Each finding: {detector, severity, title, lines:[int], confidence}."""
    # Slither refuses to overwrite an existing --json target, so use a path that does NOT exist yet.
    tmp_dir = tempfile.mkdtemp(prefix="slither_")
    out_json = os.path.join(tmp_dir, "out.json")
    try:
        # --json writes machine-readable results; non-zero exit just means findings exist.
        subprocess.run(
            ["slither", source_path, "--json", out_json],
            capture_output=True, text=True, timeout=180,
        )
        if not os.path.exists(out_json) or os.path.getsize(out_json) == 0:
            return []
        with open(out_json) as f:
            data = json.load(f)
    finally:
        if os.path.exists(out_json):
            os.unlink(out_json)
        if os.path.isdir(tmp_dir):
            os.rmdir(tmp_dir)

    findings = []
    if not data.get("success") and not data.get("results"):
        return findings
    for det in data.get("results", {}).get("detectors", []):
        lines = []
        for el in det.get("elements", []):
            sm = el.get("source_mapping", {})
            for ln in sm.get("lines", []) or []:
                lines.append(ln)
        findings.append({
            "detector": det.get("check", "unknown"),
            "severity": _IMPACT.get(det.get("impact", "Informational"), "informational"),
            "title": det.get("description", "").strip().split("\n")[0][:200],
            "lines": sorted(set(lines)),
            "confidence": det.get("confidence", "Medium"),
            "source": "slither",
        })
    return findings
