# Design Progress: mantle-sentinel (Sentinel)

started: 2026-06-15
style_config: ~/.claude/style.config.md
color_mode: dark-only — security/dev tool, dark IS the identity; matches observed dark-first pattern
flags: --skip-state (static landing page, no app state); polish-driven (identity already locked)

phase_0: completed
phase_1: skipped - static page
phase_1.5: completed
comparables: EAS (attest.org), Linear, Etherscan/Blockscout, Vercel
research_output: ai/design-research.md

phase_2: completed - REAL research (Socket.dev, CertiK Skynet, Snyk, ToB/OZ, Linear, Vercel/Resend, Stripe) drove a verdict-as-credential direction
phase_3: completed - selected 'verdict credential + forensic code excerpt' direction
phase_4: completed - production polish (layered bg, mint glow, verdict-as-credential card, motion, liveness)
audit_result: pass
issues_fixed: 1 (11px label -> 12px)
phase_5: completed
qa_result: APPROVED — gates pass (no pure black/white, no ease-in, 0 sub-12px, liveness pulse, active-press + focus rings, cubic-bezier). VISUALLY VERIFIED via headless Chrome (desktop + mobile screenshots); read-path live. Redesigned off real comparable research after first pass was AI-slop.
