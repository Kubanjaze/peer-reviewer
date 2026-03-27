import sys
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import argparse, os, json, re, warnings
warnings.filterwarnings("ignore")
import pandas as pd
from dotenv import load_dotenv
import anthropic

load_dotenv()
os.environ.setdefault("ANTHROPIC_API_KEY", os.getenv("ANTHROPIC_API_KEY", ""))

REVIEW_SYSTEM = """You are a critical peer reviewer for medicinal chemistry SAR hypotheses.
Given a hypothesis and supporting compound data, evaluate it rigorously.

You MUST respond with ONLY valid JSON in this exact format:
{
  "verdict": "support" | "refute" | "inconclusive",
  "confidence": 0.0-1.0,
  "evidence_for": ["point 1", "point 2"],
  "evidence_against": ["point 1", "point 2"],
  "suggestion": "one-sentence suggestion for strengthening the hypothesis"
}

Be critical. Look for counterevidence. Do not default to agreement."""


def generate_hypotheses(df: pd.DataFrame, n: int) -> list[dict]:
    """Generate SAR hypotheses from compound data patterns."""
    hypotheses = []

    # Hypothesis 1: EWG effect on benzimidazole series
    benz = df[df["compound_name"].str.startswith("benz")]
    if len(benz) >= 2:
        benz_sorted = benz.sort_values("pic50", ascending=False)
        top = benz_sorted.iloc[0]
        bot = benz_sorted.iloc[-1]
        hypotheses.append({
            "hypothesis": (
                f"Electron-withdrawing groups (e.g., CF3, CN) on the benzimidazole scaffold "
                f"increase CETP inhibitory potency compared to electron-donating groups (e.g., OMe, OH)."
            ),
            "compounds": benz.to_dict(orient="records"),
        })

    # Hypothesis 2: Indole series is uniformly potent
    ind = df[df["compound_name"].str.startswith("ind")]
    if len(ind) >= 2:
        mean_pic50 = ind["pic50"].mean()
        std_pic50 = ind["pic50"].std()
        hypotheses.append({
            "hypothesis": (
                f"The indole scaffold series shows uniformly high potency (mean pIC50={mean_pic50:.2f}, "
                f"std={std_pic50:.2f}), suggesting the indole core itself is the primary driver of "
                f"activity regardless of R-group substitution."
            ),
            "compounds": ind.to_dict(orient="records"),
        })

    # Hypothesis 3: Pyridine series is weakest
    pyr = df[df["compound_name"].str.startswith("pyr")]
    if len(pyr) >= 2:
        hypotheses.append({
            "hypothesis": (
                f"The pyridine scaffold is intrinsically less potent than other scaffolds "
                f"for CETP inhibition, indicating poor complementarity with the binding site."
            ),
            "compounds": pyr.to_dict(orient="records"),
        })

    return hypotheses[:n]


def main():
    parser = argparse.ArgumentParser(
        description="Phase 73 — Claude as peer reviewer for SAR hypotheses",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--input", required=True, help="Compounds CSV with pic50 column")
    parser.add_argument("--n", type=int, default=2, help="Number of hypotheses to review")
    parser.add_argument("--model", default="claude-haiku-4-5-20251001", help="Model ID")
    parser.add_argument("--output-dir", default="output", help="Output directory")
    args = parser.parse_args()
    os.makedirs(args.output_dir, exist_ok=True)

    df = pd.read_csv(args.input)
    hypotheses = generate_hypotheses(df, args.n)
    print(f"\nPhase 73 — Claude as Peer Reviewer for SAR Hypotheses")
    print(f"Model: {args.model} | Hypotheses: {len(hypotheses)}\n")

    client = anthropic.Anthropic()
    reviews = []
    total_input = 0
    total_output = 0

    for i, h in enumerate(hypotheses, 1):
        compounds_str = "\n".join(
            f"  {c['compound_name']}: pIC50={c['pic50']:.2f}" for c in h["compounds"]
        )
        user_msg = (
            f"HYPOTHESIS: {h['hypothesis']}\n\n"
            f"COMPOUND DATA:\n{compounds_str}\n\n"
            f"Review this hypothesis critically. Respond with JSON only."
        )

        response = client.messages.create(
            model=args.model,
            max_tokens=512,
            system=REVIEW_SYSTEM,
            messages=[{"role": "user", "content": user_msg}],
        )
        text = "".join(b.text for b in response.content if hasattr(b, "text"))
        total_input += response.usage.input_tokens
        total_output += response.usage.output_tokens

        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            review = json.loads(match.group())
        else:
            review = {"verdict": "parse_error", "raw": text}

        review["hypothesis"] = h["hypothesis"]
        reviews.append(review)

        print(f"Hypothesis {i}: {h['hypothesis'][:80]}...")
        print(f"  Verdict: {review.get('verdict', '?')} | Confidence: {review.get('confidence', '?')}")
        if review.get("evidence_for"):
            print(f"  Evidence for: {review['evidence_for'][0][:80]}...")
        if review.get("evidence_against"):
            print(f"  Evidence against: {review['evidence_against'][0][:80]}...")
        print(f"  Suggestion: {review.get('suggestion', 'N/A')[:80]}")
        print()

    cost = (total_input / 1e6 * 0.80) + (total_output / 1e6 * 4.0)
    report = (
        f"Phase 73 — Peer Review Results\n{'='*50}\n"
        f"Model: {args.model} | Hypotheses reviewed: {len(reviews)}\n\n"
    )
    for r in reviews:
        report += f"Hypothesis: {r['hypothesis'][:100]}...\n"
        report += f"  Verdict: {r.get('verdict')} | Confidence: {r.get('confidence')}\n"
        report += f"  Suggestion: {r.get('suggestion', 'N/A')}\n\n"
    report += f"Tokens: in={total_input} out={total_output}\nCost: ${cost:.4f}\n"
    print(report)

    with open(os.path.join(args.output_dir, "peer_reviews.json"), "w") as f:
        json.dump(reviews, f, indent=2)
    with open(os.path.join(args.output_dir, "peer_review_report.txt"), "w") as f:
        f.write(report)
    print("Done.")


if __name__ == "__main__":
    main()
