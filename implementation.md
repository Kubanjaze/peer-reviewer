# Phase 73 — Claude as Peer Reviewer for SAR Hypotheses

**Version:** 1.0 | **Tier:** Micro | **Date:** 2026-03-28

## Goal
Use Claude as a structured peer reviewer for SAR hypotheses. Given a hypothesis about structure-activity relationships, Claude evaluates it against compound data and returns a structured review with verdict, supporting evidence, counterevidence, and confidence score.

CLI: `python main.py --input data/compounds.csv --n 2`

Outputs: peer_reviews.json, peer_review_report.txt

## Logic
1. Load compound library with pIC50 values
2. Generate 2 SAR hypotheses from data patterns (e.g., "EWG substituents increase potency in benzimidazole series")
3. Send each hypothesis + supporting compound data to Claude with a peer review system prompt
4. Parse structured review: verdict (support/refute/inconclusive), evidence_for, evidence_against, confidence (0-1), suggestion
5. Save structured reviews

## Key Concepts
- Structured peer review output format (JSON)
- System prompt engineering for critical evaluation role
- Claude as domain expert reviewer (not generator)
- Evidence-based reasoning with compound data

## Verification Checklist
- [ ] 2 hypotheses reviewed
- [ ] Each review has verdict, evidence_for, evidence_against, confidence, suggestion
- [ ] JSON output parseable
- [ ] --help works
- [ ] Cost < $0.01

## Risks
- Claude may always agree (sycophancy) — mitigate with explicit "find counterevidence" instruction
- JSON parsing failures — use regex fallback
