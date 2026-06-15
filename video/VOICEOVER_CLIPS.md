# Sentinel — Demo Video Script

Target: ~70s · Framework: lead-with-product (show it working in 5s), then walk the system, then the hard part, then CTA.
Money shot: the LIVE audit — paste a contract → grade F + an AI-found CRITICAL appears. Built first; everything else frames it.
Tone: technical, concrete, show-don't-sell. ElevenLabs Brian, stability 0.82, style 0.03. ~140 wpm.

Music: dark minimal electronic (dev-tool / web3), ~100-105 BPM, no vocals → video/music/bg.mp3

---

## Clip 1 — HOOK (frame: live audit result, grade F credential) [~5s]
Paste any smart contract into Sentinel, and seconds later you get this. A security grade.

## Clip 2 — THE AUDIT (frame: findings list, Gemini CRITICAL visible) [~9s]
It runs two engines at once. Slither for static analysis, and an AI model for the logic bugs static tools miss. Here it caught a critical one. Funds the owner could drain.

## Clip 3 — ON-CHAIN (frame: Mantlescan attestation tx) [~8s]
The verdict doesn't sit in a database. It's written to Mantle. The full report is hashed, so the grade is tamper-proof and anyone can verify it.

## Clip 4 — REGISTRY (frame: registry table, A/PASS + D/FAIL spread) [~8s]
Every contract it has graded lives in one on-chain registry. Pass or fail, A through F, read straight from the chain.

## Clip 5 — THE HARD PART (frame: registry dev snippet / ERC-8004) [~9s]
Each verdict binds to the agent's ERC-8004 identity. So one call — isAttestedSafe — lets your contract refuse to trust an agent that never passed.

## Clip 6 — CTA (frame: hero, Sentinel wordmark + URL) [~5s]
Sentinel. The safety layer for on-chain agents. Try it at the link below.

---

## Frame plan (one distinct surface per clip — no reuse)
- 01: home, live-audited result credential (grade F via the paste flow) — the money shot still
- 02: same audit scrolled to the findings list showing the CRITICAL row
- 03: Mantlescan tx page for an attestation (sepolia.mantlescan.xyz/tx/…)
- 04: registry.html table (3 verdicts: A PASS, two D FAIL)
- 05: registry.html developers snippet (isAttestedSafe interface)
- 06: home hero (wordmark + "Audit any agent. Prove it on-chain." + URL overlay)

## Adversarial gate (passed): no failure cases, no caveats, no "honest assessment" — those live in the README.
## Word count ~ 115 words → ~50s audio + padding ≈ 65-72s total.
