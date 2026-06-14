"""Mantle Sentinel — orchestrator.

Usage:
  python run.py --file samples/VulnerableVault.sol --target 0x<addr> [--agent-id N] [--attest]
  python run.py --address 0x<deployed-addr> [--attest]      (fetches verified source from the explorer)

Pipeline: source -> Slither + Hunyuan -> merge -> canonical report -> keccak hash -> (IPFS) -> on-chain.
Without --attest it does a dry run (audit + report only), so you can see findings before paying gas."""
import argparse
import json
import os
import sys
import urllib.request

from static_pass import run_slither
from llm_pass import run_llm
from report import merge_findings, build_report, report_hash, canonical_bytes
from ipfs import pin_json
from config import HUNYUAN_MODEL, EXPLORER_ADDR

REPORTS_DIR = os.path.join(os.path.dirname(__file__), "reports")


def fetch_source(address: str) -> tuple[str, str]:
    """Fetch verified source from the Mantlescan/Blockscout API. Returns (source_text, name)."""
    url = f"https://explorer.sepolia.mantle.xyz/api?module=contract&action=getsourcecode&address={address}"
    with urllib.request.urlopen(url, timeout=60) as r:
        data = json.loads(r.read())
    res = (data.get("result") or [{}])[0]
    src = res.get("SourceCode", "")
    if not src:
        raise RuntimeError("No verified source found for this address on the explorer.")
    return src, res.get("ContractName", "Contract")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", help="local .sol file to audit")
    ap.add_argument("--address", help="audit a verified on-chain contract by address")
    ap.add_argument("--target", help="target address to key the attestation by (defaults to --address)")
    ap.add_argument("--agent-id", type=int, default=0, help="ERC-8004 agentId of the target, if any")
    ap.add_argument("--attest", action="store_true", help="write the verdict on-chain (costs gas)")
    args = ap.parse_args()

    if args.file:
        with open(args.file) as f:
            source = f.read()
        source_name = os.path.basename(args.file)
        source_path = args.file
    elif args.address:
        source, source_name = fetch_source(args.address)
        source_path = os.path.join("reports", f"{args.address}.sol")
        os.makedirs(REPORTS_DIR, exist_ok=True)
        with open(source_path, "w") as f:
            f.write(source)
    else:
        print("error: provide --file or --address", file=sys.stderr)
        sys.exit(2)

    target = args.target or args.address
    if not target:
        print("error: provide --target (or use --address)", file=sys.stderr)
        sys.exit(2)

    # 1. static ground-truth pass
    static = run_slither(source_path)
    # 2. LLM reasoning pass (empty if no Tencent credentials -> reported honestly)
    llm = run_llm(source)
    llm_active = bool(os.getenv("HUNYUAN_API_KEY") or (os.getenv("TENCENT_SECRET_ID") and os.getenv("TENCENT_SECRET_KEY")))

    findings = merge_findings(static, llm)
    model_version = HUNYUAN_MODEL if llm_active else "slither-only"
    report = build_report(target, source_name, findings, model_version, args.agent_id)
    digest, hex_hash = report_hash(report)

    os.makedirs(REPORTS_DIR, exist_ok=True)
    with open(os.path.join(REPORTS_DIR, f"{target}.json"), "wb") as f:
        f.write(canonical_bytes(report))

    v = report["verdict"]
    print("=" * 64)
    print(f"TARGET:   {target}")
    print(f"SOURCE:   {source_name}")
    print(f"ENGINE:   slither + {'hunyuan(active)' if llm_active else 'hunyuan(inactive, no key)'}")
    print(f"VERDICT:  {'PASS' if v['pass'] else 'FAIL'}  | findings: {v['vulnCount']}  | highest severity: {v['highestSeverity']}")
    print(f"HASH:     {hex_hash}")
    print("-" * 64)
    for fnd in findings:
        lines = ",".join(str(x) for x in fnd.get("lines", [])) or "?"
        print(f"  [{fnd['severity'].upper():>8}] L{lines}: {fnd['title']}  ({'+'.join(fnd.get('sources', []))})")
    print("=" * 64)

    if not args.attest:
        print("dry run (no on-chain write). add --attest to record the verdict on Mantle.")
        return

    cid = pin_json(report)
    from attest import write_attestation
    res = write_attestation(target, v["pass"], v["vulnCount"], v["highestSeverity"],
                            args.agent_id, hex_hash, cid)
    print(f"on-chain registry tx: {res['registryTxUrl']}")
    if res.get("reputationTx"):
        print(f"ERC-8004 reputation tx: {res['reputationTxUrl']}")
    elif args.agent_id:
        print(f"ERC-8004 binding skipped: {res.get('reputationError', 'n/a')}")
    print(f"registry: {EXPLORER_ADDR}{__import__('config').AUDIT_REGISTRY}")


if __name__ == "__main__":
    main()
