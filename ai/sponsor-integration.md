# Sponsor Integration Depth — Sentinel

## SPONSOR: Mantle (chain + ERC-8004 + AI x RWA infra)
Track prize: Grand Champion (25% Mantle Ecosystem Contribution) + AI DevTools nomination
Current depth: 0/5 → Target: 5/5 (load-bearing)

Surface area used:
- On-chain: deploy attestation registry contract on Mantle Sepolia testnet; write audit verdicts on-chain
- Identity: bind each verdict to the audited contract's ERC-8004 agent identity NFT
- Explorer: verify the contract on Mantle Explorer (Deployment Award requirement)

Committed for V1 (must ship):
- Attestation registry deployed + verified on Mantle Explorer — acceptance: explorer link returns "Verified"
- AI audit verdict written on-chain via a callable function — acceptance: a verdict tx appears on Mantle Explorer
ERC-8004 binding:
- V1 if event's ERC-8004 contracts are live on Mantle testnet (confirm addresses first)
- V2 fallback: minimal self-deployed identity registry if not live — disclosed in README

## SPONSOR: Tencent Cloud (AI DevTools track host)
Track prize: AI DevTools first prize
Current depth: 0/5 → Target: 3/5

Surface area used:
- Off-chain: run the LLM audit inference (Tencent Cloud inference / hosted model endpoint) — depth 3
Committed for V1:
- Audit inference runs on a Tencent Cloud endpoint — acceptance: README documents the endpoint, demo calls it
- If Tencent Cloud inference onboarding blocks V1: document the integration point and route inference
  through it as the named V2 win; do NOT name-drop without the call landing.

## Anti-patterns avoided
- ERC-8004 must be a load-bearing verdict binding, NOT a README mention.
- Tencent Cloud must actually host the inference call, not just be listed.
