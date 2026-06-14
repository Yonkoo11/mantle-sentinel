"""Optional IPFS pinning via Pinata. If PINATA_JWT is absent, returns "" and the pipeline still
anchors the verdict by reportHash alone (the report is also saved locally under reports/)."""
import os
import json
import urllib.request


def pin_json(report: dict) -> str:
    jwt = os.getenv("PINATA_JWT")
    if not jwt:
        return ""
    body = json.dumps({"pinataContent": report}).encode()
    req = urllib.request.Request(
        "https://api.pinata.cloud/pinning/pinJSONToIPFS", data=body,
        headers={"Authorization": f"Bearer {jwt}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read()).get("IpfsHash", "")
    except Exception:
        return ""
