# AI auditor for on-chain agents

Paste a Mantle contract. A hybrid engine (Slither static analysis + Tencent Hunyuan reasoning) finds
the vulnerabilities, decides pass/fail, and writes the verdict **on-chain** — bound to the contract's
**ERC-8004 agent identity**, so an autonomous agent's safety reputation travels with it.

Built for the **Mantle Turing Test Hackathon 2026** — AI DevTools track. Live on Mantle Sepolia.

---

## Why this exists

The hackathon puts autonomous agents on-chain with real money and gives each one an ERC-8004 identity.
Nobody audits those agents or the contracts they touch. CertiK's score is centralized and off-chain;
audit firms ship PDFs; AI auditors return a chat reply. None write a **composable, tamper-evident,
on-chain** verdict another contract can check with `isAttestedSafe(address)`. This does.

## What it does (verified live)

1. **Reads the code** — Slither finds real bugs with line numbers (e.g. a reentrancy money-drain at lines 13–18 of the sample). Tencent Hunyuan adds LLM reasoning on top.
2. **Anchors the report** — the full report is canonicalized and `keccak256`-hashed; only the hash + IPFS CID go on-chain, so the verdict is tamper-evident and falsifiable.
3. **Writes the verdict** — a pass/fail attestation lands in our `AuditAttestationRegistry` on Mantle.
4. **Binds to identity** — if the target is an ERC-8004 agent, the verdict is also written to its on-chain reputation via `ReputationRegistry.giveFeedback(...)`.

## Deployed on Mantle Sepolia (chain 5003)

| Contract | Address |
|---|---|
| AuditAttestationRegistry (ours) | [`0xbCE17E724c0Cd038622a9C4299F86Caf411C1Fae`](https://sepolia.mantlescan.xyz/address/0xbCE17E724c0Cd038622a9C4299F86Caf411C1Fae) |
| Sample audited target (VulnerableVault) | [`0x469C46486d44eE02BB5A8d4FE341e55d13f5dF25`](https://sepolia.mantlescan.xyz/address/0x469C46486d44eE02BB5A8d4FE341e55d13f5dF25) |
| ERC-8004 IdentityRegistry (reference) | `0x8004A818BFB912233c491871b3d84c89A494BD9e` |
| ERC-8004 ReputationRegistry (reference) | `0x8004B663056A597Dffe9eCcC1965A193B7388713` |

Demo agent #186's reputation carries a live `security-audit` verdict (read it with
`getSummary(186, [auditor], "security-audit", "high")` → count 1, value 20).

## Architecture

```
docs/ (static frontend, GitHub Pages)  — reads live verdicts from the registry via public RPC
contracts/ (Foundry)                   — AuditAttestationRegistry.sol + tests + deploy scripts
agent/ (Python)                        — the auditor:
  static_pass.py   Slither static analysis -> findings with line numbers
  llm_pass.py      Tencent Hunyuan (OpenAI-compatible + native TC3-HMAC-SHA256 signed)
  report.py        canonical report + keccak256 hash
  ipfs.py          optional Pinata pinning
  attest.py        on-chain writes: our registry + ERC-8004 reputation
  erc8004.py       register agent identities
  run.py           orchestrator CLI
```

## Run it

**Contracts**
```bash
cd contracts
forge test                       # 10 passing
forge script script/Deploy.s.sol:Deploy --rpc-url mantle_sepolia --broadcast
```

**Auditor** (needs Slither + solc: `pip install slither-analyzer`; `solc-select use 0.8.20`)
```bash
cd agent
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
# dry run (audit only, no gas):
.venv/bin/python run.py --file samples/VulnerableVault.sol --target 0x<addr>
# write the verdict on-chain (+ bind to ERC-8004 agent if --agent-id given):
.venv/bin/python run.py --file samples/VulnerableVault.sol --target 0x<addr> --agent-id 186 --attest
```

**Frontend**
```bash
cd docs && python3 -m http.server 8080   # then open http://localhost:8080
```

## Secrets

Keys are read from the environment at runtime (`DEPLOYER_PRIVATE_KEY`, `HUNYUAN_API_KEY`,
`TENCENT_SECRET_ID/KEY`, `PINATA_JWT`) — never hardcoded, never committed. See `SECURITY.md`.

## Sponsor integration

- **Mantle + ERC-8004** — reads identity, registers agents, writes our registry, and binds verdicts to
  agent reputation. Four primitives load-bearing.
- **Tencent Cloud Hunyuan** — runs the LLM audit pass (OpenAI-compatible endpoint + a natively
  TC3-HMAC-SHA256-signed call). Without a key, the engine falls back to Slither-only and says so.

## Honest status

- Slither pass + on-chain registry + ERC-8004 binding: **verified live on Mantle Sepolia.**
- Tencent Hunyuan pass: **coded, not yet run live** (pending API key) — current verdicts are Slither-only.
- This is a security tool; AI verdicts can have false positives/negatives. The report hash makes every
  verdict checkable, and Slither is the static ground-truth layer.

## License

MIT — see `LICENSE`.
