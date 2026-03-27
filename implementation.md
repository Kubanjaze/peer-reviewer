# Phase 73 — Claude as Peer Reviewer for SAR Hypotheses

**Version:** 1.1 | **Tier:** Micro | **Date:** 2026-03-28

## Goal
Use Claude as a structured peer reviewer for SAR hypotheses. Given a hypothesis about structure-activity relationships, Claude evaluates it against compound data and returns a structured review with verdict, supporting evidence, counterevidence, and confidence score.

CLI: `python main.py --input data/compounds.csv --n 2`

Outputs: peer_reviews.json, peer_review_report.txt

## Logic
1. Load compound library with pIC50 values
2. Generate 2 SAR hypotheses from data patterns
3. Send each hypothesis + supporting compound data to Claude with a peer review system prompt
4. Parse structured review: verdict (support/refute/inconclusive), evidence_for, evidence_against, confidence (0-1), suggestion
5. Save structured reviews

## Key Concepts
- Structured peer review output format (JSON)
- System prompt engineering for critical evaluation role
- Claude as domain expert reviewer (not generator)
- Evidence-based reasoning with compound data
- Anti-sycophancy prompting ("Be critical. Look for counterevidence.")

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
| H1 (EWG benzimidazole) | Verdict: support, Confidence: 0.82 |
| H2 (Indole uniformly potent) | Verdict: refute, Confidence: 0.85 |
| Total tokens | in=757 out=822 |
| Est. cost | $0.0039 |

Key findings:
- Claude correctly supported the EWG hypothesis but noted NO2 underperformance as counterevidence
- Claude refuted the "uniform potency" hypothesis, noting 1.40 pIC50 unit range across R-groups
- Anti-sycophancy prompting worked: Claude provided genuine counterevidence and refuted H2
- Both reviews included actionable suggestions for hypothesis refinement

## Risks
- Claude may always agree (sycophancy) — mitigated with explicit "find counterevidence" instruction; H2 refuted confirms mitigation works
- JSON parsing failures — regex fallback included
