"""Build the canonical audit report and its keccak256 hash.

The report is serialized with sorted keys + compact separators (a deterministic JSON form, in the
spirit of RFC 8785 / JCS) so the same findings always produce the same bytes -> the same hash.
Only this hash + the IPFS CID go on-chain, so anyone can re-download the report, re-hash it, and
prove it matches the on-chain verdict. Tamper-evident and falsifiable."""
import json
from typing import List, Dict, Tuple

from config import SEVERITY
from eth_utils import keccak

# A verdict "passes" only if no high/critical findings remain.
_BLOCKING = {"high", "critical"}


def merge_findings(static: List[Dict], llm: List[Dict]) -> List[Dict]:
    """Combine the two passes and de-duplicate by (severity bucket, overlapping lines)."""
    merged: List[Dict] = []
    for f in static + llm:
        dup = False
        for m in merged:
            same_sev = m["severity"] == f["severity"]
            overlap = set(m.get("lines", [])) & set(f.get("lines", []))
            if same_sev and overlap:
                # keep the static one's detector name, record both sources
                m["sources"] = sorted(set(m.get("sources", [m["source"]]) + [f["source"]]))
                dup = True
                break
        if not dup:
            f = dict(f)
            f["sources"] = [f["source"]]
            merged.append(f)
    # sort by severity desc, then first line
    merged.sort(key=lambda x: (-SEVERITY.get(x["severity"], 0), (x.get("lines") or [10**9])[0]))
    return merged


def build_report(target: str, source_name: str, findings: List[Dict],
                 model_version: str, erc8004_agent_id: int) -> Dict:
    highest = max([SEVERITY.get(f["severity"], 0) for f in findings], default=0)
    passed = not any(f["severity"] in _BLOCKING for f in findings)
    return {
        "schema": "mantle-agent-auditor/v1",
        "target": target.lower(),
        "sourceName": source_name,
        "erc8004AgentId": erc8004_agent_id,
        "modelVersion": model_version,
        "verdict": {"pass": passed, "vulnCount": len(findings), "highestSeverity": highest},
        "findings": findings,
    }


def canonical_bytes(report: Dict) -> bytes:
    return json.dumps(report, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def report_hash(report: Dict) -> Tuple[bytes, str]:
    """Return (32-byte keccak digest, 0x-hex string)."""
    h = keccak(canonical_bytes(report))
    return h, "0x" + h.hex()
