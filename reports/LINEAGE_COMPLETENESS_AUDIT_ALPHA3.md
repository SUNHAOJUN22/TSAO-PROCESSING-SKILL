# TSAO lineage-completeness audit — alpha.3

## Baselines compared

1. `SJTU-POE-PROCESSING-SKILL 1.0.0` — the original evidence-to-kinetics-to-property-to-reactor-to-steady/dynamic-process-to-scale-up-to-acceptance method distilled from the SJTU POE corpus.
2. `SJTU-UNIVERSAL-POLYMER-TECHNOLOGY-DEVELOPMENT-SKILL 2.0.0` — the original one-call polymer R&D operating system with project modes, recursive file inventory, falsifiable research graph, fourteen workstreams, maturity M0–M9 and technology-package delivery.
3. `EPDM Universal Polymer Technology Development Skill 9.0.0` — the qualification-oriented EPDM specialist with active-site, terpolymer architecture, recovery, compound/customer and lifecycle-assurance methods.
4. `TSAO 0.1.0-alpha.2` — the hardened software baseline with 418/418 complete-distribution tests and cleanroom qualification.

## Findings before alpha.3

### Correctly achieved

- The master G0–G18 lifecycle is broader and more explicit than the original polymer-only lifecycle.
- Evidence freshness, Gate transactions, model risk, assurance graph, project audit, deterministic release and cleanroom behaviour are materially stronger than the earliest skills.
- The complete distribution preserves the EPDM v9, SJTU-POE and universal-polymer source trees and their historical identities.
- Software qualification is correctly separated from technical approval.

### Incomplete or regressed

1. Root `SKILL.md` still declared alpha.1 although the package, manifest and release were alpha.2.
2. The root Skill had become concise enough to lose important original execution behaviour: one-call mandatory actions, parallel workstreams, role model, claim states and M0–M9 maturity.
3. The router recognized biochemical, electrochemical, solids, fine-chemical and petrochemical terms, but there was no corresponding non-polymer specialist Skill; generic projects could initialize with no active subskill.
4. GitHub source-core subskill files are reviewable contracts, not the complete historical EPDM/POE/universal-polymer source trees. Full source parity exists only in the qualified distribution.
5. Automated-test depth is asymmetric: EPDM has extensive inherited tests, while POE and universal-polymer primarily have structural and smoke coverage.
6. The Draft PR and some public documentation still reported alpha.1/14-test/362-test historical values after alpha.2 qualification.

## Alpha.3 corrections

- restored the full one-call execution contract, fourteen workstreams, role model, claim-state separation and M0–M9 maturity to the root Skill;
- added `skills/process-general/` for non-polymer routes and integrated it into project initialization and Schema;
- made every project activate at least one supported subskill;
- unified alpha.3 version metadata including root Skill and CI report;
- added lineage and specialist-content regression tests;
- documented the source-core versus complete-distribution boundary explicitly.

## Remaining programme work

### P0 — public full-source parity

The final open-source objective is not fully met until the complete EPDM v9, SJTU-POE and universal-polymer source trees are ingested as ordinary reviewable Git files or release-linked source packages with per-file provenance. The current complete distribution is qualified, but it is not equivalent to browsing every specialist source file on the Draft PR branch.

### P1 — POE and universal-polymer executable depth

Increase POE and universal-polymer tests from structural/smoke coverage to known-solution, conservation, identifiability, scale-up, recycle/devolatilization and negative-release suites comparable to EPDM.

### P1 — non-polymer domain packs

The new process-general Skill supplies a coherent method. Future releases should add executable domain packs and fixtures for bioprocess, electrochemical, solids/crystallization, fine-chemical batch and petrochemical/refining cases.

### P2 — installation and agent-host qualification

Add tested installers and registration checks for Codex, Claude Code and the Agent Skills standard on Windows and Linux/macOS.

## Verdict

Alpha.2 was a strong software-assurance release but did not fully preserve the earliest operational mission in the public source core. Alpha.3 closes the highest-impact semantic and routing gaps. The project is now a credible universal process-development source core, while full public specialist-source parity and balanced domain test depth remain explicit release blockers for a stable 1.0 claim.
