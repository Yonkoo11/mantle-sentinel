# DoraHacks BUIDL form — copy/paste source (Sentinel)

Copy each field straight from here. Written in plain prose, no AI tells.
NOTE: only the **Profile** tab was confirmed from a screenshot. Details / Team / Contact / Submission
are filled from the standard DoraHacks form — confirm the field labels against your tabs and tell me
if any differ.

================================================================
## TAB 1 — PROFILE  (confirmed from screenshot)
================================================================

### Vision  (Describe the problem which this project solves)  [MAX 256 CHARS — this is 249]
Autonomous agents move real money on Mantle, each with an on-chain identity, but no one checks if their contracts are safe. Audits are PDFs; scores live off-chain. Sentinel writes a pass/fail verdict on-chain, bound to the agent's ERC-8004 identity.

(Longer version for any field WITHOUT a limit, e.g. the Details description:)
Autonomous agents now move real money on Mantle, and every agent gets an on-chain identity. Nobody checks whether the contracts behind them are safe. Audit firms hand back PDFs. Security scores sit on websites a smart contract can't read. There is no way for one contract to ask, on-chain, whether another agent has been audited and passed. Sentinel answers that. It audits any contract, writes a pass or fail verdict to Mantle, and ties it to the agent's ERC-8004 identity, so anyone can check it and any contract can act on it.

### Category
Crypto / Web3
(If you'd rather lead with the AI angle, AI / Robotics also fits. Crypto / Web3 is the stronger primary
because the core of the product is the on-chain verdict registry.)

### Is this BUIDL an AI Agent?
Yes  (toggle ON)
Reason: Sentinel registers its own ERC-8004 agent identity and runs an autonomous audit pipeline that
reads a contract, reasons about it with an LLM, and writes its verdict on-chain without a human in the loop.

### Links
GitHub:           https://github.com/Yonkoo11/mantle-sentinel
Project website:  https://yonkoo11.github.io/mantle-sentinel/

================================================================
## TAB 2 — DETAILS   (CONFIRMED: ONE markdown field. Paste the whole block below.)
================================================================
Notes: this is a single rich-text box that takes Markdown and embeds YouTube. Paste your YouTube link
on its own line and DoraHacks turns it into an embedded player. Everything (video, links, contract
addresses) goes in here, because there are no separate fields for them.

--- copy from here ---

**Sentinel is an AI auditor for on-chain agents.** Give it a contract, it finds the bugs, and it writes a pass or fail security verdict onto Mantle. The verdict is bound to the contract's ERC-8004 agent identity, so an agent's safety record lives on-chain and travels with it.

[paste your YouTube demo link here on its own line]

### How it works

**1. Read the code.** A hybrid engine runs Slither for static analysis and Google Gemini for the logic bugs static tools miss. The two passes are merged, so anything both engines flag is marked confirmed. On a sample vault it catches a reentrancy money-drain at the exact lines. On a tx.origin contract the AI pass adds a critical "owner can drain all funds" that the static tool only flagged as a warning.

**2. Anchor the report.** The full report is reduced to one keccak256 hash. Only the hash and an IPFS pointer go on-chain, so the verdict is cheap to store and can't be changed after the fact. Anyone can re-run the report and confirm the hash matches.

**3. Write the verdict.** A pass or fail attestation is written to the AuditAttestationRegistry on Mantle Sepolia. Any other contract can call `isAttestedSafe(address)` and gate its own logic on the result.

**4. Bind to identity.** If the audited contract is a registered ERC-8004 agent, the verdict is also written to its on-chain reputation through the ReputationRegistry. The safety record follows the agent's identity, not a link that can rot.

### Live right now
- Registry deployed and running on Mantle Sepolia: `0xbCE17E724c0Cd038622a9C4299F86Caf411C1Fae`
- A web app that reads verdicts straight from the chain, plus a hosted backend that audits any pasted contract on demand
- A real verdict bound to ERC-8004 agent #186, readable back on-chain with `getSummary`
- Three contracts already graded in the public registry: one passing at grade A, two failing at grade D

### Why it needs Mantle
Sentinel is the trust layer for this event's own thesis. It reads the ERC-8004 identities Mantle issues to agents, writes verdicts to a Mantle contract, and binds those verdicts to agent reputation. Take Mantle's ERC-8004 layer away and a portable, on-chain agent safety record has nowhere to live.

### Built with
Mantle Sepolia, Solidity, Foundry (10 passing tests), Slither, Google Gemini, Python, FastAPI, ethers.js, the ERC-8004 Identity and Reputation registries, Hugging Face Spaces, and GitHub Pages.

### Links
- Live demo: https://yonkoo11.github.io/mantle-sentinel/
- Verdict registry (live): https://yonkoo11.github.io/mantle-sentinel/registry.html
- Audit API: https://yonko11-sentinel-audit-api.hf.space
- Source (MIT): https://github.com/Yonkoo11/mantle-sentinel
- Registry on Mantle Sepolia: `0xbCE17E724c0Cd038622a9C4299F86Caf411C1Fae`

--- copy to here ---

================================================================
## TAB 3 — TEAM   (already complete on your form — checkmarked)
================================================================
Nothing to paste unless you want to change it. If it asks for a profile, use GitHub: Yonkoo11.

================================================================
## TAB 4 — CONTACT   (already complete on your form — checkmarked)
================================================================
Nothing to paste unless you want to change it.

================================================================
## TAB 5 — SUBMISSION   (CONFIRMED: Track dropdown + agree to terms)
================================================================
Track (required, single select): choose **AI DevTools**
Then tick: "I agree to the Terms of Use Agreement and Participant Agreement"
Then click: Submit for Review

(Grand Champion is judged across all tracks for any nominated project, so selecting AI DevTools is all
you need here. Make sure your YouTube link is already pasted into the Details field before you submit.)
