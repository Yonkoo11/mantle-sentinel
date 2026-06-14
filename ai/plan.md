# Build Plan — Mantle Agent Auditor

**Pitch:** AI auditor for on-chain agents. Paste a Mantle contract → AI + static analysis find
vulnerabilities → a pass/fail security verdict is written on-chain AND bound to the contract's
ERC-8004 agent identity, giving every autonomous agent a portable, verifiable safety reputation.

Track: AI DevTools (Tencent Cloud) · also Grand Champion + 20 Deployment Award.

---

## Verified facts this plan is built on (researched 2026-06-14)

**ERC-8004 IS live on Mantle Sepolia (chain 5003)** — confirmed by on-chain bytecode check:
- IdentityRegistry (ERC-721, `agentId` = tokenId): `0x8004A818BFB912233c491871b3d84c89A494BD9e`
- ReputationRegistry (`giveFeedback(...)`): `0x8004B663056A597Dffe9eCcC1965A193B7388713` *(verify with eth_getCode as step 1)*
- NO ValidationRegistry on Mantle → we deploy our own attestation registry.
- ERC-8004 is DRAFT; pin to the deployed ABI, not the evolving spec.

**Mantle Sepolia:** RPC `https://rpc.sepolia.mantle.xyz`, explorer `https://sepolia.mantlescan.xyz`
(+ Blockscout `https://explorer.sepolia.mantle.xyz`), faucet `https://faucet.sepolia.mantle.xyz`,
gas token MNT, EVM = Cancun (EIP-1153 available), set `evmVersion = cancun`. Verify contracts free
via Blockscout: `forge verify-contract --verifier blockscout --verifier-url https://explorer.sepolia.mantle.xyz/api/`.

**Tencent Cloud Hunyuan (inference host):** OpenAI-compatible `https://api.hunyuan.cloud.tencent.com/v1/chat/completions`
(`Authorization: Bearer <key>`, model `hunyuan-turbos-latest`, 256K context). A native TC3-HMAC-SHA256
signed call is the "load-bearing" proof. Friction: card-binding + possible KYC delay → register TODAY.

**Differentiator (verified vs prior art):** CertiK Skynet = centralized/off-chain; OZ = PDF; EAS = generic
no audit schema; AI auditors (ChainGPT etc.) stay off-chain. Nobody writes a composable, hash-anchored
pass/fail keyed to a contract address AND its ERC-8004 identity. That gap is the wedge.

---

## Deep-integration design (this is the priority)

Two sponsor surfaces, both load-bearing — remove either and the product breaks:

### Mantle + ERC-8004 → depth 5/5
1. **Read** the target's ERC-8004 identity: query IdentityRegistry for the target agent's `agentId`.
2. **Self-register** our auditor as its own ERC-8004 agent (one-time) → the auditor has on-chain identity.
3. **Write our own `AuditAttestationRegistry`** verdict on Mantle Sepolia → composable `isAttestedSafe(address)`
   any contract/frontend can query. (Deployed + verified on Mantlescan = Deployment Award.)
4. **Bind to identity:** if the target is a registered ERC-8004 agent, call
   `ReputationRegistry.giveFeedback(agentId, score, …, tag1="security-audit", feedbackURI=ipfsCID, feedbackHash=reportHash)`
   so the security verdict travels with the agent's identity NFT. **This is the killer demo** — audit a
   competing hackathon agent and its on-chain reputation now carries your verdict. Multiple ERC-8004
   primitives load-bearing (read identity + self-register + write reputation), not a name-drop.

### Tencent Cloud → depth 3–4/5
- Audit LLM inference runs on Hunyuan (OpenAI-compatible endpoint) — committed V1.
- One native TC3-HMAC-SHA256 signed `ChatCompletions` call to prove genuine Tencent auth — committed V1.
- Stretch: host the backend on Tencent Cloud Lighthouse so compute + inference both run on Tencent (depth 5).

### Honesty / accuracy layer (the real moat — leans on your existing pipeline)
Most teams will do one naive LLM call. This runs a **hybrid**: Slither static analysis (via your slither
MCP / CLI) + Hunyuan LLM reasoning, merged and de-duplicated. Verdict report is canonicalized (RFC 8785),
`keccak256`-hashed, pinned to IPFS; only the hash + CID go on-chain → tamper-evident + falsifiable.
Confidence disclosed; demo runs against a KNOWN-vulnerable contract first so the verdict is checkable.

---

## Architecture

```
web/ (GitHub Pages, public)  ──>  backend API (Render free tier or Tencent Lighthouse)
  input: Mantle address              1. fetch verified source (Mantlescan API) or accept pasted source
  output: verdict + vuln list        2. Slither static pass  +  Hunyuan LLM pass  -> merge
          attestation tx link        3. canonical report -> keccak256 hash -> pin to IPFS (CID)
          ERC-8004 reputation link   4. on-chain: AuditAttestationRegistry.attest(target, pass, hash, cid)
                                      5. if target is ERC-8004 agent: ReputationRegistry.giveFeedback(...)
contracts/
  AuditAttestationRegistry.sol  (append-only, msg.sender=auditor, gated to agent key, isAttestedSafe view)
agent/
  audit pipeline (Python: Slither + Hunyuan), web3.py for on-chain writes (keys via os.getenv only)
```

Tech: Solidity + Foundry (evmVersion cancun); Python backend (reuses Slither + your audit methodology);
viem/ethers in the static frontend for wallet + read calls. License MIT.

---

## Build order (Phase 1 Gate first — no UI until it passes)

**Task 0 — Confirm unknowns (do first, ~30 min):**
- eth_getCode on ReputationRegistry `0x8004B663...` to confirm it's live; pull its deployed ABI.
- Register a Tencent Cloud account + get a Hunyuan API key (start now — KYC may lag).
- Get test MNT from the faucet into a fresh operator key (env only).

**Task 1 — AuditAttestationRegistry.sol:** deploy to Mantle Sepolia, verify on Mantlescan.
  Acceptance: explorer shows "Verified"; `attest()` writes; `isAttestedSafe()` reads back.

**Task 2 — Audit pipeline:** given one known-vulnerable contract, Slither+Hunyuan return the real bug
  with correct line number. Acceptance: known bug flagged, line number correct.

**Task 3 — Wire verdict → on-chain:** pipeline output → canonical report → hash → IPFS → `attest()` tx.
  **Acceptance = PHASE 1 GATE:** paste a real Mantle address → ≥1 true vuln w/ line number + a verdict
  tx visible on Mantlescan.

**Task 4 — ERC-8004 binding:** if target has an `agentId`, also write `ReputationRegistry.giveFeedback(...)`.
  Acceptance: a competing agent's reputation shows the security verdict on-chain.

**Task 5 — Public frontend (GitHub Pages):** input address → verdict + vuln list + tx link + reputation
  link. Acceptance: works from a public URL, not localhost.

**Task 6 — Tencent native auth call:** one TC3-HMAC-SHA256 signed Hunyuan call. Acceptance: signed call
  returns 200 with a real verdict.

**Task 7 — Ship artifacts:** README (setup, architecture, deployed address), MIT LICENSE, ≥2min demo video.

Then Phase 4 polish: `/design mantle-agent-auditor`, `/demo-video`, `/submit`.

---

## Honest risks / contingencies
- **ReputationRegistry ABI drift** (UUPS upgradeable, spec is DRAFT) → verify deployed ABI before coding Task 4;
  if `giveFeedback` differs, our own AuditAttestationRegistry still satisfies the Phase 1 Gate + Deployment Award.
- **Tencent Cloud signup blocked by region KYC** → register today; fallback keeps the audit working via the
  OpenAI-compatible endpoint, and we honestly document Tencent depth as partial rather than name-drop.
- **AI false positives/negatives** → hybrid + Slither ground truth, demo against known bugs, disclose confidence.
- **Backend needs a public host** (GitHub Pages is static-only) → Render free tier default; Tencent Lighthouse
  is the depth-maximizing stretch.
- **RWA tokens (USDY/fBTC) are mainnet-only** → not needed for the auditor; ignore for testnet build.
```
