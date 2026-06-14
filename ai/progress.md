# Progress — Mantle Agent Auditor

## Status: Phase 1 Gate PASSED (verified on-chain)

### Deployed on Mantle Sepolia (chain 5003)
- AuditAttestationRegistry: `0xbCE17E724c0Cd038622a9C4299F86Caf411C1Fae`
- Sample vulnerable target (VulnerableVault): `0x469C46486d44eE02BB5A8d4FE341e55d13f5dF25`
- ERC-8004 IdentityRegistry (live, reference deploy): `0x8004A818BFB912233c491871b3d84c89A494BD9e`
- ERC-8004 ReputationRegistry (live, reference deploy): `0x8004B663056A597Dffe9eCcC1965A193B7388713`
- Deployer/auditor: `0xf9946775891a24462cD4ec885d0D4E2675C84355`

### What Changed (Plain English)
The auditor now works end to end. You point it at a contract, it reads the code, finds the real
security bugs (it caught a textbook "reentrancy" money-drain bug with the exact line numbers), decides
pass or fail, and stamps that verdict permanently onto Mantle. We checked the stamp by reading it back
from the chain: the bad contract correctly shows as "not safe." This is the core thing working for real,
not a mock.

### Verified
- 10/10 contract tests pass (`forge test`).
- Slither static pass finds the reentrancy (HIGH) with line numbers 13-18.
- Verdict written on-chain (registry tx `0x3c5212...`) and reads back: pass=false, vulnCount=3, severity=4,
  reportHash matches the locally computed hash.

### Done
- [x] Registry contract written, tested, deployed on Mantle Sepolia
- [x] Hybrid audit engine (Slither live; Hunyuan LLM pass coded, inactive until Tencent key)
- [x] Canonical report + keccak256 hash anchoring
- [x] On-chain attestation write + read-back (Phase 1 Gate)

### Next
- [ ] Verify registry source on Mantlescan/Blockscout (explorer API was 503; retry)
- [ ] ERC-8004 binding live test (giveFeedback) — needs a target with a real agentId
- [ ] Public frontend (GitHub Pages): paste address -> verdict + tx links
- [ ] Tencent Cloud Hunyuan: BLOCKED on user signup (HUNYUAN_API_KEY not set). LLM pass falls back to
      Slither-only and says so honestly until the key exists.
- [ ] README + MIT LICENSE + 2-min demo video

### Honest gaps
- LLM (Tencent) pass is written but UNTESTED live — no API key yet. Current verdicts are Slither-only.
- Registry source not yet verified on the explorer (cosmetic; contract works).
- ERC-8004 giveFeedback path is coded against the real ABI but not yet executed live.
