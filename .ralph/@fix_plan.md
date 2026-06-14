# Fix Plan — Mantle Agent Auditor

Phase 1 Gate: paste a Mantle contract address → AI returns ≥1 true vulnerability with line number
AND writes a security attestation tx on Mantle testnet. Build these in order.

## Tasks

- [ ] Task 1: Confirm Mantle Sepolia testnet RPC + ERC-8004 contract addresses (or decide self-deployed registry fallback)
  - Acceptance: a documented RPC URL in README + a yes/no on whether event ERC-8004 contracts are live on testnet
  - Files: README.md, ai/memory.md

- [ ] Task 2: Write + deploy the AttestationRegistry contract on Mantle Sepolia
  - Acceptance: contract deployed, address recorded, verified on Mantle Explorer; stores (contractAddr, verdict, reportHash, auditor)
  - Files: contracts/AttestationRegistry.sol, deploy script (uses vm.envUint, never hardcode keys)

- [ ] Task 3: Build the AI audit pass over a Solidity source string
  - Acceptance: given one known-vulnerable contract, returns the real bug with a correct line number
  - Files: agent/audit.py or agent/audit.ts (uses os.getenv / process.env for keys; inference via Tencent Cloud endpoint)

- [ ] Task 4: Wire audit verdict → on-chain attestation write
  - Acceptance: running the agent on a contract address produces a verdict tx visible on Mantle Explorer
  - Files: agent/attest.ts (viem/ethers), reads key from env only

- [ ] Task 5: Minimal public frontend — input address, show verdict + attestation tx link
  - Acceptance: deployed to a public URL (GitHub Pages), not localhost; runs the full core action
  - Files: web/

- [ ] Task 6: README (setup, architecture, deployed address) + MIT LICENSE
  - Acceptance: a fresh reader can reproduce the demo; license file present
  - Files: README.md, LICENSE

## Completed
(builder fills this in)
