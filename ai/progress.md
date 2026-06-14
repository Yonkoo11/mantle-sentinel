# Progress — Sentinel

## Status: Phase 1 PASSED + deep ERC-8004 integration live + public demo shipped

LIVE DEMO: https://yonkoo11.github.io/mantle-sentinel/
REPO: https://github.com/Yonkoo11/mantle-sentinel

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
- [x] ERC-8004 binding live test PASSED — giveFeedback bound verdict to agent 186; getSummary returns count=1, value=20, tag=security-audit (tx 0x5965c8...)
- [x] Public frontend LIVE on GitHub Pages (reads live verdicts from Mantle; read path verified)
- [ ] Tencent Cloud Hunyuan: BLOCKED on user signup (HUNYUAN_API_KEY not set). LLM pass falls back to
      Slither-only and says so honestly until the key exists.
- [x] README + MIT LICENSE done. [ ] 2-min demo video (do near deadline)
- [ ] Explorer source-verification: explorer.sepolia.mantle.xyz API returning 503 (their infra); retry. Contract works regardless.

### Honest gaps
- LLM (Tencent) pass is written but UNTESTED live — no API key yet. Current verdicts are Slither-only.
- Registry source not yet verified on the explorer (cosmetic; contract works).
- ERC-8004 giveFeedback verified live (agent 186). Note: registry blocks self-feedback, so the auditor key must differ from the audited agent's owner (correct real-world case).
