# Phase 73 — Claude as Peer Reviewer for SAR Hypotheses

**Version:** 1.1 | **Tier:** Micro | **Date:** 2026-03-27

## Goal
Use Claude as a structured peer reviewer for SAR hypotheses. Given a hypothesis about structure-activity relationships, Claude evaluates it against compound data and returns a structured review with verdict, supporting evidence, counterevidence, and confidence score.

CLI: `python main.py --input data/compounds.csv --n 2`

Outputs: peer_reviews.json, peer_review_report.txt

## Logic
1. Load compound library with pIC50 values
2. Generate 2 SAR hypotheses from data patterns (e.g., "EWG substituents increase potency in benzimidazole series")
3. Send each hypothesis + supporting compound data to Claude with a peer review system prompt
4. Parse structured review: verdict (support/refute/inconclusive), evidence_for, evidence_against, confidence (0-1), suggestion
5. Save structured reviews and summary report

## Key Concepts
- Structured peer review output format (JSON with verdict, evidence_for, evidence_against, confidence, suggestion)
- System prompt engineering for critical evaluation role — must explicitly instruct Claude to find counterevidence
- Claude as domain expert reviewer (evaluating, not generating)
- Evidence-based reasoning: Claude must cite specific compound names and pIC50 values

## Verification Checklist
- [x] 2 hypotheses reviewed
- [x] Each review has verdict, evidence_for, evidence_against, confidence, suggestion
- [x] JSON output parseable
- [x] --help works
- [x] Cost < $0.01

## Results
| Metric | Value |
|--------|-------|
| Hypotheses reviewed | 2 |
| Hypothesis 1 verdict | support (confidence=0.82) — EWG on bzim increases potency |
| Hypothesis 2 verdict | refute (confidence=0.85) — ind series NOT uniformly high, R-group matters |
| Input tokens | 757 |
| Output tokens | 822 |
| Est. cost | $0.0039 |

## Risks (resolved)
- Sycophancy risk: mitigated by explicit "find counterevidence" instruction — Claude successfully refuted hypothesis 2
- JSON parsing: no issues encountered

Key finding: Claude successfully refuted hypothesis 2 (indole uniformly high potency) by noting that R-group electronic properties drive meaningful modulation within the series. This demonstrates Claude can critically evaluate rather than just agree with presented hypotheses.
