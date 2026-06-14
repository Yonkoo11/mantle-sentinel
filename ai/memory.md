# Mantle Sentinel — Memory

## Phase 1 Gate (MUST PASS BEFORE ANY OTHER WORK)
Core Action: Paste a real Mantle contract address → the AI auditor agent returns at least one true vulnerability with a line number AND writes a pass/fail security attestation transaction on Mantle testnet.
Success Test: One known-vulnerable Mantle testnet contract → agent flags the real bug with correct line number, and a verifiable attestation tx appears on Mantle Explorer (Sepolia testnet).
Min Tech: LLM audit pass over Solidity source + ethers/viem to write one attestation call on Mantle testnet + a contract that stores the verdict.
NOT Phase 1: ERC-8004 full reputation scoring, web UI polish, multi-contract batch, false-positive tuning, gas optimizer, paid tiers, mainnet.
Status: [x] PASSED 2026-06-14 (registry 0xbCE17E7..., target 0x469C464..., tx 0x3c5212...)

## Hackathon Context
- Event: Mantle Turing Test Hackathon 2026 — "AI Awakening" (Phase 2)
- DEADLINE: 2026-06-15 16:59 (submission closes)
- Track applied for: AI DevTools (Exclusively Supported by Tencent Cloud) — "Mantle-specific audit assistants"
- Also eligible: Grand Champion (substantive Mantle use) + 20 Project Deployment Award
- Prize pool: $100,000
- Submission: https://dorahacks.io/hackathon/mantleturingtesthackathon2026/detail
- Chain: Mantle (EVM L2). Testnet = Mantle Sepolia.
- Marquee primitive: ERC-8004 agent identity NFT (attach security verdict to agent identity)

## Judging Criteria (Grand Champion)
- Technical Depth 30% (AI × on-chain integration, architecture, code quality)
- Innovation 25% (new AI × Web3 paradigm)
- Mantle Ecosystem Contribution 25% (substantive Mantle use)
- Product Completeness 20% (runnable demo, UX, scalability)

## Chosen Idea
Mantle Sentinel: an AI agent that audits any Mantle contract address, finds vulnerabilities,
and writes a signed pass/fail security attestation on-chain bound to the contract's ERC-8004 agent
identity. Gives autonomous trading/RWA agents a portable, verifiable on-chain safety reputation that
users can check before delegating funds. Sits at the trust layer the whole "Human vs AI" benchmark needs.

## Competitive Landscape
- Sec3 / OZ Defender: reactive, enterprise-only, no agent-identity-linked attestations
- No Mantle-native auditor exists; no auditor writes ERC-8004-bound verdicts

## Fatal Flaws (track these)
- AI audit false positives/negatives → attestation only as good as the audit. Mitigation: ship a small
  rules+LLM hybrid, disclose confidence, demo against a known-bug contract first.
- Needs real Mantle contracts to demo → the event itself supplies hundreds of agent contracts (corpus).
- ERC-8004 contract addresses on Mantle testnet must be confirmed before binding to them. Fallback:
  deploy our own minimal attestation registry if ERC-8004 deployment isn't live.

## Required Deliverables Checklist
- [ ] Open-source GitHub repo + README (setup, architecture, deployed contract address)
- [ ] Contract deployed on Mantle (testnet or mainnet) + verified on Mantle Explorer
- [ ] At least one AI-powered function callable on-chain (audit verdict written on-chain)
- [ ] Public (non-localhost) frontend demo
- [ ] Demo video ≥ 2 min walking the core use case
- [ ] Deployment address in DoraHacks submission
- [ ] LICENSE (OSI-approved — MIT for A4 public-goods archetype)
- [ ] Project pitch

## Archetype / Precedent
- Archetype A4 (open-source dev/security tooling, Public Goods winner pattern)
- Precedent: Seer (Cypherpunk Infra 1st), IDL Space (Breakout PGA), DevXStark (ETHIndia AI dev tooling), Samui Wallet (PGA)
