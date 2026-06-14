## SECURITY — KEYS NEVER IN REPO OR CONTEXT (BLOCKING)

The deployer + operator + RPC keys live ONLY in `~/.zshenv`. Hard rules:

- **NEVER read `~/.zshenv`, `~/.zshrc`, `~/.zprofile`, `~/.bashrc`, `~/.bash_profile`, `~/.netrc`, `~/.npmrc`, `~/.git-credentials`, SSH keys, `*.key`, `*.pem`, or any `keystore/*` file.** Not `Read`, not `cat`, not `head`, not `grep -v`. Project + global hooks block these.
- **NEVER print, echo, or log key values.** `echo $KEY`, `print(os.getenv("KEY"))`, `vm.toString(pk)`, `console.log(process.env.KEY)` are banned.
- **NEVER commit `.env*`, `*.key`, `*.pem`, `keystore/`, `secrets/`** — covered by `.gitignore`. Verify `git diff --cached` before every save point.
- **NEVER use `git add -A` for the first save point in a new project.** Add by explicit file name.
- **Foundry deploys use `vm.envUint("DEPLOYER_PRIVATE_KEY")`** — reads process env at runtime. Never hardcode. Never `--private-key 0x...` on the CLI either.
- **Python agents use `os.getenv("OPERATOR_PRIVATE_KEY")`** — same pattern. Never `dotenv.load_dotenv("~/.zshenv")`. Never shell out to echo env vars.
- **Check var presence without seeing value:** `[ -n "$VARNAME" ] && echo "set"` or `echo "${#VARNAME}"` (length only).
- **If a key ever surfaces in chat or output, STOP. Tell the user to rotate. Do not paginate the value back into context.**

Full playbook: `SECURITY.md`. Read it before any deploy or signing work.

---

## Vibecoder Mode
- Never say: branch, commit, merge, PR, push, pull, HEAD, diff, npm, deploy, lint, env var.
  Instead say: version, save point, combine changes, publish, update, latest, changes, install, check code.
- Never show raw terminal output or error messages. Summarize in one sentence; say what you're fixing.
- Describe what changed by what the user SEES in the app, not what files changed.
- Auto-save after every completed task (git add specific files + commit). Never ask "should I save?"
- If tests fail, fix them silently. Keep explanations to 1-3 sentences.
- After each task: update `ai/progress.md` with a "What Changed (Plain English)" section.

---

## Project: Mantle Agent Auditor

**Pitch:** AI auditor for on-chain agents. Paste a Mantle contract address → AI finds vulnerabilities →
writes a signed pass/fail security attestation on-chain, bound to the contract's ERC-8004 agent identity.

### Phase 1 Gate (MUST PASS BEFORE ANYTHING ELSE)
Core Action: Paste a real Mantle contract address → auditor returns ≥1 true vulnerability with a line
number AND writes a security attestation transaction on Mantle testnet.
Success Test: One known-vulnerable Mantle testnet contract → real bug flagged with correct line number +
verifiable attestation tx on Mantle Explorer.
Status: NOT STARTED. No UI/CSS until this passes.

### Build Order (no skipping)
1. Core action end-to-end (audit → on-chain attestation written + readable)
2. Data flows (real contract source in, real verdict on-chain)
3. Product complete (public frontend, demo video, README, LICENSE)
4. Visual polish LAST (`/design mantle-agent-auditor`)

### Hackathon Context
- Mantle Turing Test Hackathon 2026 — AI DevTools track (Tencent Cloud) + Grand Champion + 20 Deployment Award
- Deadline: 2026-06-15 16:59. Chain: Mantle (testnet = Mantle Sepolia).
- Must ship: open-source repo + verified Mantle contract + on-chain AI function + public demo + ≥2min video.

### Sponsor Depth Targets
- Mantle 5/5 (load-bearing: on-chain attestation registry + ERC-8004 verdict binding). See `ai/sponsor-integration.md`.
- Tencent Cloud 3/5 (LLM audit inference hosted on Tencent Cloud).

### Required Tech
- EVM/Solidity (attestation registry), an LLM audit pass over Solidity source, viem/ethers for the on-chain write.
- License: MIT (A4 open-source public-goods archetype).

Research base: `~/Projects/IDEAS-SUMMARY.md` (#101, #6, #2). Memory: `ai/memory.md`.
