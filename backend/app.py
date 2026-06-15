"""Sentinel audit API — audit ANY contract on demand.

POST /audit { "address": "0x…" }   -> fetch verified source, audit, return verdict
POST /audit { "source": "..." }    -> audit pasted Solidity directly
GET  /health                       -> liveness + whether the LLM pass is active

Read-only by default: it returns the verdict/report. Writing the verdict on-chain stays a separate,
key-holding operator action (the CLI) so a public endpoint can't be spammed into draining gas.
Reuses the same audit pipeline as the CLI (agent/)."""
import os
import sys
import json
import re
import tempfile
import urllib.request
from typing import Optional, Tuple

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "agent"))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from static_pass import run_slither
from llm_pass import run_llm
from report import merge_findings, build_report, report_hash
from config import HUNYUAN_MODEL, SEVERITY

GRADE = [("A", 98), ("A", 92), ("B", 82), ("C", 68), ("D", 46), ("F", 22)]


def _clean(title: str) -> str:
    """Strip Slither's trailing '(/tmp/path#L-L):' file location from a finding title."""
    return re.sub(r"\s*\([^()]*#\d[\d\-,]*\):?\s*$", "", title).strip()

app = FastAPI(title="Sentinel Audit API")
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["POST", "GET"], allow_headers=["*"],
)


class AuditReq(BaseModel):
    address: Optional[str] = None
    source: Optional[str] = None


def fetch_source(address: str) -> Tuple[str, str]:
    """Verified source by address — Blockscout first, then Sourcify. Raises if neither has it."""
    bs = f"https://explorer.sepolia.mantle.xyz/api?module=contract&action=getsourcecode&address={address}"
    try:
        with urllib.request.urlopen(bs, timeout=40) as r:
            res = (json.loads(r.read()).get("result") or [{}])[0]
        if res.get("SourceCode"):
            return res["SourceCode"], res.get("ContractName", "Contract")
    except Exception:
        pass
    sc = f"https://sourcify.dev/server/files/any/5003/{address}"
    try:
        with urllib.request.urlopen(sc, timeout=40) as r:
            files = json.loads(r.read()).get("files", [])
        sols = [f for f in files if f.get("name", "").endswith(".sol")]
        if sols:
            return "\n\n".join(f["content"] for f in sols), sols[0]["name"]
    except Exception:
        pass
    raise RuntimeError("No verified source found for this address (Blockscout/Sourcify). Paste the source instead.")


@app.get("/health")
def health():
    return {"ok": True, "llm": bool(os.getenv("HUNYUAN_API_KEY") or os.getenv("TENCENT_SECRET_ID"))}


@app.post("/audit")
def audit(req: AuditReq):
    if req.source:
        source, name = req.source, "pasted.sol"
    elif req.address:
        try:
            source, name = fetch_source(req.address)
        except Exception as e:
            return {"error": str(e)}
    else:
        return {"error": "Provide an address or source."}

    # Slither needs a path; Slither refuses an existing --json target, so use a fresh dir.
    tmp_dir = tempfile.mkdtemp(prefix="sentinel_")
    src_path = os.path.join(tmp_dir, "Target.sol")
    with open(src_path, "w") as f:
        f.write(source)

    try:
        static = run_slither(src_path)
    except Exception as e:
        return {"error": f"Could not compile/analyze the contract: {str(e)[:200]}"}
    llm = run_llm(source)
    llm_active = bool(os.getenv("HUNYUAN_API_KEY") or (os.getenv("TENCENT_SECRET_ID") and os.getenv("TENCENT_SECRET_KEY")))

    findings = merge_findings(static, llm)
    model = HUNYUAN_MODEL if llm_active else "slither-only"
    report = build_report(req.address or name, name, findings, model, 0)
    _, hex_hash = report_hash(report)
    v = report["verdict"]
    g = GRADE[v["highestSeverity"]] if v["highestSeverity"] < len(GRADE) else GRADE[-1]

    return {
        "target": req.address or name,
        "engine": "slither" + (" + hunyuan" if llm_active else ""),
        "pass": v["pass"],
        "grade": g[0],
        "score": g[1],
        "vulnCount": v["vulnCount"],
        "highestSeverity": v["highestSeverity"],
        "highestSeverityLabel": [k for k, val in SEVERITY.items() if val == v["highestSeverity"]][:1],
        "reportHash": hex_hash,
        "findings": [
            {"severity": f["severity"], "title": _clean(f["title"]), "lines": f.get("lines", []), "sources": f.get("sources", [])}
            for f in findings
        ],
    }
