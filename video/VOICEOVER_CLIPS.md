# Sentinel — Demo Video Script (v2: real views only, no synthetic card, no music)

Lessons applied (from the Verigate build): every clip maps to a DISTINCT real product view, the close is
the real landing hero (not a generated card), captions are verbatim to the audio, no em-dashes, no music.
Lead with the strongest element (the live audit). Brian voice, ~140 wpm.

| Clip | View shown (real screenshot) | Line |
|------|------------------------------|------|
| money | Live audit result on the site (grade F + findings) | Paste a contract into Sentinel. Two engines grade it in seconds, Slither and an AI model. Here it flagged a critical bug. Funds the owner could drain. |
| onchain | Terminal: the attestation write + a cast read-back | The verdict is written to Mantle. The report is hashed, so the grade is tamper-proof and anyone can verify it. |
| registry | The on-chain verdict registry table | Every contract it grades lives in one on-chain registry. Pass or fail, A through F, read live from the chain. |
| composable | The registry developer snippet (isAttestedSafe) | Each grade binds to the agent's ERC-8004 identity. One call, isAttestedSafe, lets any contract refuse an agent that never passed. |
| close | The real landing hero | Sentinel. Audit any agent, and prove it on-chain. |

Frame note: the only non-screenshot frame is the terminal (clip 2). The on-chain write can't be shown as a
live screenshot because the Mantle explorer is behind a Cloudflare bot-wall, so a clean terminal showing the
real tx hashes + a real cast read-back stands in for it. Everything else is a live screenshot of the product.
